# Hikvision-Intercom-RE

Firmware reverse engineering and security analysis of the **Hikvision DS-KV6113-WPE1(C)** IP video door station.

📄 **[Read the writeup →](https://andreivladescu.github.io/Hikvision-Intercom-RE/)**

## What this is

A 32 MB SPI NOR flash image was chip-off read from a physical unit (Macronix MX25L25645G) and analysed statically — binwalk extraction, manual reversing of `hicore`, `psh`, `dec`, `sipServer`, and `daemon_fsp_app`, plus a full EMBA automated run. A second, newer unit was later wired for live UART testing.

25 findings are summarised on the [project page](https://andreivladescu.github.io/Hikvision-Intercom-RE/), covering a vendor-controlled backdoor shell, hardcoded cryptographic material, cloud telemetry endpoints, and an end-of-life software stack.

## Scope of the evidence — please read

**This is primarily a static-analysis project.** With the exceptions below, no finding has been exploited end-to-end against a working device:

| Finding | Status |
|---|---|
| F-06 — encrypted boot script | **Demonstrated** — 3DES key recovered, `start.sh` fully decrypted |
| F-20 — CPIU IPC bus | **Partial** — reproducible SIGSEGV under `qemu-arm-static`; no execution control shown |
| F-02 — `psh` backdoor shell | **Live-confirmed** on both units at console-access level (no login prompt); `Debug` unlock not achieved |
| Everything else | Artifact confirmed present in the image; **exploitability not tested** |

The findings establish that vulnerable code, keys, and endpoints exist *in the firmware image*. They do not establish that any of them is remotely reachable and weaponisable on a deployed unit. CVSS scores are worst-case-if-confirmed and should be read as upper bounds on hypotheses, not measurements.

Live testing on the second unit has already **refuted** one finding (F-22, secure boot bypass — that unit is OTP-locked and signature verification passes) and cast doubt on another (F-17, inferred from a version string the newer firmware falls outside of). Section 5 of the report marks the evidence class and test status of every finding individually; Section 2.1 compares the two units.

Corrections are welcome — particularly from anyone able to test a finding against hardware.

## Repository layout

| Path | Contents |
|---|---|
| *(withheld)* | The full technical report is retained privately — see Disclosure posture |
| `index.md`, `js/`, `img/` | GitHub Pages site — writeup and PCB photo gallery |
| `TASKS.md` | Working task list and project phases |
| `TEMPLATE.md` | Generic report scaffold, reusable for other devices |
| `decrypted_start.sh` | The 3DES-decrypted boot script (F-06) |
| `boot_uart_115.2k.txt` | Cold-boot UART capture from the second unit, 115200 8N1 |
| `extractions/`, `emba_logs/` | Binwalk output and full EMBA run — gitignored, not published |

`firmware.bin` and the extracted filesystems are not redistributed.

## Legal

Security research and responsible disclosure. All testing was performed on hardware owned by the researcher. No third-party device was accessed.
