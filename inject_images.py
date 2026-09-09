#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert `img:'...'` fields into the N[] marker array of the map HTML,
based on image_map.json produced by fetch_images.py."""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, 'qinghai-gansu-route-map.html')
MAP = json.load(open(os.path.join(BASE, 'image_map.json')))

src = open(HTML, encoding='utf-8').read()

# only touch lines inside the const N = [...] block
start = src.index('const N = [')
end = src.index('\n];', start)
block = src[start:end]

changed = 0
missing = []


def fix(m):
    global changed
    head, name, tail = m.group(1), m.group(2), m.group(3)
    if 'img:' in m.group(0):
        return m.group(0)
    info = MAP.get(name)
    if not info:
        missing.append(name)
        return m.group(0)
    changed += 1
    # tail ends with the d:'...' value; pattern consumed the trailing " },".
    # Keep the object closed and comma-separated, otherwise the JS breaks.
    return "%sn:'%s'%s, img:'%s' }," % (head, name, tail, info['file'])


pat = re.compile(r"(\{ k:'\w+', )n:'([^']+)'(, p:\[[^\]]+\], t:'[^']*'(?:, d:'[^']*')?) \},")
new_block = pat.sub(fix, block)

src = src[:start] + new_block + src[end:]
open(HTML, 'w', encoding='utf-8').write(src)
print('injected:', changed)
print('no image for:', missing)
