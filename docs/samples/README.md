# Sample notes

One file per sample: `<model>-<version>.md`. Keep it short — provenance, the
scan output, and anything the scanner cannot see (e.g. decryption result).

Template:

````markdown
# D7000 v1.04

- source: <Nikon download URL>
- package: `F-D7000-V104W.exe`
- payload: `D7000Update/D7000_0104.bin`, 19 676 347 bytes
- sha256: `<hash>`

```text
<paste tools/nikon_fw_scan.py output here>
```

Notes:
- decrypted with the Expeed 4/5 tooling: yes / no
- A banner: present / absent, model string `...`
````

Binaries are never committed; see `samples/README.md`.
