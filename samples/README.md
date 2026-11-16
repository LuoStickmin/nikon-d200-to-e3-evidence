# Samples

This repository does **not** contain Nikon firmware. Binaries are copyrighted
by Nikon and are not redistributed here.

## Where the samples come from

Official firmware is published by Nikon on its regional support sites, e.g.
`https://downloadcenter.nikonimglib.com/` (search the body model, download the
Windows updater `F-<MODEL>-V<version>W.exe`).

- Expeed-era packages are self-extracting archives (WinRAR/InstallShield).
  Extracting them yields `<MODEL>Update\<MODEL>_<version>.bin`.
- The D200 package `F-D200-V201W.exe` is a WinRAR SFX and yields two files:
  `D200Update\A2000201.bin` (A) and `D200Update\B2000201.bin` (B).
- Expeed 4/5 payloads are encrypted containers; decrypt them with the tooling
  of your choice (this repo does not ship keys or decryption code) and scan
  the decrypted image.

## Rules

* Never commit `.bin`, `.exe`, `.dec` files or extracted module directories —
  `.gitignore` covers them.
* Evidence entries should quote only the bytes needed (headers, stamps,
  short ASCII strings), never whole images.
* If you cannot publish an image or its hash, publish the scan output and say
  so in the sample note.
