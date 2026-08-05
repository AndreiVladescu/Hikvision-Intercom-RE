# Hikvision DS-KV6113-WPE1(C) — RE / Audit Task List

## Phase 1 — Firmware Extraction & Recon (DONE)
- [x] Chip-off flash dump (MX25L25645G, 32MB)
- [x] binwalk3 extraction — identified 2x JFFS2 + CramFS + U-Boot
- [x] CramFS mounted and files catalogued
- [x] Ramdisk (ext2) explored via debugfs
- [x] `hicore` binary (main app) strings analysis
- [x] `psh` binary extracted and analyzed
- [x] `servercert.pem` / `serverkey.pem` decoded

## Phase 2 — Deep Static Analysis (DONE)
- [x] Run EMBA — 4,000 CVEs, 105 exploits, 12 Metasploit; JTR hash crack (failed); STACS key scan
- [x] Root password hash crack attempt (JTR: uncracked after 1 hour)
- [x] Reverse `dec` binary + `digicapkeyArm.ko` — 3DES-ECB key extracted, `start.sh` fully decrypted (F-06)
- [x] `psh` static disassembly — RSA challenge-response flow, 4 hardcoded keys, command set (F-02)
- [x] `da_info` dispatch table extracted (145 entries) — resetPasswd/resetParam hidden surface (F-16)
- [x] `hicore` ISAPI endpoint mapping (42 endpoints) — CVE-2021-36260 endpoint + version check (F-17); serial passthrough (F-19)
- [x] `sipServer` SQL injection via SIP REGISTER, static confirm (F-18)
- [x] `libbsp_data_encrypt.so` reversed — AES-128-ECB key hierarchy, decryptData oracle (F-21)
- [x] `daemon_fsp_app` CPIU IPC bus reversed — heap OOB write (F-20)
- [x] `daemon_fsp_app` F-20 dynamically confirmed under QEMU (`qemu-arm-static`) — SIGSEGV PoC
- [x] U-Boot environment recovered — `verify=n`, `bootdelay=1`, TFTP factory path (F-22)
- [x] `hicore` secretkey ISAPI bypass mechanism reversed (F-23)
- [x] Hardcoded tokens / fallback key in `hicore` (F-24); no CSRF on web interface (F-25)

**Note:** all of Phase 2 was performed against the single chip-off'd unit only (firmware V2.1.5, Linux 3.18.20). See Phase 5 below — a second, newer physical unit is now being tested live and does not share this exact firmware/bootloader.

## Phase 3 — Reporting (IN PROGRESS)
- [x] Initial findings compiled (F-01 through F-11)
- [x] EMBA findings integrated (F-12 through F-15, SBOM CVE counts, CVE table, stats appendix)
- [x] F-16 through F-25 written up in `REPORT.md`
- [x] `TEMPLATE.md` created
- [x] §2.1 added to `REPORT.md` — chip-off unit vs. live UART unit hardware/firmware comparison, with caveats added to F-02, F-17, F-22
- [ ] Final review pass on `REPORT.md`
- [ ] Add F-01–F-25 rows for F-24/F-25 to the Section 5 findings summary table (currently only goes to F-23)
- [ ] Add live UART dynamic-analysis findings once interactive testing (Phase 5) is complete

## Phase 4 — Optional Further Work
- [ ] Live traffic capture (network sniff with device online)
- [x] UART console access confirmed reachable (console=ttyS0,115200) — see Phase 5 for live testing
- [ ] Flash modified firmware / test patch mitigations

## Phase 5 — Live UART Testing, Second Physical Unit (IN PROGRESS, started 2026-07-04)

Second unit is a **newer hardware/firmware revision** than the chip-off unit (V2.2.65 vs V2.1.5, Linux 4.19.91 vs 3.18.20, OTP-locked secure boot vs `verify=n`, PCB DS-17116, prod. date 2025-03-26). Full comparison in `REPORT.md` §2.1. Treat findings against this unit as a separate data point, not a re-confirmation of the chip-off unit's findings.

