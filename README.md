# Evidence: Nikon "Firmware A / Firmware B" from D200 to Expeed 3

Nikon ships most DSLRs with **two separately versioned firmware images**: an
**A** image (the camera-control MCU) and a **B** image (the main application).
This repo collects the *packaging* evidence for when that split started, how
the images are wrapped, and where the current module container came from.

Verified anchors in this repo:

* **2008** — D200 v2.01: bare flash images, no container, no encryption.
  A = 256 KiB H8S/2600 MCU image; B = 3.75 MiB Fujitsu FR image. Both end in a
  big-endian CRC-16/CCITT. A also carries an 8-byte **firmware stamp**
  (version + revision + BCD build date).
* **2013→2017** — Expeed 4/5 module containers: the A module is literally
  titled `Firmware A Copyright Nikon Corp.` inside the image, carries the
  *same* 8-byte stamp (banner copy + trailer copy) and the *same*
  CRC-16/CCITT. The B module is a bare image + CRC, exactly like D200's B.

The middle — **Expeed 1/2/3 bodies (≈2008–2013: D3/D300/D90/D3s/D7000/D5100/
D3200/D4/D800/D600/D5200/D7100 …)** — is the gap this repo is meant to close.
No E3-era sample is included yet; see [docs/e3-gap.md](docs/e3-gap.md) for the
exact checklist.

## What the evidence shows

| generation | camera | firmware | A module | A size | A ISA | A stamp (banner) | B module | B size |
|---|---|---|---|---|---|---|---|---|
| pre-Expeed | D200 | 2.01 | `A2000201.bin` (raw) | 0x40002 | H8S/2600 MCU | v2.01 r0 2008-06-09 19h | `B2000201.bin` | 0x3C0000 |
| Expeed 4 | D5300 | 1.03 | `a930_010103.bin` | 0x100002 | MIPS32 BE | v1.01 r3 2015-10-16 10h | `b930_103.bin` | 0x15BF4A2 |
| Expeed 4 | D4S | 1.33 | `a1140_013201.bin` | 0x100002 | MIPS32 BE | v1.32 r1 2016-12-16 12h | `b1140_133f.bin` | 0x103AC62 |
| Expeed 4 | D810 | 1.14 | `a920_011300.bin` | 0x100002 | MIPS32 BE | v1.13 r0 2017-02-15 10h | `b920_114.bin` | 0x123E7E2 |
| Expeed 4 | D810A | 1.03 | `a1410_010300.bin` | 0x100002 | MIPS32 BE | v1.03 r0 2017-02-15 11h | `b1410_102b.bin` | 0x1186462 |
| Expeed 4 | D750 | 1.15 | `a1010_011100.bin` | 0xC0002 | Cortex-M0 | v1.11 r0 2017-02-20 13h | `b1010_115a.bin` | 0x1362062 |
| Expeed 4 | D7200 | 1.04 | `a1230_010300.bin` | 0xC0002 | Cortex-M0 | v1.03 r0 2017-02-15 11h | `b1230_104.bin` | 0x11980E2 |
| Expeed 4 | D5500 | 1.02 | `a1120_010200.bin` | 0xC0002 | Cortex-M0 | v1.02 r0 2017-03-24 11h | `b1120_102.bin` | 0x142D062 |
| Expeed 5 | D5 | 1.50 | `a870_013000.bin` | 0x100002 | Cortex-M0 | v1.30 r0 2022-04-12 10h | `b870_150.bin` | 0x16CB5D6 |
| Expeed 5 | D850 | 1.31 | `a1330_010303.bin` | 0x100002 | Cortex-M0 | v1.03 r3 2020-08-17 18h | `b1330_131.bin` | 0x187B6F6 |

Every module CRC-16 verified. Full per-sample output, the container layout,
the stamp layout and the D200-era update mechanism are in
[docs/evidence.md](docs/evidence.md).

## Reproduce

```bash
pip install --upgrade pip   # nothing else: stdlib only
python tools/nikon_fw_scan.py path/to/A2000201.bin path/to/B2000201.bin
python tools/nikon_fw_scan.py path/to/D750_0115.dec --md
```

Point it at a **raw** Nikon update file, a **decrypted** container (`.dec`), or
a **plaintext** container (`D5__0150.bin`). It prints module names, sizes,
CRC status, the CPU-family signature, the in-image banner and both stamp
copies. It never writes to the input and performs no decryption.

## Scope and rules

* **No firmware binaries here.** Nikon firmware is copyrighted; the repo holds
  only scripts, tables and short quoted strings needed as evidence.
* **No decryption keys.** Containers must be decrypted before scanning.
* Not affiliated with Nikon. Nothing here establishes that a modified image is
  accepted by a camera; CRC-16 is integrity, not authenticity.
* Evidence entries are expected to be *reproducible*: every claim maps to a
  `nikon_fw_scan.py` output line.

## Layout

```
README.md               this file
README.zh-CN.md         中文摘要
docs/evidence.md        packaging spec + full evidence table + D200 details
docs/e3-gap.md          what is missing for Expeed 1/2/3, and how to check it
tools/nikon_fw_scan.py  the scanner
samples/README.md       where official firmware comes from; do not commit it
```
