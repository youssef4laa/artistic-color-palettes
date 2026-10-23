import sys; sys.path.insert(0,'.')
from colour import *
sys.stdout.reconfigure(encoding="utf-8")
def m(l,fg,bg): print(f"  {l:<55} {fg} on {bg}: WCAG {wcag_ratio(fg,bg):.2f}:1 APCA {apca_lc(fg,bg):+.1f} {' '.join(flags(fg,bg))}")
def adj(l,fg,bg,t,d=+1):
    L,C,h=hex_to_oklch(fg); cur=fg; n=0
    while abs(apca_lc(cur,bg))<t and n<60: L+=d*0.01; cur=oklch_to_hex(L,min(C,cmax(L,h)),h); n+=1
    L1,C1,_=hex_to_oklch(cur); print(f"  ADJUST {l}: {fg} (L {hex_to_oklch(fg)[0]:.3f}, {wcag_ratio(fg,bg):.2f}, {apca_lc(fg,bg):+.1f}) -> {cur} (L {L1:.3f} C {C1:.3f}, {wcag_ratio(cur,bg):.2f}, {apca_lc(cur,bg):+.1f}) on {bg}")
print("(a)")
m("text neutral-900 on voice-1 pinned #b5b1d8", "#2c2d35", "#b5b1d8")
m("accent-text #005b8d on voice-1 pinned", "#005b8d", "#b5b1d8")
m("accent-500 vs voice-700 adjacency", "#1b91d8", "#584b90")
m("dark: neutral-50 on accent-600 pinned", "#f1f1f6", "#005b8d")
print(f"  dL accent-500 {hex_to_oklch('#1b91d8')[0]:.3f} vs voice-700 {hex_to_oklch('#584b90')[0]:.3f}")
print("(b)")
adj("dark muted Lyons-dark-300 -> Lc 60", "#8ea2c5", "#0f1829", 60)
m("dark: Raw Sienna dark-300 vs bg adjacency (non-text 3.0)", "#c49771", "#0f1829")
m("light: ground-600 panel light text", "#f4f7fb", "#3169ce")
for h in ["#f4f7fb","#1c1f25","#15655f","#e7eaed","#0f1829","#2b736d","#eff2f6","#0a0d12","#c49771","#e7d6c7","#151f31","#8ea2c5","#abe7e0"]:
    print("  ",h,fmt_oklch(h))
print("(c)")
m("dark: neutral-50 on accent-600 (= pinned Vermeer blue)", "#f3f2ed", "#254D83")
m("dark: focus accent-400 non-text on bg", "#5b85be", "#0f0d08")
m("dark: accent-500 vs accent-600 hover adjacency", "#3f679e", "#254D83")
m("light: accent-600 vs accent-700 hover adjacency", "#386fb9", "#254D83")
m("light: tan pinned as large text on column", "#C89D7A", "#f8f7f2")
m("light: muted neutral-700 on ground-2 wells", "#5c584d", "#C6BDA9")
for h in ["#f8f7f2","#0f0d08","#29261e","#5c584d","#386fb9","#e0d7d1","#b7cff1","#cdbdba","#3f679e","#2d251e","#8d897c","#b8b4a7"]:
    print("  ",h,fmt_oklch(h))
