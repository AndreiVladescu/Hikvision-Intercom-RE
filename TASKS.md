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
- [ ] Extract JFFS2 backup partition (0xA02E0, needs `jefferson`)
- [ ] Reverse `dec` binary — find encryption algorithm used on start.sh
- [ ] Analyze `digicapkeyArm.ko` (modinfo + strings + Ghidra)
- [ ] Attempt root password hash crack (`hashcat -m 1400` unsalted SHA-256)
- [ ] Analyze web server files (`webs.tar.gz`, `web4.0_help.tar.gz`) for web vulns
- [ ] Analyze `base.tar.lzma` and `lib.tar.lzma`
- [ ] Analyze `sipServer` binary
- [ ] Dynamic analysis / emulation with QEMU (ARM)
- [ ] Run EMBA for automated CVE correlation (user offered)

## Phase 3 — Reporting (IN PROGRESS)
- [x] Initial findings compiled
- [ ] Cross-reference all findings with NVD / CVE database
- [ ] Complete `REPORT.md` — full professional report
- [ ] Review and finalize `TEMPLATE.md`

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
