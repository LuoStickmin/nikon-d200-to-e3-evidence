# Packaging evidence

All numbers below were produced by `tools/nikon_fw_scan.py` on the samples
listed at the end of this file. Nothing here is inferred from the firmware
*behaviour*; every claim is a byte-level observation.

## 1. Two images, two names

Nikon's own terminology is visible inside the A image, right next to the
version stamp:

```
D750   Firmware A Copyright Nikon Corp.
D5300  Firmware A Copyright Nikon Corp.
D4S    Firmware A Copyright Nikon Corp.
```

The B image carries no such banner, but the D200-era updater (inside the B
image) refers to the pair as `A` and `B` in its own descriptor, and looks for
files named `A200????.BIN` / `B200????.BIN` on the CF card. The D200 A image
predates the banner wording and identifies itself as `D200AMCU` instead.

## 2. The 8-byte firmware stamp

```
offset 0   BE16  version          e.g. 0x0201 = v2.01
offset 2   1B    revision         e.g. 0x00, 0x03
offset 3   1B    0x00
offset 4   1B    BCD year         e.g. 0x08 -> 2008, 0x17 -> 2017
offset 5   1B    BCD month
offset 6   1B    BCD day
offset 7   1B    BCD hour
```

Observed:

| image | stamp | decoded |
|---|---|---|
| D200 `A2000201.bin` (0x3FFF8 and 0x200) | `02 01 00 00 08 06 09 19` | v2.01 r0 2008-06-09 19h |
| D5300 `a930_010103.bin` | `01 01 03 00 15 10 16 10` | v1.01 r3 2015-10-16 10h |
| D4S `a1140_013201.bin` | `01 32 01 00 16 12 16 12` | v1.32 r1 2016-12-16 12h |
| D750 `a1010_011100.bin` | `01 11 00 00 17 02 20 13` | v1.11 r0 2017-02-20 13h |
| D850 `a1330_010303.bin` | `01 03 03 00 20 08 17 18` | v1.03 r3 2020-08-17 18h |

Notes:

* The stamp occurs **twice** in every A image: once in the banner block
  (immediately before the model name) and once at `image_size - 10`.
  D5/D850 A images (1 MiB, trailer padded with `FF`) only keep the banner copy.
* The version in the stamp is the **A-image** version, which is independent of
  the package version. E.g. D750 v1.15 ships A v1.11, built 2017-02-20.
* The date is a *build* date, not a release date; later package releases can
  carry an A image rebuilt years earlier or later.

## 3. CRC-16/CCITT everywhere

```
poly 0x1021, init 0x0000, no reflection, no final XOR
= binascii.crc_hqx(data, 0)
stored big-endian
```

* A image: CRC over `[0, image_size)`, stored at `image_size` — so the file is
  `image_size + 2` bytes (`0x40000+2` for D200, `0xC0000+2` / `0x100000+2` for
  Expeed 4/5).
* B image: CRC over `[0, size-2)`, stored in the last 2 bytes (D200 B is
  `0x3C0000` total; the Expeed B modules are `image + 2`).
* Module container: each directory entry's module ends in the same BE16 CRC,
  and the container adds a package CRC over the body minus its 16-byte trailer.

D200 v2.01 concrete values: `crc_hqx(A[0:0x40000], 0) = 0xEF19` (stored at
0x40000), `crc_hqx(B[0:0x3BFFFE], 0) = 0xE25F` (stored at 0x3BFFFE).

## 4. Container layout (Expeed era)

```
0x00  32B  spaces ("                                ") in every body seen so far
0x20  BE32 module_count
0x24  BE32 directory_size = 0x30 + 32 * count
0x30  entries: 16B name | BE32 start | BE32 length | 8B tag
      modules follow, contiguous, each ending in BE16 CRC-16/CCITT
```

Original update files prepend a 0x20-byte wrapper to this body (its first 20
bytes are a SHA-1 in the encrypted generations). Decrypted dumps start at body
offset 0, while some plaintext dumps (`D5600`, `D5`, `D850`) keep the wrapper,
so the body starts at 0x20 — the scanner tries both bases.

The A module is named `a<model-code>_<ver><rev>` (`a1010_011100.bin` =
D750, v1.11, rev 00); the B module is `b<model-code>_<ver><rev>`
(`b1010_115a.bin` = D750, v1.15, rev a). D200's filenames encode the same
idea without the separator: `A2000201.bin` = A, model 200, v2.01.

Extra modules seen: `_wma_verXX.XX.XX` (wireless module, tag sometimes
`crc.bin`), `_wt5xxx_` (WT-5 wireless transmitter), `_tpcy_` / `_tpj00_`
(small MCU-side blobs).

## 5. A-image CPU families

| family | first bytes | images |
|---|---|---|
| H8S/2600 (Hitachi) | 4-byte BE vector table at 0x0000; `AMCU` id | D200 A |
| MIPS32 big-endian | `lui k0,0xBFC0; addiu k0,k0,0x500; jr k0; nop` → entry 0xBFC00500 | D5300, D4S, D810, D810A A |
| Cortex-M0 | SP in 0x20000000.., reset 0x0000C20D (odd = Thumb) | D750, D7200, D5500, D5600, D5, D850 A |
| Fujitsu FR | `REALOS/FR`, Softune strings | D200 B |

The A-image ISA changed with the platform Nikon chose for each body, not
strictly with the year: MIPS and Cortex-M A images coexist in 2014–2015.

