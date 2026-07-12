# 字卡樣式庫（1080×1920 直式）

## 風格系統：骨架與皮膚分離

15 種卡的**結構與動畫語彙（骨架）不變**，換一組 design token（皮膚）＝全新風格。Phase 4 開工先讓用戶從六套選一（沒偏好→推薦 editorial）。預覽圖見 `assets/styles/*.png`。

| 風格 | 卡片質感 | 字型/字重 | 動畫個性 | 字幕連動 |
|------|---------|----------|---------|---------|
| **editorial 大字報** | 紙底 #FFFDF6＋4-5px ink 邊＋硬陰影 | PingFang TC 800 | back.out 彈跳＋貼紙旋轉 | 白字黑邊＋黃色關鍵詞（本檔預設） |
| **variety 綜藝爆字** | 無底卡——漸層大字＋粗白描邊＋外層黑影 | PingFang TC 900、字級 +20% | scale 1.6→1 砸落＋shake、✦ 集中線 | 更粗更大（102級）、描邊加厚、黃色關鍵詞 |
| **whiteboard 手寫筆記** | 便利貼/紙片＋膠帶＋不規則圓角＋軟陰影 | LXGW WenKai TC（需完整版，缺→PingFang）700 | 手繪 draw-path 底線圈圈、輕擺動 | 米白字＋咖啡描邊、紅筆關鍵詞 |
| **minimal 極簡** | 白/毛玻璃、無邊或 1.5px 細線、無硬陰影 | PingFang TC 500-600、字距放寬 | fade＋y 12 power2，無彈跳 | 72級白字細邊、天藍關鍵詞 |
| **neon 夜光** | 深色毛玻璃＋1.5-2px 霓虹描邊＋glow box-shadow | PingFang TC 700-800 | opacity＋glow 呼吸、霓虹閃爍 2 下再亮定 | 白字＋青色 glow 關鍵詞 |
| **terminal 工程師** | #0D1117 終端機視窗（紅黃綠三點 bar）＋1px #30363D 邊 | Menlo/等寬＋PingFang、`$` prompt | 打字機逐字＋block cursor ▌ | 等寬體、綠色 #3FB950 關鍵詞 |

**Token 色板速查：** variety=漸層黃橙 #FFE14D→#FF7A00／青藍 #6EF3FF→#2F6BFF＋桃紅 chip；whiteboard=紙 #FBF7EE、墨 #2B2B2B、紅筆 #D6453D；minimal=單一強調色 #0A84FF（可換品牌色）；neon=青 #00FFF0＋洋紅 #FF3DF2 on rgba(8,10,20,.55)；terminal=#E6EDF3/#3FB950/#D29922/#79C0FF。

**實作方式：** 沿用本檔 Pattern 1-8 的結構與 GSAP 時間軸，僅替換 :root token＋卡片 chrome CSS＋進場 ease（variety 用 back.out(2.6)+shake、minimal 用 power2.out、terminal 用 stagger 打字）。預覽圖生成器 `assets/styles/build_previews.py` 內含六套的完整 CSS 配方可直接抄。

---

以下為 **editorial** 的完整配方（其他風格照上表換皮）：

全部沉澱自實戰。共用 token（定義在 composition :root）：

```css
--ink:#16181D; --paper:#FFFDF6;
--acc-y:#FFD54D; --acc-r:#E5484D; --acc-b:#2F6BFF; --acc-g:#30A46C; --acc-p:#8B5CF6;
```

共同 DNA：紙底＋4–5px ink 邊框＋硬陰影（`box-shadow:10px 10px 0 rgba(10,12,16,.88)`）＋圓角 16–20px。動畫語彙全片統一三種：逐字彈出（kinetic-chars）、scale-pop（back.out）、draw-path 手繪線。

## 版面原則

- 臉佔直式自拍畫面寬 25–75%、高 15–55% → 安全區＝**下半身衣服區＋左右上角**
- 連續出現的卡位置要錯開（左下→右下斜貼→中右直式…），避免「每張都在同一格」
- 有字幕時先定字幕帶，卡讓位；字幕距底 1/3 時卡可回填底部區
- 卡 host 一律 `card-host clip` 雙 class＋data-track-index；時間重疊的裝飾卡放 track 3

