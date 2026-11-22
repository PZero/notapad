"""Estrazione minimale di testo da PDF non cifrati (stream FlateDecode, operatori Tj/TJ). Solo lettura.
Uso: python -I pdf_testo.py file.pdf > file.txt"""
import sys, re, zlib

data = open(sys.argv[1], "rb").read()
out = []
for m in re.finditer(rb"stream\r?\n", data):
    s = m.end()
    e = data.find(b"endstream", s)
    if e < 0:
        continue
    raw = data[s:e]
    try:
        dec = zlib.decompress(raw)
    except Exception:
        try:
            dec = zlib.decompressobj().decompress(raw)
        except Exception:
            continue
    if b"BT" not in dec:
        continue
    for bt in re.findall(rb"BT(.*?)ET", dec, re.S):
        parts = []
        for t in re.findall(rb"\((?:[^()\\]|\\.)*\)|<[0-9A-Fa-f]+>", bt):
            if t.startswith(b"("):
                parts.append(t[1:-1].decode("latin-1"))
            else:
                h = t[1:-1]
                try:
                    b = bytes.fromhex(h.decode())
                    parts.append(b.decode("utf-16-be", "replace") if len(b) % 2 == 0 and b[:1] == b"\x00" else b.decode("latin-1"))
                except Exception:
                    pass
        line = "".join(parts).strip()
        if line:
            out.append(line)
sys.stdout.buffer.write("\n".join(out).encode("utf-8", "replace"))