## 6. D200 (2008) side details

* Official package `F-D200-V201W.exe` is a WinRAR SFX containing exactly
  `D200Update\A2000201.bin` and `D200Update\B2000201.bin` — no keys, no tools.
* A header at 0x200: stamp + `D200AMCU` + `0x080D`; tail: stamp + CRC.
* B image is the whole camera application: PTP/USB stack, FAT/CF driver,
  menus, 32 JPEGs at 0x36C298–0x3A545E.
* B image contains the CF update path: filename templates
  `A200????.BIN` / `B200????.BIN` / `_WT3????.BIN`, a FAT16 boot-sector
  template (OEM `NIKON5.0`, MS-DOS boot code), and a descriptor tagged
  `Q220FirmwareSignature` (Q220 = D200 project code) with version string
  `Ver.2.01  D200 2008/08/18 for mass production`.
* No SHA-1/MD5/AES constants were found in either image: in 2008 the "signature"
  is model/version matching plus CRC-16 integrity.
* The same conventions are reported for Expeed 2 images in 2011 — embedded
  JPEGs, SD card as `A:\`, A/B split, XMODEM-style CRC-16 (see
  [references.md](references.md)). The D200 is not an isolated oddity; the
  packaging lineage continues across the gap.

## 7. Per-sample scan output

| sample | module | size | CRC16 | ISA | stamp |
|---|---|---|---|---|---|
| D200 v2.01 | `A2000201.bin` (raw) | 0x40002 | OK | H8S/2600 (D200AMCU) | v2.01 r0 2008-06-09 19h |
| D200 v2.01 | `B2000201.bin` (raw) | 0x3C0000 | OK | Fujitsu FR | - |
| D5300 v1.03 | `a930_010103.bin` | 0x100002 | OK | MIPS32 BE | v1.01 r3 2015-10-16 10h |
| D5300 v1.03 | `b930_103.bin` | 0x15BF4A2 | OK | unknown | - |
| D4S v1.33 | `a1140_013201.bin` | 0x100002 | OK | MIPS32 BE | v1.32 r1 2016-12-16 12h |
| D4S v1.33 | `_wt5103_.bin` | 0x113C72F | OK | unknown | - |
| D4S v1.33 | `b1140_133f.bin` | 0x103AC62 | OK | unknown | - |
| D810 v1.14 | `a920_011300.bin` | 0x100002 | OK | MIPS32 BE | v1.13 r0 2017-02-15 10h |
| D810 v1.14 | `b920_114.bin` | 0x123E7E2 | OK | unknown | - |
| D810A v1.03 | `a1410_010300.bin` | 0x100002 | OK | MIPS32 BE | v1.03 r0 2017-02-15 11h |
| D810A v1.03 | `b1410_102b.bin` | 0x1186462 | OK | unknown | - |
| D750 v1.15 | `a1010_011100.bin` | 0xC0002 | OK | Cortex-M0 | v1.11 r0 2017-02-20 13h |
| D750 v1.15 | `_wma_ver01.00.00` | 0x6BB37 | OK | unknown | - |
| D750 v1.15 | `b1010_115a.bin` | 0x1362062 | OK | unknown | - |
| D7200 v1.04 | `a1230_010300.bin` | 0xC0002 | OK | Cortex-M0 | v1.03 r0 2017-02-15 11h |
| D7200 v1.04 | `_wma_ver01.00.00` | 0x6BB37 | OK | unknown | - |
| D7200 v1.04 | `b1230_104.bin` | 0x11980E2 | OK | unknown | - |
| D5500 v1.02 | `a1120_010200.bin` | 0xC0002 | OK | Cortex-M0 | v1.02 r0 2017-03-24 11h |
| D5500 v1.02 | `_wma_ver01.00.00` | 0x6BB37 | OK | unknown | - |
| D5500 v1.02 | `b1120_102.bin` | 0x142D062 | OK | unknown | - |
| D5600 v1.20 | `a1530_010001.bin` | 0xC0002 | OK | Cortex-M0 | v1.00 r1 2016-10-05 13h |
| D5600 v1.20 | `_wma_ver01.11.00` | 0xD792B | OK | unknown | - |
| D5600 v1.20 | `b1530_120.bin` | 0x1478C22 | OK | unknown | - |
| D5 v1.50 | `a870_013000.bin` | 0x100002 | OK | Cortex-M0 | v1.30 r0 2022-04-12 10h |
| D5 v1.50 | `_wt5160_.bin` | 0x1617A70 | OK | unknown | - |
| D5 v1.50 | `_tpcy_0009.bin` | 0xEA64 | OK | unknown | - |
| D5 v1.50 | `b870_150.bin` | 0x16CB5D6 | OK | unknown | - |
| D850 v1.31 | `a1330_010303.bin` | 0x100002 | OK | Cortex-M0 | v1.03 r3 2020-08-17 18h |
| D850 v1.31 | `_wma_ver01.11.00` | 0xD792B | OK | unknown | - |
| D850 v1.31 | `_tpj00_0150.bin` | 0xE002 | OK | unknown | - |
| D850 v1.31 | `b1330_131.bin` | 0x187B6F6 | OK | unknown | - |

Samples were official Nikon update packages (`.exe`), extracted, and — for
encrypted containers — decrypted before scanning. The binaries themselves are
not part of this repo (see `samples/README.md`).
