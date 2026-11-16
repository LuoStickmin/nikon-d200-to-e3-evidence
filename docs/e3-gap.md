# The gap: Expeed 1/2/3 (≈2008–2013)

Verified anchors sit at 2008 (D200) and 2013 (D5300). Everything in between is
unverified, and that interval is where the current packaging was introduced:

* the module **container** (0x30 header + directory + per-module CRC16),
* the body **encryption** (the T1/T2/T3 keystream used by Expeed 4/5),
* the `a<model>_<ver>` **module naming**,
* the `Firmware A Copyright Nikon Corp.` banner.

D200 has none of those; D5300 has all of them. The 2008–2013 samples decide
which generation introduced what.

## Candidate bodies

Ordered roughly by generation; any one sample per generation is already useful.

| generation | body | expected update layout |
|---|---|---|
| Expeed 1 (2007–2008) | D3, D300, D700, D90, D3X | single `.bin` (probably still raw, like D200) |
| Expeed 2 (2009–2011) | D3s, D300s, D5000, D3000, D7000, D3100, D5100 | single `.bin` |
| Expeed 3 (2012–2013) | D4, D800/D800E, D600, D3200, D5200, D7100, D3300 | single `.bin`, container + encryption likely |

Nikon's own naming for the download is `F-<MODEL>-V<version>W.exe`
(Windows SFX); the payload inside is `<MODEL>Update\<MODEL>_<version>.bin`.
The D200-era packages are the exception: two files, `A2000201.bin` and
`B2000201.bin`.

## Checklist per sample

Record all of the following in `docs/samples/<model>-<version>.md`:

1. **Provenance** — Nikon download URL, package filename, payload filename,
   size, `sha256`.
2. **Container?** — hex dump of the first 0x40 bytes; module count at 0x20,
   directory entries. If none: "no container".
3. **A/B split** — module names, sizes, tags. Expect `a<code>_<ver>` and
   `b<code>_<ver>`, or `A<code><ver>.bin` / `B<code><ver>.bin` for the old
   layout.
4. **CRC-16/CCITT** — per module and per package: pass/fail.
   `binascii.crc_hqx(payload, 0)`, stored big-endian.
5. **A stamp** — decode banner + trailer stamps. If neither decodes, dump the
   last 16 bytes of the A image and the bytes before `Firmware A Copyright`.
6. **Banner** — is `Firmware A Copyright Nikon Corp.` present? At which
   offset? What model string precedes it?
7. **A ISA** — first 16 bytes: `lui k0,0xBFC0` (MIPS), SP+Thumb reset
   (Cortex-M), 4-byte BE vector table / `AMCU` (H8S), `REALOS/FR` (FR).
8. **Encryption** — can the payload be decrypted with the Expeed 4/5 tooling?
   If it fails, say so and record the first 32 bytes of the wrapper.

`tools/nikon_fw_scan.py` covers items 2–7 for raw images and containers; item 8
is external.

## What would settle the history

* **One Expeed 1 sample (D3 or D300)**: does it already have a container? If
  not, the container arrived later than 2007. Does the A image still look like
  D200's (H8S, `AMCU` id, no banner)?
* **One Expeed 2 sample (D7000 or D5100)**: is the container there yet? Is the
  body encrypted (T1/T2/T3) or still plaintext, as D200 is?
* **One Expeed 3 sample (D4, D800 or D7100)**: confirm container + encryption
  are already in place a full generation before Expeed 4, and that the A
  image already uses the MIPS or Cortex-M layouts seen in 2013–2014.

## Contributing

Open a PR adding `docs/samples/<model>-<version>.md`, or a row to
`docs/evidence.md`'s table, with the `nikon_fw_scan.py` output pasted in a
fenced block. **Do not attach firmware binaries** — see `samples/README.md`.
