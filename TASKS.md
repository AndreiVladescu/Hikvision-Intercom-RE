# Hikvision DS-KV6113-WPE1(C) — RE / Audit Task List

## Phase 1 — Firmware Extraction & Recon (DONE)
- [x] Chip-off flash dump (MX25L25645G, 32MB)
- [x] binwalk3 extraction — identified 2x JFFS2 + CramFS + U-Boot
- [x] CramFS mounted and files catalogued
- [x] Ramdisk (ext2) explored via debugfs
- [x] `hicore` binary (main app) strings analysis
- [x] `psh` binary extracted and analyzed
- [x] `servercert.pem` / `serverkey.pem` decoded

## Phase 2 — Deep Analysis (IN PROGRESS)
- [x] Run EMBA — 4,000 CVEs, 105 exploits, 12 Metasploit; JTR hash crack (failed); STACS key scan
- [x] Root password hash crack attempt (JTR: uncracked after 1 hour)
- [ ] Reverse `dec` binary — find encryption algorithm used on start.sh
- [ ] Analyze `digicapkeyArm.ko` (Ghidra — find embedded key material)
- [ ] Analyze web server files (`webs.tar.gz`, `web4.0_help.tar.gz`) for web vulns
- [ ] Analyze `sipServer` binary
- [ ] Verify CVE-2021-36260 command injection against ISAPI endpoints in hicore
- [ ] Dynamic analysis / emulation with QEMU (ARM)

## Phase 3 — Reporting (IN PROGRESS)
- [x] Initial findings compiled (F-01 through F-11)
- [x] EMBA findings integrated (F-12 through F-15, SBOM CVE counts, CVE table, stats appendix)
- [x] `TEMPLATE.md` created
- [ ] Final review pass on `REPORT.md`
- [ ] Add dynamic analysis findings when available

## Phase 4 — Optional Further Work
- [ ] Live traffic capture (network sniff with device online)
- [ ] UART console access (console=ttyS0,115200 confirmed in U-Boot)
- [ ] Flash modified firmware / test patch mitigations

---

## Known CVEs to Cross-Reference
| CVE | Description |
|-----|-------------|
| CVE-2021-36260 | Hikvision command injection via ISAPI (unauthenticated RCE) |
| CVE-2017-7921 | Hikvision auth bypass (access snapshot without auth) |
| CVE-2017-7923 | Hikvision password disclosure |
| CVE-2014-4878 | Hikvision default credentials |
| CVE-2022-28171 | Hikvision web server injection |
