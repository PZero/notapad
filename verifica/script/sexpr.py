"""Parser S-expression minimale per file KiCad (simboli, impronte, netlist)."""
import re

TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


def parse(text):
    stack, cur = [], []
    for m in TOK.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return cur[0] if len(cur) == 1 else cur


def find(node, head):
    """tutti i sottonodi (ricorsivo) con primo elemento == head"""
    out = []
    if isinstance(node, list):
        if node and node[0] == head:
            out.append(node)
        for c in node:
            out.extend(find(c, head))
    return out


def child(node, head):
    for c in node:
        if isinstance(c, list) and c and c[0] == head:
            return c
    return None
