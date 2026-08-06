#!/usr/bin/env python3
"""
Reconstruct audio and video from a passively captured RTSP/RTP session.

The RTSP service on these devices negotiates the RTP/AVP profile -- the
*unencrypted* one. There is no SRTP, no TLS, and no key of any kind involved.
Anyone with access to the network segment can recover the media, which for a
door station means the audio and video of everyone who comes to the door.

This script demonstrates that with nothing but a packet capture:

  * audio -- G.711 mu-law (PCMU, payload type 0) -> playable .wav
  * video -- H.264 (dynamic payload type, usually 96) -> Annex-B .h264

H.264 depacketisation implements RFC 6184: single NAL units, STAP-A
aggregation packets, and FU-A fragmentation.

Usage:
    ./rtp_extract.py capture.pcap                       # auto-detect streams
    ./rtp_extract.py capture.pcap --audio-port 8207 --video-port 8205
    ffplay out.h264            # play the recovered video
    ffplay out.wav             # play the recovered audio

Requires tshark (wireshark-common).
"""

import argparse
import struct
import subprocess
import sys
from collections import defaultdict

# ---------------------------------------------------------------- G.711 mu-law

def _mulaw_table():
    tbl = []
    for byte in range(256):
        u = ~byte & 0xFF
        sign = u & 0x80
        exponent = (u >> 4) & 0x07
        mantissa = u & 0x0F
        value = (((mantissa << 1) | 33) << exponent) - 33
        tbl.append(-value if sign else value)
    return tbl

_MULAW = _mulaw_table()


def write_wav(path, mulaw_bytes, rate=8000):
    pcm = b"".join(
        struct.pack("<h", max(-32768, min(32767, _MULAW[b] * 4))) for b in mulaw_bytes
    )
    hdr = (
        b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16)
        + b"data" + struct.pack("<I", len(pcm))
    )
    with open(path, "wb") as fh:
        fh.write(hdr + pcm)
    return len(pcm) // 2 / rate


# ------------------------------------------------------------ H.264 / RFC 6184

START = b"\x00\x00\x00\x01"


def depacketise_h264(payloads):
    """RTP payloads -> Annex-B byte stream."""
    out = bytearray()
    frag = None
    for p in payloads:
        if not p:
            continue
        nal_type = p[0] & 0x1F

        if 1 <= nal_type <= 23:                       # single NAL unit
            out += START + p

        elif nal_type == 24:                          # STAP-A aggregation
            i = 1
            while i + 2 <= len(p):
                size = struct.unpack(">H", p[i:i + 2])[0]
                i += 2
                if size and i + size <= len(p):
                    out += START + p[i:i + size]
                i += size

        elif nal_type == 28:                          # FU-A fragmentation
            if len(p) < 2:
                continue
            fu_ind, fu_hdr = p[0], p[1]
            start, end = fu_hdr & 0x80, fu_hdr & 0x40
            if start:
                frag = bytearray([(fu_ind & 0xE0) | (fu_hdr & 0x1F)]) + p[2:]
            elif frag is not None:
                frag += p[2:]
            if end and frag is not None:
                out += START + bytes(frag)
                frag = None
    return bytes(out)


# ------------------------------------------------------------------- capture IO

def rtp_by_port(pcap, ports):
    """{srcport: [(payload_type, payload_bytes), ...]} decoded as RTP."""
    decode = []
    for p in ports:
        decode += ["-d", f"udp.port=={p},rtp"]
    cmd = (["tshark", "-r", pcap] + decode
           + ["-Y", "rtp", "-T", "fields", "-e", "udp.srcport",
              "-e", "rtp.p_type", "-e", "rtp.payload"])
    res = subprocess.run(cmd, capture_output=True, text=True)
    streams = defaultdict(list)
    for line in res.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 3 or not parts[2]:
            continue
        try:
            payload = bytes.fromhex(parts[2].replace(":", ""))
        except ValueError:
            continue
        streams[int(parts[0])].append((int(parts[1]), payload))
    return streams


def sniff_ports(pcap):
    """Read the RTSP SETUP responses to learn the server RTP ports."""
    res = subprocess.run(["tshark", "-r", pcap, "-Y", "rtsp", "-T", "fields",
                          "-e", "rtsp.transport"], capture_output=True, text=True)
    ports = set()
    for line in res.stdout.splitlines():
        for tok in line.split(";"):
            if tok.startswith("server_port="):
                rng = tok.split("=", 1)[1]
                ports.add(int(rng.split("-")[0]))
    return sorted(ports)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pcap")
    ap.add_argument("--audio-port", type=int)
    ap.add_argument("--video-port", type=int)
    ap.add_argument("--prefix", default="recovered")
    a = ap.parse_args()

    ports = [p for p in (a.audio_port, a.video_port) if p] or sniff_ports(a.pcap)
    if not ports:
        print("no RTP ports found; pass --audio-port / --video-port", file=sys.stderr)
        return 1
    print(f"RTP ports: {', '.join(map(str, ports))}")

    streams = rtp_by_port(a.pcap, ports)
    if not streams:
        print("no RTP packets decoded", file=sys.stderr)
        return 1

    for port, pkts in sorted(streams.items()):
        ptype = pkts[0][0]
        payloads = [p for _, p in pkts]

        if ptype == 0:                                  # PCMU
            raw = b"".join(payloads)
            out = f"{a.prefix}.wav"
            secs = write_wav(out, raw)
            print(f"  port {port}  PT {ptype:<3} PCMU/8000  "
                  f"{len(pkts):>5} pkts -> {out}  ({secs:.1f}s audio)")

        elif ptype >= 96:                               # dynamic: H.264
            data = depacketise_h264(payloads)
            out = f"{a.prefix}.h264"
            with open(out, "wb") as fh:
                fh.write(data)
            nals = data.count(START)
            print(f"  port {port}  PT {ptype:<3} H264       "
                  f"{len(pkts):>5} pkts -> {out}  ({len(data):,} bytes, {nals} NAL units)")
        else:
            print(f"  port {port}  PT {ptype:<3} (unhandled) {len(pkts)} pkts")

    print("\nplay with:  ffplay " + a.prefix + ".h264   |   ffplay " + a.prefix + ".wav")
    return 0


if __name__ == "__main__":
    sys.exit(main())