## Pattern 1 — Hook 大字報

kicker（小字距寬字母）＋一行中字＋**大字黃底 mark**＋灰色小註。mark 用 clipPath 掃入：

```css
.mark { font-size:112px; font-weight:800; background:var(--acc-y); padding:2px 22px 8px; border-radius:10px; }
```
```js
tl.fromTo(SEL, {clipPath:'inset(0 100% 0 0)'}, {clipPath:'inset(0 0% 0 0)', duration:.45, ease:'power3.out'}, T);
```

## Pattern 2 — 強調貼紙（頭旁邊、關鍵字同步）

黃底/紙底＋5px 邊＋±3–4° 旋轉，講到關鍵字瞬間 back.out 彈出＋輕微 wiggle：

```js
tl.fromTo(SEL, {scale:.2, rotation:-10}, {scale:1, rotation:4, duration:.38, ease:'back.out(2.4)'}, T);
tl.to(SEL, {rotation:1, duration:.14}, T+.42); tl.to(SEL, {rotation:4, duration:.14}, T+.56);
```

放頭的左右側上方（host 約 500×260），一支影片 2–3 張，過多會吵。

## Pattern 3 — STEP 系列 chip（B-roll / 段落標記）

黑膠囊白邊＋黃色小方塊＋白粗字，頂部滑入。同款出現 2–3 次形成系列感（STEP 1/2/3）：

```css
.chip { background:rgba(16,18,23,.92); border:3px solid rgba(255,255,255,.9); border-radius:999px; padding:14px 30px; }
```

## Pattern 4 — Pipeline 圖（節點跟語音逐個亮）

節點 chip＋箭頭，橫式（row＋➜）或直式（column＋↓）。每個節點的 pop 時間**對準講到該詞的 word timestamp**。中間主角節點反色（ink 底 paper 字）。

## Pattern 5 — 指尖圖表（手勢觸發）

面板 `transform-origin` 設在指尖方向角落，scale-pop 從手指「長出來」；長條 grow-y 逐根＋SVG 折線 draw-path＋count-up 數字：

```js
tl.fromTo(panel, {opacity:0, scale:.3}, {opacity:1, scale:1, duration:.5, ease:'back.out(1.7)'}, T); // origin 靠手指
// bars: fromTo height 0→N staggered；polyline: strokeDasharray=L → strokeDashoffset 0
// count-up: tl.to(obj,{v:327, onUpdate:()=>el.textContent='+'+Math.round(o.v)+'%'})
```

先抽該時間點的格確認手指位置再定 host 座標。

## Pattern 6 — 手繪圈臉（B-roll 上點名）

全畫布 SVG 兩顆橢圓（半徑略異、各轉 ±5°、一粗一細半透明）draw-path 依序畫出＝手繪感，配黃底標籤 chip 彈出。圈心座標從 B-roll 抽格量。

## Pattern 7 — Checklist 打勾

2×2 grid，每項 slide-in＋綠色 ✓ 方塊 scale-pop，stagger ~0.3s，對準「每個元素都有做到」類台詞。

## Pattern 8 — CTA 進度條＋印章

大字（關鍵詞紅色）＋進度條 scaleX 0→1＋count-up 到目標數字＋結尾**紅印章**（rotate -8°、power3.in 大→小蓋下）。印章時間對準口播結尾詞但寧早勿晚（至少留 1.2s 可視）；CTA 卡 hold 到最後一格不做退場 fade。

## 字幕雙樣式（ASS）

```
Style: Default,PingFang TC,76,&H00FFFFFF,...,Outline 5.5,Alignment 2,MarginV 620
Style: Emph,PingFang TC,96,...,Outline 6.5,MarginV 610
```
Emph 行前綴彈入：`{\fscx55\fscy55\t(0,130,\fscx100\fscy100)}`；關鍵詞變色 `{\c&H4DD5FF&}詞{\c&HFFFFFF&}`（BGR！黃=&H4DD5FF&、紅=&H4D48E5&）。強調句佔全片 15–25%，「就這麼簡單」類收尾句可整句紅配印章。