- [x] Cold-boot UART capture obtained (`boot_uart_115.2k.txt`, 115200 8N1) — passive, no commands sent
- [x] Confirmed live: console reaches `ash` → `psh` with no login/getty prompt (F-02 live-confirmed at console-access level)
- [x] Confirmed live: secure boot appears enforced on this unit — `[Start Mode]: Secure`, signature verification passed for uImage + ramdisk (F-22 flagged unconfirmed on this revision)
- [x] Confirmed live: firmware V2.2.65 reported — outside CVE-2021-36260 affected range inferred for the chip-off unit (F-17 flagged likely inapplicable)
- [x] Interactive UART session driven via `pyserial` script (port shared with user's minicom caused corruption at first — resolved once minicom was closed)
- [x] `help` on this build lists 4 commands: `getHardInfo`, `help`, `Debug`, `sandbox` — differs from the statically-analyzed build's table
- [x] `getHardInfo` runs with **no** `Debug` auth on this build, dumps serial number + firmware build + hw registers; `tools_process`/`unix_bus` IPC activity observed alongside it (timing correlation only, call path not traced)
- [x] `sandbox` (listed but not a psh built-in) → `/bin/sh: sandbox: not found` — dispatch reaches a real shell for at least this command
- [x] Metacharacter filter tested live and reproduced twice (`getHardInfo;id`, `help;id`) — both blocked with `Not Support Redirect I/O or Combinated Commands.`; only `;` tested, other metachars/encodings untested
- [x] `Debug` challenge decoded: base64 → `08000000` + `eth0` MAC (`a4:d5:c2:4e:71:f3`) + 4 trailing bytes — **identical across 2 invocations** in the same boot session (possible non-fresh nonce; untested across reboot)
- [x] Empty password on `Debug` → `Incorrect Password. 3 Times Left` (starting attempt budget indeterminate — do not assume it differs from the documented 5)
- [x] Signal/EOF escape attempts against `psh` (Ctrl-D/C/\\/Z) — all failed, no parent shell reached (F-02 updated)
- [x] Newline-based metacharacter filter bypass attempt — failed, LF treated as its own line terminator by the tty layer, no smuggling achieved (F-02 updated)
- [x] Offline RSA cryptanalysis of the 4 embedded public keys (chip-off unit's `psh` binary, re-extracted from offset `0xbcd99`) — pairwise GCD (no shared factors), exponent check (e=65537, standard), primality check (composite), Fermat factorization (2M iterations, no factor) — no exploitable key weakness found
- [x] Attempted the F-22 attack path against this unit: interrupting the 1-second `bootdelay` window does **not** reach a generic U-Boot `=>` shell — lands in a vendor upgrade-menu → unauthenticated TFTP recovery flow instead. Ctrl+U (documented elsewhere as an interrupt key on an older Hikvision camera) and a genuine serial BREAK condition both tested as alternate triggers — neither reached a different shell (F-22 updated, flagged as likely specific to the older hardware revision)
- [x] **No unrestricted shell reached on this unit via any UART-based approach tried.** Decision made to chip-off read this unit's flash directly instead of continuing live exploitation — see Phase 6. Items below remain blocked pending that:
  - [ ] Check `/etc/passwd` / `/etc/shadow` for root hash — same shared hash as F-03, or unique per unit? (now via chip-off, not live shell)
  - [ ] Check the `enable_telnet` config flag (F-08) — confirm it gates `sshd`, not Telnet (no telnetd exists in the chip-off image); toggle it and verify port 22 opens / port 23 does not
  - [ ] Attempt `da_info resetPasswd` direct invocation (F-16) on this firmware build
  - [ ] Check whether `/home/config/dev_masterkey` exists (F-23) and whether the secretkey ISAPI bypass endpoints are present in this build's `hicore`
  - [ ] Extract and statically analyze this build's actual `psh` binary (svn358439) — compare against the older build's challenge-response implementation
- [ ] Test `/ISAPI/System/configurationData` directly over network for CVE-2021-36260 (F-17) rather than relying on version-string inference, once device has network access
- [x] Update `REPORT.md` with confirmed/refuted status for each item above

## Phase 6 — Chip-Off Read, Second Physical Unit (NOT STARTED, decided 2026-07-04)

Mirrors Phase 1's methodology, applied to the live/newer unit, since all UART-based bypass attempts (Phase 5) were exhausted without reaching a shell. This should resolve most of Phase 5's blocked items via clean offline analysis instead of live exploitation.

- [ ] Identify the flash IC package/pinout on this unit's PCB (may differ from the MX25L25645G on the chip-off unit, given the different SoC platform — confirm chip markings first)
- [ ] Attempt in-circuit read via SOIC clip if package/pinout allows; desolder only if necessary
- [ ] Dump full flash image, run through `binwalk3` to identify partitions (expect a different layout given the NVT/Novatek boot stack vs. the original's HiSilicon layout)
- [ ] Extract and analyze this unit's actual `psh` binary (svn358439), `/etc/shadow`, `/home/config/dev_masterkey`, telnet config, `da_info` table, and any TFTP-recovery-related upgrade tooling found in the image
- [ ] Compare directly against the chip-off unit's findings (F-01–F-25) and the live UART observations (§2.1, Phase 5) — note agreements/divergences in `REPORT.md`
- [ ] Determine whether the TFTP recovery flow discovered in Phase 5 validates image signatures before writing to flash, by examining the recovery/upgrade binary statically (safer than testing it live)

---

## Known CVEs to Cross-Reference
| CVE | Description |
|-----|-------------|
| CVE-2021-36260 | Hikvision command injection via ISAPI (unauthenticated RCE) |
| CVE-2017-7921 | Hikvision auth bypass (access snapshot without auth) |
| CVE-2017-7923 | Hikvision password disclosure |
| CVE-2014-4878 | Hikvision default credentials |
| CVE-2022-28171 | Hikvision web server injection |
