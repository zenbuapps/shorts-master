#!/usr/bin/env python3
"""渲染 6 套字卡風格的預覽圖（1080×1920）。
用法: python3 build_previews.py  （需 macOS + Google Chrome）
每張圖內容相同（STEP chip / 強調貼紙 / hook 卡 / 字幕行），僅換風格 token。"""
import os, pathlib, subprocess

OUT = pathlib.Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:540px; height:960px; overflow:hidden; }}
#stage {{ position:relative; width:540px; height:960px; overflow:hidden;
  background:
    radial-gradient(circle at 75% 22%, rgba(255,225,180,.30), transparent 45%),
    radial-gradient(circle at 18% 60%, rgba(140,180,220,.22), transparent 40%),
    linear-gradient(165deg,#46566b 0%,#2c3646 55%,#1d2431 100%); }}
.bokeh {{ position:absolute; border-radius:50%; filter:blur(14px); opacity:.35; }}
.b1 {{ width:120px;height:120px;background:#ffd9a0;left:60px;top:120px; }}
.b2 {{ width:80px;height:80px;background:#a8c8e8;right:70px;top:330px; }}
.b3 {{ width:140px;height:140px;background:#8899bb;left:120px;top:640px; }}
.person {{ position:absolute; left:50%; top:44%; transform:translate(-50%,-50%);
  width:230px; height:300px; }}
.head {{ width:120px;height:140px;border-radius:56px 56px 48px 48px;background:#c9a184;margin:0 auto; }}
.hair {{ position:absolute; left:50%; top:-16px; transform:translateX(-50%); width:140px; height:86px;
  border-radius:70px 70px 40px 40px; background:#a5713c; }}
.body {{ width:230px;height:150px;border-radius:60px 60px 0 0;background:#b9bec7;margin:-18px auto 0; }}
.name {{ position:absolute; left:0; right:0; text-align:center; top:104%; font:600 17px/1 -apple-system; color:rgba(255,255,255,.4); letter-spacing:.2em; }}
{style_css}
</style></head><body><div id="stage">
<div class="bokeh b1"></div><div class="bokeh b2"></div><div class="bokeh b3"></div>
<div class="person"><div class="hair"></div><div class="head"></div><div class="body"></div><div class="name">口播畫面示意</div></div>
{style_body}
<div class="stylename">{label}</div>
</div></body></html>"""

COMMON_LABEL = """.stylename { position:absolute; left:0; right:0; bottom:22px; text-align:center;
  font:700 20px/1 -apple-system; color:rgba(255,255,255,.55); letter-spacing:.14em; }"""

STYLES = {
"editorial": ("Editorial 大字報", COMMON_LABEL + """
.chip0 { position:absolute; left:18px; top:64px; display:flex; align-items:center; gap:8px;
  background:rgba(16,18,23,.92); border:2px solid rgba(255,255,255,.9); border-radius:999px; padding:8px 16px; }
.chip0 .sq { width:10px;height:10px;background:#FFD54D;border-radius:2px; }
.chip0 .t { font:800 17px/1 'PingFang TC'; color:#fff; }
.pop { position:absolute; right:20px; top:130px; background:#FFD54D; border:3px solid #16181D; border-radius:10px;
  box-shadow:5px 5px 0 rgba(10,12,16,.85); padding:10px 16px; transform:rotate(4deg);
  font:800 26px/1.1 'PingFang TC'; color:#16181D; }
.hook { position:absolute; left:20px; bottom:150px; background:#FFFDF6; border:2.5px solid #16181D; border-radius:12px;
  box-shadow:6px 6px 0 rgba(10,12,16,.88); padding:18px 22px 20px; }
.hook .k { font:800 12px/1 'Inter','PingFang TC'; letter-spacing:.2em; color:#E5484D; margin-bottom:6px; }
.hook .l1 { font:800 30px/1.2 'PingFang TC'; color:#16181D; }
.hook .mark { display:inline-block; font:800 50px/1.15 'PingFang TC'; background:#FFD54D; color:#16181D;
  padding:1px 10px 3px; border-radius:6px; margin-top:4px; }
.subline { position:absolute; left:0; right:0; bottom:330px; text-align:center;
  font:800 34px/1 'PingFang TC'; color:#fff;
  text-shadow:-3px -3px 0 #000,3px -3px 0 #000,-3px 3px 0 #000,3px 3px 0 #000,0 3px 0 #000,0 -3px 0 #000,3px 0 0 #000,-3px 0 0 #000; }
.subline .kw { color:#FFD54D; }
""", """
<div class="chip0"><div class="sq"></div><div class="t">STEP 2 — 加上字卡動畫</div></div>
<div class="pop">不只是順剪！</div>
<div class="hook"><div class="k">AI CUT EXPERIMENT</div><div class="l1">這支影片是</div><div><span class="mark">AI 剪的</span></div></div>
<div class="subline">就是 <span class="kw">AI 幫我剪的</span></div>
"""),

"variety": ("Variety 綜藝爆字", COMMON_LABEL + """
.chip0 { position:absolute; left:16px; top:60px; padding:8px 16px; border-radius:12px;
  background:linear-gradient(180deg,#FF5FA2,#E5338B); border:3px solid #fff; box-shadow:0 5px 0 rgba(0,0,0,.4);
  font:900 18px/1 'PingFang TC'; color:#fff; transform:rotate(-2deg); }
.pop { position:absolute; right:12px; top:120px; transform:rotate(5deg);
  font:900 40px/1.05 'PingFang TC';
  background:linear-gradient(180deg,#FFE14D 20%,#FF7A00 85%); -webkit-background-clip:text; background-clip:text; color:transparent;
  filter:drop-shadow(2px 2px 0 #fff) drop-shadow(-2px -2px 0 #fff) drop-shadow(2px -2px 0 #fff) drop-shadow(-2px 2px 0 #fff) drop-shadow(0 6px 2px rgba(0,0,0,.45)); }
.burst { position:absolute; right:150px; top:118px; font:900 30px/1 sans-serif; color:#FFE14D;
  text-shadow:2px 2px 0 #000; transform:rotate(-12deg); }
.hook { position:absolute; left:0; right:0; bottom:170px; text-align:center; }
.hook .l1 { font:900 34px/1.2 'PingFang TC'; color:#fff;
  text-shadow:-3px -3px 0 #2c3646,3px -3px 0 #2c3646,-3px 3px 0 #2c3646,3px 3px 0 #2c3646,0 6px 0 rgba(0,0,0,.5); }
.hook .mark { display:block; font:900 68px/1.15 'PingFang TC';
  background:linear-gradient(180deg,#6EF3FF 15%,#2F6BFF 90%); -webkit-background-clip:text; background-clip:text; color:transparent;
  filter:drop-shadow(3px 3px 0 #fff) drop-shadow(-3px -3px 0 #fff) drop-shadow(-3px 3px 0 #fff) drop-shadow(3px -3px 0 #fff) drop-shadow(0 8px 3px rgba(0,0,0,.5)); transform:rotate(-2deg); }
.subline { position:absolute; left:0; right:0; bottom:335px; text-align:center;
  font:900 38px/1 'PingFang TC'; color:#fff;
  text-shadow:-4px -4px 0 #000,4px -4px 0 #000,-4px 4px 0 #000,4px 4px 0 #000,0 5px 0 #000; }
.subline .kw { color:#FFE14D; }
""", """
<div class="chip0">STEP 2・字卡動畫</div>
<div class="burst">✦</div>
<div class="pop">不只是順剪！</div>
<div class="hook"><div class="l1">這支影片是</div><div class="mark">AI 剪的！</div></div>
<div class="subline">就是 <span class="kw">AI 幫我剪的</span></div>
"""),

"whiteboard": ("Whiteboard 手寫筆記", COMMON_LABEL + """
.chip0 { position:absolute; left:18px; top:64px; background:#FDF9EC; border:2px dashed #8a6f4d; border-radius:6px;
  padding:8px 14px; transform:rotate(-1.5deg); font:700 17px/1 'PingFang TC'; color:#5c4a33;
  box-shadow:0 4px 10px rgba(0,0,0,.25); }
.pop { position:absolute; right:22px; top:128px; background:#FFF6C9; padding:12px 18px; transform:rotate(3deg);
  box-shadow:0 6px 12px rgba(0,0,0,.3); font:800 26px/1.1 'PingFang TC'; color:#3a2f22;
  border-radius:4px 14px 6px 12px; }
.pop::before { content:''; position:absolute; left:50%; top:-8px; transform:translateX(-50%) rotate(-4deg);
  width:56px; height:16px; background:rgba(180,190,200,.55); }
.hook { position:absolute; left:22px; bottom:150px; background:#FBF7EE; border-radius:8px 20px 10px 16px;
  padding:18px 24px 20px; box-shadow:0 8px 16px rgba(0,0,0,.3); transform:rotate(-1deg); }
.hook .l1 { font:700 30px/1.25 'PingFang TC'; color:#2B2B2B; }
.hook .mark { font:800 48px/1.2 'PingFang TC'; color:#D6453D; display:inline-block; position:relative; }
.hook .mark svg { position:absolute; left:-8px; bottom:-6px; width:110%; }
.subline { position:absolute; left:0; right:0; bottom:330px; text-align:center;
  font:800 33px/1 'PingFang TC'; color:#FFF9E8;
  text-shadow:-3px -3px 0 #4a3b28,3px -3px 0 #4a3b28,-3px 3px 0 #4a3b28,3px 3px 0 #4a3b28,0 3px 0 #4a3b28; }
.subline .kw { color:#FFD54D; }
""", """
<div class="chip0">✏️ STEP 2 — 加上字卡動畫</div>
<div class="pop">不只是順剪！</div>
<div class="hook"><div class="l1">這支影片是</div><span class="mark">AI 剪的
  <svg viewBox="0 0 200 14" fill="none"><path d="M4 9 C 50 3, 90 13, 196 6" stroke="#D6453D" stroke-width="5" stroke-linecap="round"/></svg></span></div>
<div class="subline">就是 <span class="kw">AI 幫我剪的</span></div>
"""),

"minimal": ("Minimal 極簡", COMMON_LABEL + """
.chip0 { position:absolute; left:18px; top:64px; background:rgba(255,255,255,.14); backdrop-filter:blur(8px);
  border:1px solid rgba(255,255,255,.35); border-radius:999px; padding:8px 16px;
  font:600 15px/1 'PingFang TC'; color:#fff; letter-spacing:.12em; }
.pop { position:absolute; right:22px; top:132px; background:rgba(255,255,255,.96); border-radius:10px;
  padding:10px 18px; font:600 24px/1.1 'PingFang TC'; color:#111;
  box-shadow:0 10px 34px rgba(0,0,0,.22); }
.pop b { color:#0A84FF; font-weight:700; }
.hook { position:absolute; left:24px; bottom:158px; }
.hook .rule { width:44px; height:3px; background:#0A84FF; margin-bottom:12px; }
.hook .l1 { font:500 27px/1.35 'PingFang TC'; color:rgba(255,255,255,.88); letter-spacing:.04em; }
.hook .mark { font:700 52px/1.25 'PingFang TC'; color:#fff; letter-spacing:.02em; }
.subline { position:absolute; left:0; right:0; bottom:332px; text-align:center;
  font:600 30px/1 'PingFang TC'; color:#fff; text-shadow:0 2px 14px rgba(0,0,0,.7), 0 0 2px rgba(0,0,0,.9); }
.subline .kw { color:#9BD1FF; }
""", """
<div class="chip0">STEP 2 · 加上字卡動畫</div>
<div class="pop">不只是<b>順剪</b></div>
<div class="hook"><div class="rule"></div><div class="l1">這支影片是</div><div class="mark">AI 剪的</div></div>
<div class="subline">就是 <span class="kw">AI 幫我剪的</span></div>
"""),

"neon": ("Neon 夜光", COMMON_LABEL + """
.chip0 { position:absolute; left:18px; top:64px; background:rgba(8,10,20,.6); backdrop-filter:blur(6px);
  border:1.5px solid rgba(0,255,240,.8); border-radius:999px; padding:8px 16px;
  font:700 15px/1 'PingFang TC'; color:#8FFFF6; letter-spacing:.1em;
  box-shadow:0 0 14px rgba(0,255,240,.4), inset 0 0 10px rgba(0,255,240,.12); }
.pop { position:absolute; right:20px; top:128px; transform:rotate(2deg);
  background:rgba(10,8,22,.55); border:2px solid #FF3DF2; border-radius:12px; padding:10px 18px;
  font:800 26px/1.1 'PingFang TC'; color:#FFB8FA;
  box-shadow:0 0 18px rgba(255,61,242,.55), inset 0 0 12px rgba(255,61,242,.18);
  text-shadow:0 0 12px rgba(255,61,242,.9); }
.hook { position:absolute; left:22px; bottom:152px; background:rgba(8,10,20,.55); backdrop-filter:blur(8px);
  border:1.5px solid rgba(0,255,240,.7); border-radius:16px; padding:18px 24px 20px;
  box-shadow:0 0 24px rgba(0,255,240,.3); }
.hook .l1 { font:700 28px/1.3 'PingFang TC'; color:#EAFBFF; }
.hook .mark { font:800 52px/1.2 'PingFang TC'; color:#8FFFF6;
  text-shadow:0 0 10px rgba(0,255,240,.95), 0 0 30px rgba(0,255,240,.6), 0 0 60px rgba(0,255,240,.4); }
.subline { position:absolute; left:0; right:0; bottom:330px; text-align:center;
  font:800 32px/1 'PingFang TC'; color:#fff; text-shadow:0 0 6px rgba(0,0,0,.9),0 2px 4px #000,0 0 18px rgba(120,220,255,.35); }
.subline .kw { color:#8FFFF6; text-shadow:0 0 12px rgba(0,255,240,.9),0 2px 4px #000; }
""", """
<div class="chip0">⚡ STEP 2 — 加上字卡動畫</div>
<div class="pop">不只是順剪！</div>
<div class="hook"><div class="l1">這支影片是</div><div class="mark">AI 剪的</div></div>
<div class="subline">就是 <span class="kw">AI 幫我剪的</span></div>
"""),

"terminal": ("Terminal 工程師", COMMON_LABEL + """
.chip0 { position:absolute; left:18px; top:64px; background:#0D1117; border:1px solid #30363D; border-radius:8px;
  padding:8px 14px; font:700 15px/1 Menlo,'PingFang TC'; color:#3FB950; }
.pop { position:absolute; right:20px; top:128px; background:#0D1117; border:1px solid #D29922; border-radius:8px;
  padding:10px 16px; font:700 22px/1.2 Menlo,'PingFang TC'; color:#D29922; }
.pop::after { content:'▌'; color:#3FB950; animation:none; }
.hook { position:absolute; left:22px; bottom:150px; width:330px; background:#0D1117; border:1px solid #30363D;
  border-radius:10px; overflow:hidden; box-shadow:0 12px 30px rgba(0,0,0,.5); }
.hook .bar { display:flex; gap:6px; padding:10px 12px; background:#161B22; border-bottom:1px solid #30363D; }
.hook .dot { width:10px; height:10px; border-radius:50%; }
.hook .d1{background:#FF5F57}.hook .d2{background:#FEBC2E}.hook .d3{background:#28C840}
.hook .bd { padding:16px 18px 18px; font:700 20px/1.7 Menlo,'PingFang TC'; color:#E6EDF3; }
.hook .p { color:#3FB950; }
.hook .mark { font-size:34px; color:#79C0FF; }
.subline { position:absolute; left:0; right:0; bottom:332px; text-align:center;
  font:700 29px/1 Menlo,'PingFang TC'; color:#E6EDF3;
  text-shadow:-2.5px -2.5px 0 #000,2.5px -2.5px 0 #000,-2.5px 2.5px 0 #000,2.5px 2.5px 0 #000,0 3px 0 #000; }
.subline .kw { color:#3FB950; }
""", """
<div class="chip0">$ step 2/3 — 加上字卡動畫</div>
<div class="pop">不只是順剪！</div>
<div class="hook"><div class="bar"><div class="dot d1"></div><div class="dot d2"></div><div class="dot d3"></div></div>
<div class="bd"><span class="p">$</span> 這支影片是<br><span class="mark">AI 剪的_</span></div></div>
<div class="subline">就是 <span class="kw">AI 幫我剪的</span></div>
"""),
}

for key, (label, css, body) in STYLES.items():
    html = BASE.format(style_css=css, style_body=body, label=label)
    f = OUT / f"_{key}.html"
    f.write_text(html, encoding="utf-8")
    png = OUT / f"{key}.png"
    subprocess.run([CHROME, "--headless=new", f"--screenshot={png}",
                    "--window-size=540,960", "--force-device-scale-factor=2",
                    "--hide-scrollbars", "--default-background-color=00000000",
                    f"file://{f}"], check=True, capture_output=True)
    f.unlink()
    print("rendered", png.name)
print("done")
