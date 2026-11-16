import re, sys
def hx(h): return [int(h[i:i+2],16) for i in (1,3,5)]
def tint(h, w):
    r = [round(c*(1-w)+255*w) for c in hx(h)]; return "#%02X%02X%02X" % tuple(r)
def shade(h, w):
    r = [round(c*(1-w)) for c in hx(h)]; return "#%02X%02X%02X" % tuple(r)
B, A, P, R = "#2859A3", "#E69F00", "#9467BD", "#C0263A"
A_DK = shade(A, 0.22)
FILL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.88
MAP = {
    # world
    "#557A9C": B, "#E7EFF7": tint(B, FILL), "#F3F7FA": tint(B, 0.95),
    # action
    "#9C8223": A_DK, "#F4D87B": tint(A, 0.45), "#FFF5D6": tint(A, FILL - 0.03), "#FFFAEA": tint(A, 0.93),
    "#BAA35C": tint(A, 0.25), "#C9B879": tint(A, 0.4),
    # summary M
    "#4D7169": P, "#E7F0EB": tint(P, FILL),
    # target
    "#C7685D": R, "#FBF0ED": tint(R, FILL + 0.02),
    # history arrow neutral
    "#607585": "#6E6E6E",
    # pose axes -> palette RGB
    "#D1242F": "#D62728", "#078146": "#2CA02C", "#155AD4": "#1F77B4",
}
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
# SE(3) decoder (raw x = 855) uses the M colours in the source; it decodes the target -> red
def fix_decoder(s):
    out = []
    for m in re.finditer(r'<path[^>]*d="M855 406\.19[^>]*>', s):
        out.append((m.start(), m.end()))
    for a, b in reversed(out):
        t = s[a:b].replace('#e7f0eb', tint(R, FILL + 0.02)).replace('#4d7169', R)
        s = s[:a] + t + s[b:]
    return s, len(out)
s, n = fix_decoder(s)
# forecast path (dashed stroke #ae6547) -> red
s = re.sub(r'(stroke-dasharray[^>]*?)stroke="#ae6547"', r'\1stroke="%s"' % R, s, flags=re.I)
s = re.sub(r'stroke="#ae6547"', 'stroke="%s"' % R, s, flags=re.I)
for k, v in MAP.items():
    s = re.sub(re.escape(k), v, s, flags=re.I)
open(dst, "w", encoding="utf-8").write(s)
print("decoder elements", n)
