# Prior work and sources

The byte-level claims in this repo come from our own scans
(`tools/nikon_fw_scan.py` on specific files). The work below is cited for
context, scope, and for pointers to what to test — not as proof of a byte-level
claim.

## Community reverse engineering, Expeed 2 era (2011)

* **Simeon Pilgrim, "Nikon Firmware Insights #04"** (2011-11-25) —
  <https://simeonpilgrim.com/blog/2011/11/25/nikon-firmware-insights-04/>
  Reports finding the checksums for the **D7000 A & B firmware**, and a normal
  XMODEM-style CRC-16 (`poly 0x1021`, start `0x0000`) for the D7000, D300S,
  D3S, D3100 and D5100 **A** images; the **D5100 B** image needed start
  `0x4ED4` instead. The post and its comments also make clear the workflow
  at the time was *decrypt → split into A + B → patch → set checksums →
  encrypt*.
* **Simeon Pilgrim, "Nikon Firmware Insights #05"** (2011-12-06) —
  <https://simeonpilgrim.com/blog/2011/12/06/nikon-firmware-insights-05/>
  D5100 image layout: fonts, overlay images, embedded JPEGs (a D7000 image was
  reported to carry 21 embedded JPEGs), and the SD card exposed as `A:\` — the
  same convention seen in the D200 B image (2008).
* **Nikon Hacker wiki, "Patching Help"** (archived) —
  <https://web.archive.org/web/20230323004548/https://nikonhacker.com/wiki/Patching_Help>
  Community patch workflow and the **Online Patch Tool**
  (<https://simeonpilgrim.com/nikon-patch/nikon-patch.html>).
* **Vitaliy Kiselev's NTool** — repacking and CRC recalculation for these
  images (referenced in the #04 comment thread; not redistributed here).

## D200 era

* **engineeror/NikonD200RE** — <https://github.com/engineeror/NikonD200RE>
  Attempts at modifying the D200 firmware; background for the pre-container
  layout.

## Official

* **Nikon download center** — <https://downloadcenter.nikonimglib.com/>
  Source of the update packages listed in `samples/README.md`.

## How citations are used here

| claim type | source |
|---|---|
| module names, sizes, CRCs, stamps, banners | our scan output only |
| "A/B split also existed in 2011", "CRC-16 poly 0x1021", "images were encrypted" | community reports above |
| download locations | Nikon official site |

Caveats: the community reports are third-party and were not byte-verified for
this repo. Some of their details remain unexplained — notably the `0x4ED4`
start value for the D5100 B image (possibly a different CRC range or a stored
length field), and their `.bin` may or may not already use the 0x30-byte module
directory seen from Expeed 4 onward. Those points are exactly what the samples
in `docs/e3-gap.md` are meant to settle.
