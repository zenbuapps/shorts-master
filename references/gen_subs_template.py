#!/usr/bin/env python3
"""繁中雙樣式字幕生成模板（ASS）。

流程：
1. map_timeline.py 產出成品時間軸 transcript.json（word-level）
2. 讀 ASR 原文，逐句填 CAPS 表：src=ASR 原字串（含錯字，用來對回 word 時間）、
   disp=修正後繁體顯示字串、style=Default|Emph、kw=要變色的關鍵詞、kc=色碼
3. 跑本腳本 → master.ass → ffmpeg-full 燒錄（-vf subtitles=master.ass，最後一層）

斷句原則：每行 8–14 個中文字、在標點或停頓處斷、行尾去句號。
"""
import json

words = json.load(open('transcript.json'))
words = [w for w in words if w['text'] != '--']
big = ''.join(w['text'] for w in words)
cmap = []
for i, w in enumerate(words):
    cmap.extend([i] * len(w['text']))

Y = r'\c&H4DD5FF&'   # #FFD54D 黃（BGR）
R = r'\c&H4D48E5&'   # #E5484D 紅（BGR）
W = r'\c&HFFFFFF&'

# ============ 逐句填這張表 ============
# (src_ASR原文, disp_繁中顯示, style, kw_變色詞, 色碼)
CAPS = [
    ("你现在看到的这支影片呢", "你現在看到的這支影片", "Default", None, None),
    ("就是AI帮我剪的", "就是 AI 幫我剪的", "Emph", "AI 幫我剪的", Y),
    # ...
]
# =====================================

lines, pos = [], 0
for src, disp, style, kw, kc in CAPS:
    idx = big.find(src, pos)
    assert idx >= 0, f"not found: {src}"
    w0, w1 = cmap[idx], cmap[idx + len(src) - 1]
    lines.append({'start': words[w0]['start'], 'end': words[w1]['end'],
                  'disp': disp, 'style': style, 'kw': kw, 'kc': kc})
    pos = idx + len(src)

MEDIA_END = 59.74  # 成品長度 - 一點餘量
for i, ln in enumerate(lines):
    tgt = ln['end'] + 0.25
    if i + 1 < len(lines):
        tgt = min(tgt, lines[i + 1]['start'] - 0.02)
    ln['end'] = min(max(tgt, ln['start'] + 0.35), MEDIA_END)

def a(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = int(t % 60)
    cs = min(int(round((t - int(t)) * 100)), 99)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

POP = r'{\fscx55\fscy55\t(0,130,\fscx100\fscy100)}'

# MarginV 620/610 = 字幕距底約 1/3；貼底改 160/150
header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang TC,76,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,5.5,0,2,40,40,620,1
Style: Emph,PingFang TC,96,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1.5,0,1,6.5,0,2,40,40,610,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

evs = []
for ln in lines:
    text = ln['disp']
    if ln['kw'] and ln['kw'] in text:
        pre, post = text.split(ln['kw'], 1)
        text = f"{pre}{{{ln['kc']}}}{ln['kw']}{{{W}}}{post}"
    if ln['style'] == 'Emph':
        text = POP + text
    evs.append(f"Dialogue: 0,{a(ln['start'])},{a(ln['end'])},{ln['style']},,0,0,0,,{text}")

open('master.ass', 'w').write(header + '\n'.join(evs) + '\n')
print('ass lines:', len(evs))
