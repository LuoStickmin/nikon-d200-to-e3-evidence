#!/usr/bin/env python3
"""Scan a Nikon firmware image and report its A/B packaging facts.

Understood input shapes
-----------------------
container
    Expeed-era module container: 0x30-byte header, then a directory of
    ``count x [16B name | BE32 start | BE32 length | 8B tag]``, modules laid
    out contiguously, each module ending in a big-endian CRC-16/CCITT.
    Decrypted containers start at offset 0; some plaintext containers carry a
    0x20-byte wrapper, which is tried as well.

raw image
    D200-style bare flash image ending in big-endian CRC-16/CCITT, optionally
    preceded by an 8-byte ``firmware stamp``.

The 8-byte stamp
----------------
``[BE16 version][1B revision][0x00][BCD yy][BCD mm][BCD dd][BCD hh]``

    D200   02 01 00 00 08 06 09 19   v2.01 r0  2008-06-09 19h
    D750   01 11 00 00 17 02 20 13   v1.11 r0  2017-02-20 13h
    D4S    01 32 01 00 16 12 16 12   v1.32 r1  2016-12-16 12h

A-images repeat the stamp in an in-image banner next to the ASCII string
``Firmware A Copyright Nikon Corp.``; the trailer copy sits at image_size-10.

All checksums are CRC-16/CCITT: poly 0x1021, init 0x0000, no reflection, no
final XOR - i.e. Python's ``binascii.crc_hqx(data, 0)``.

The tool never modifies its input and performs no decryption.

Usage
-----
    python nikon_fw_scan.py FILE [FILE ...] [--label NAME] [--md]
"""
import argparse
import binascii
import re
import struct
import sys

CONTAINER_BASES = (0x00, 0x20)
BANNER_RE = re.compile(rb"([A-Za-z0-9_ .-]{4,12}?)\s{1,8}Firmware A Copyright")


def crc16(data):
    return binascii.crc_hqx(data, 0)


def _bcd(byte):
    hi, lo = byte >> 4, byte & 0x0F
    if hi > 9 or lo > 9:
        return None
    return hi * 10 + lo


def decode_stamp(raw8):
    """Decode the 8-byte stamp, or return None if it is not well formed."""
    if len(raw8) != 8:
        return None
    ver = struct.unpack_from(">H", raw8, 0)[0]
    rev, pad = raw8[2], raw8[3]
    yy, mm, dd, hh = (_bcd(x) for x in raw8[4:8])
    if pad != 0 or None in (yy, mm, dd, hh):
        return None
    if not (1 <= mm <= 12 and 1 <= dd <= 31 and hh <= 23 and ver != 0):
        return None
    return {
        "version": "v%x.%02x" % (ver >> 8, ver & 0xFF),
        "rev": rev,
        "date": "20%02d-%02d-%02d %02dh" % (yy, mm, dd, hh),
    }


def stamp_text(stamp):
    if not stamp:
        return None
    return "%s r%d %s" % (stamp["version"], stamp["rev"], stamp["date"])


def find_stamp_near(blob, pos, window=24):
    """Look for a valid 8-byte stamp ending within `window` bytes before pos."""
    for back in range(8, window + 1):
        start = pos - back
        if start < 0:
            break
        st = decode_stamp(blob[start:start + 8])
        if st:
            return st, start
    return None, None


def isa_hint(blob):
    if len(blob) >= 16:
        w0, w1, w2 = struct.unpack_from(">3I", blob, 0)
        if (w0 >> 26) == 0x0F and (w1 >> 26) == 0x09 and w2 == 0x03400008:
            # lui k0,0xbfc0 ; addiu k0,k0,imm ; jr k0 ; nop
            return "MIPS32 BE (kseg1, entry 0xBFC0%04X)" % (w1 & 0xFFFF)
        if 0x20000000 <= w0 <= 0x200FFFFF and (w1 & 1) and w1 < 0x01000000:
            return "Cortex-M (SP=%08X, reset=%08X)" % (w0, w1)
    head = blob[:0x1000]
    if b"AMCU" in head:
        m = re.search(rb"([A-Z0-9]{3,12}AMCU)", head)
        return "H8S/2600 MCU (id %r)" % (m.group(1).decode() if m else "AMCU")
    if b"REALOS/FR" in blob[:0x200000]:
        return "Fujitsu FR (REALOS/FR)"
    return "unknown"


