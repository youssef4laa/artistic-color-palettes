"""Gate check: flag quoted passages over 15 words and unresolved '??' readings."""
import re, sys
pat = re.compile(r'"([^"\n]{20,})"|“([^”]{20,})”|「([^」]{20,})」|^> (.+)$', re.M)
bad = 0
for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    for m in pat.finditer(text):
        q = next(g for g in m.groups() if g)
        n = len(q.split()) if re.search(r'[A-Za-z]', q) else len(q) // 2
        if n > 15:
            bad += 1; print(f"{path}: {n} words: {q[:90]}")
    for i, line in enumerate(text.splitlines(), 1):
        if "??" in line:
            bad += 1; print(f"{path}:{i}: '??' {line[:90]}")
    print(f"{path}: {len(text.splitlines())} lines")
sys.exit(1 if bad else 0)
