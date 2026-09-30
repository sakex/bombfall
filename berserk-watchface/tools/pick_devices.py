#!/usr/bin/env python3
"""Rewrite manifest.xml <iq:products> with the fenix 8 Pro / fenix 9 ids the
SDK actually knows, so new models (e.g. fenix 9 Pro) are picked up without
guessing their device ids.

    connect-iq-sdk-manager device list > devices.txt
    python3 tools/pick_devices.py devices.txt manifest.xml
"""
import re
import sys

WANTED = re.compile(r"^fenix(9|8pro)", re.I)


def main(devices_txt, manifest):
    names = []
    for line in open(devices_txt, encoding="utf-8"):
        parts = line.split()
        if parts and parts[0] != "NAME":
            names.append(parts[0])
    picked = sorted(n for n in names if WANTED.match(n))
    if not picked:
        sys.exit("no fenix 8 Pro / fenix 9 devices found in device list")
    xml = open(manifest, encoding="utf-8").read()
    products = "\n".join(f'            <iq:product id="{n}"/>' for n in picked)
    xml = re.sub(r"(<iq:products>).*?(\s*</iq:products>)",
                 lambda m: m.group(1) + "\n" + products + m.group(2), xml, flags=re.S)
    open(manifest, "w", encoding="utf-8").write(xml)
    print("\n".join(picked))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
