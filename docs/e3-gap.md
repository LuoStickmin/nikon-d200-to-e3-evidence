# The gap: Expeed 1/2/3 (≈2008–2013)

Verified anchors in this repo sit at **2008** (D200 v2.01) and **2013**
(D5300 v1.03). Community reports from 2011 already document the A/B split, the
CCITT CRC-16 and a decrypt/encrypt step for D7000, D5100, D3100, D300S and D3S
(see [references.md](references.md)) — so **Expeed 2 is "already modern" in
outline**. Two things remain genuinely unverified:

1. whether those 2009–2011 payloads already use the 0x30-byte **module
   directory** (the container) seen from Expeed 4 onward;
2. what **Expeed 1** (2007–2008: D3, D300, D700, D90, D3X) looks like — still
   raw like the D200, already containerised, or already encrypted.

## What the community established in 2011 (cited, not re-verified here)

* Workflow: *decrypt → split into A + B → patch → set checksums → encrypt*.
  The A/B pair and the re-encryption step are both documented for
  D7000 / D5100 / D3100 / D300S / D3S.
* Checksum: normal XMODEM-style CRC-16, polynomial `0x1021`, start `0x0000`
  for the listed A images (and most B images). The D5100 **B** image needed a
  start value of `0x4ED4`, which is still unexplained.
* Content: the payloads carry embedded JPEGs, fonts and overlay bitmaps, and
  reach the SD card as `A:\` — the same conventions visible in the D200 B
  image from 2008.

Consequences for this repo: checklist items 4–6 below (CRC, stamp, banner) are
*expected to already hold* for Expeed 2 samples; the container directory
(item 2) and the `Firmware A` banner (item 6) are the open questions.

## Candidate bodies

| generation | body | expected update layout |
|---|---|---|
| Expeed 1 (2007–2008) | D3, D300, D700, D90, D3X | single `.bin`; raw like D200 or already containerised — this is the key unknown |
| Expeed 2 (2009–2011) | D3s, D300s, D5000, D3000, D7000, D3100, D5100 | single `.bin`; A/B + CRC-16 + encryption documented; container unknown |
| Expeed 3 (2012–2013) | D4, D800/D800E, D600, D3200, D5200, D7100, D3300 | single `.bin`; container + encryption expected |

Nikon's download naming is `F-<MODEL>-V<version>W.exe` (Windows SFX); the
payload inside is `<MODEL>Update\<MODEL>_<version>.bin`. The D200-era packages
are the exception: two files, `A2000201.bin` and `B2000201.bin`.

## Checklist per sample

Record all of the following in `docs/samples/<model>-<version>.md`:

1. **Provenance** — Nikon download URL, package filename, payload filename,
   size, `sha256`.
2. **Container?** — hex dump of the first 0x40 bytes; module count at 0x20,
   directory entries, directory size. This is the most important unknown.
3. **A/B split** — module names, sizes, tags. Expect `a<code>_<ver>` and
   `b<code>_<ver>`, or `A<code><ver>.bin` / `B<code><ver>.bin` for the old
   layout.
4. **CRC-16/CCITT** — per module and per package: pass/fail, plus the start
   value that makes it pass. `binascii.crc_hqx(payload, 0)` for the modern
   layout; try non-zero starts for a raw B image.
5. **A stamp** — decode banner + trailer stamps. If neither decodes, dump the
   last 16 bytes of the A image and the bytes before `Firmware A Copyright`.
6. **Banner** — is `Firmware A Copyright Nikon Corp.` present? At which
   offset? What model string precedes it? If absent, dump the bytes around
   any `AMCU` id.
7. **A ISA** — first 16 bytes: `lui k0,0xBFC0` (MIPS), SP+Thumb reset
   (Cortex-M), 4-byte BE vector table / `AMCU` (H8S), `REALOS/FR` (FR).
8. **Encryption** — can the payload be decrypted with Expeed 4/5 tooling? If
   it fails, say so and record the first 32 bytes of the wrapper.

`tools/nikon_fw_scan.py` covers items 2–7 for raw images and containers; item 8
is external.

## What would settle the history

* **One Expeed 1 sample (D3 or D300)**: does the payload have a container
  directory at all? If yes, the container predates 2008 and the D200 is the
  outlier; if no, the container arrived between D200 (2008) and D300S (2009).
  Does the A image still look like D200's (H8S, `AMCU` id, no banner)?
* **One Expeed 2 sample (D7000 or D5100)**: the 2011 reports already show
  decrypt/encrypt and CRC-16; the scan would confirm whether the 0x30 module
  directory and the `Firmware A` banner were already there in 2011.
* **One Expeed 3 sample (D4, D800 or D7100)**: confirm MIPS-vs-Cortex-M A
  images and the container were in place a full generation before Expeed 4.

## Contributing

Open a PR adding `docs/samples/<model>-<version>.md`, or a row to
`docs/evidence.md`'s table, with the `nikon_fw_scan.py` output pasted in a
fenced block. **Do not attach firmware binaries** — see `samples/README.md`.