def banner_info(blob):
    """Return (model, stamp) from the in-image 'Firmware A' banner."""
    m = BANNER_RE.search(blob)
    if not m:
        return None, None
    model = m.group(1).decode("latin1").strip()
    stamp, _ = find_stamp_near(blob, m.start(1))
    return model, stamp


def parse_container(data):
    """Return (base, modules) if data looks like a Nikon module container."""
    for base in CONTAINER_BASES:
        if len(data) < base + 0x30 + 32:
            continue
        count = struct.unpack_from(">I", data, base + 0x20)[0]
        if not 0 < count <= 64:
            continue
        if base + 0x30 + 32 * count > len(data):
            continue
        modules, expect, ok = [], 0x30 + 32 * count, True
        for i in range(count):
            o = base + 0x30 + 32 * i
            name = data[o:o + 16].rstrip(b"\x00")
            start, length = struct.unpack_from(">II", data, o + 16)
            if start != expect or length < 2 or base + start + length > len(data):
                ok = False
                break
            if not name or any(b < 0x20 or b > 0x7E for b in name):
                ok = False
                break
            expect = start + length
            modules.append({
                "name": name.decode("ascii", "replace"),
                "start": start,
                "length": length,
                "tag": data[o + 24:o + 32],
                "blob": data[base + start:base + start + length],
            })
        if ok and modules:
            return base, modules
    return None


def module_facts(mod):
    blob = mod["blob"]
    stored = struct.unpack(">H", blob[-2:])[0]
    model, banner_stamp = banner_info(blob)
    return {
        "name": mod["name"],
        "size": mod["length"],
        "crc_ok": crc16(blob[:-2]) == stored,
        "isa": isa_hint(blob),
        "model": model,
        "banner_stamp": banner_stamp,
        "trailer_stamp": decode_stamp(blob[-10:-2]),
        "tag": mod["tag"].rstrip(b"\x00"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Report Nikon firmware A/B packaging facts.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--label", default="", help="sample label for --md rows")
    ap.add_argument("--md", action="store_true", help="also emit a markdown table")
    args = ap.parse_args(argv)

    rows = []
    for path in args.files:
        with open(path, "rb") as fh:
            data = fh.read()
        label = args.label or path.replace("\\", "/").rsplit("/", 1)[-1]
        parsed = parse_container(data)
        print("== %s  (%d bytes, 0x%x)" % (path, len(data), len(data)))
        if parsed is None:
            print("   shape: raw image (no container directory)")
            mods = [{"name": "(raw image)", "start": 0, "length": len(data),
                     "tag": b"", "blob": data}]
        else:
            base, mods = parsed
            print("   shape: container, body at 0x%02x, %d module(s)" % (base, len(mods)))
        for mod in mods:
            f = module_facts(mod)
            print("   %-18s len=0x%-9x crc=%-3s tag=%-10r" % (
                f["name"], f["size"], "OK" if f["crc_ok"] else "BAD", f["tag"]))
            print("       isa=%s" % f["isa"])
            if f["model"]:
                print("       banner: %-8s %s" % (f["model"], stamp_text(f["banner_stamp"])))
            print("       stamp : %s" % (stamp_text(f["trailer_stamp"]) or "-"))
            rows.append((label, f))

    if args.md:
        print()
        print("| sample | module | size | CRC16 | ISA | Firmware A stamp |")
        print("|---|---|---|---|---|---|")
        for label, f in rows:
            print("| %s | `%s` | 0x%x | %s | %s | %s |" % (
                label, f["name"], f["size"], "OK" if f["crc_ok"] else "BAD",
                f["isa"], stamp_text(f["trailer_stamp"]) or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
