---
name: shorts-master
description: Use when the user has casually recorded talking-head phone clips (walking / selfie vlog style, multiple fragments with stutters, filler words and retakes) and wants them edited into a polished vertical short video. Triggers include 幫我剪片、順剪、剪成一分鐘短影片、邊走邊講的影片、亂錄的片段剪成 Reels/TikTok/Shorts、加字卡字幕B-roll配樂.
---

# Shorts Master 短影片大師

## Overview

把 N 段亂錄的直式口播片段，剪成一支帶 AI B-roll（本人入鏡）、動態字卡、繁中字幕、BGM 的精緻短影片。七個階段，每階段產出一版**先給用戶確認再進下一階段**；每個剪點與字卡都要抽格＋波形自我 QC 過才交付。

**輸入**：N 段影片（順序＝敘事順序）＋臉部參考照 2–4 張（可選，B-roll 入鏡用）＋目標時長。
**專案目錄**：`~/playwright/videos/<專案名>/`，成品同步到用戶指定位置。每階段結束更新 `edit/project.md`（session 記錄）。

## 前置檢查（開工前跑一次）

| 依賴 | 用途 | 缺了怎辦 |
|------|------|---------|
| `ELEVENLABS_API_KEY`（env 或專案 .env） | Scribe 轉錄（＋Music） | 轉錄 fallback faster-whisper（見下）；音樂改 Lyria／平台曲庫 |
| Higgsfield MCP（`claude mcp list` 有 higgsfield） | B-roll 生圖＋生影片 | 見 `references/integrations.md` 路線 A；或 ComfyUI Cloud（見同檔路線 C） |
| `GEMINI_API_KEY` 或 `OPENROUTER_API_KEY` | Lyria 3 BGM（$0.08/首）、備用生圖 | 音樂改 ElevenLabs 或平台曲庫 |
| 含 libass 的 ffmpeg（`ffmpeg -filters \| grep subtitles`） | 燒字幕 | macOS：`brew install ffmpeg-full` 用 `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`；**Homebrew 預設 ffmpeg 無 libass** |
| `npx hyperframes doctor` | 字卡渲染 | 照 doctor 提示補 |
| **磁碟剩餘 ≥5GB**（`df -h`） | render/合成中間檔吃 1-2GB/輪 | 清舊專案 clips_preview/、prenorm、已備份的成品副本；**磁碟滿時連 shell 都可能無法執行** |
| video-use skill（helpers＋venv） | 順剪工具鏈 | 照 video-use install.md |

**缺工具的處理原則：** 上表工具 agent **直接代裝**（brew/uv/git clone，經用戶權限確認；npx 類零安裝）；只有需要管理員密碼的（Homebrew 本體、Node）給指令請用戶自貼。Linux 註記：apt 版 ffmpeg 通常自帶 libass；中文字型改 Noto Sans TC。
**零服務底線：** 就算一個第三方服務都沒有，本地免費工具（ffmpeg＋HyperFrames＋faster-whisper）仍可完成**順剪＋變速＋全部字卡＋字幕＋人聲美化**的完整成片——只缺 AI B-roll（Phase 3 跳過）與 BGM（發佈平台曲庫補），約八成價值。開工檢查時明講會啟用哪些降級，不要跑到一半才失敗。

**AI 服務一個都沒有？** → 讀 `references/integrations.md`：三條推薦路線（**Higgsfield** 最省事一站式／**ComfyUI Cloud** 官方託管、workflow 全客製／**OpenRouter** 一把 key 吃生圖＋音樂）與零付費最低可行組合。

## 七階段管線

**REQUIRED SUB-SKILL：** Phase 1 用 video-use、Phase 4 用 talking-head-recut——本 skill 是總導演腳本，只補它們沒有的三塊：變速時間軸映射、B-roll 轉場策略、繁中雙樣式字幕。

### Phase 1 順剪（video-use）
transcribe_batch（Scribe word-level）→ pack_transcripts → 讀逐字稿挑 take：**完整句重講取最後一次最完整版；講半截的 false start 整段跳過；句間單獨的「呃」剪掉**。EDL 剪點貼字邊＋30–200ms padding，間隙 <150ms 的剪點靠 30ms fade 收。render.py 出 preview → timeline_view 驗每個剪點（無爆音、無切字）。
✅ checkpoint：回報總長＋剪了什麼。

### Phase 2 壓時長＋語速
先語意砍冗余（重複語意的子句、鋪陳、贅詞），再全片變速：`setpts=PTS/倍速` + `atempo=倍速`（不變調）。
**語速原則：短影音觀眾習慣偏快的語速，1.1–1.3x 是甜蜜區**——就算砍完冗余時長已達標，也預設加 1.1x 讓節奏更緊；需要壓時長時 `倍速 = 現長/目標長`，落在 1.1–1.3 剛好雙贏，超過 ~1.35x 要提醒用戶語速會明顯偏快、請用戶試聽把關。
✅ checkpoint：目標時長版本。

### Phase 3 AI B-roll（Higgsfield MCP）
最多 3–4 段、每段 2.5–3.5s、**跟正在講的話同步出現**；開場 hook 與結尾 CTA 保持本人在鏡頭上。
1. 臉照 media_upload → **nano_banana_pro** 生首幀（count 2 給用戶挑）；同場景多鏡位用前一張的 job_id 當參考連戲
2. **seedance_2_0** i2v：start_image 鎖首幀、9:16、1080p std、`generate_audio:false`；被 preset_recommendation 攔截就帶 `declined_preset_id` 重送
3. 合成鐵律：**B-roll 結尾要蓋過 EDL 場景跳接點**（切出去場景 A、回來已是場景 B，B-roll 即轉場），進出各加 0.2s alpha crossfade（`format=yuva420p` + `fade alpha=1`，fade 時間用 offset 前的本地時間）
✅ checkpoint：B-roll 版＋各段插入點說明。

### Phase 4 字卡動畫（talking-head-recut / HyperFrames）
時間戳**不重轉錄**，用 `helpers/map_timeline.py` 把 Phase 1 逐字稿映射到變速後時間軸。**先出風格選單讓用戶六選一**（editorial 大字報／variety 綜藝爆字／whiteboard 手寫筆記／minimal 極簡／neon 夜光／terminal 工程師——token 表與預覽圖見 card-patterns.md 與 assets/styles/，沒偏好推薦 editorial）。字卡全部進一支 `build.py`（META 表＋卡 HTML＋GSAP timeline），改卡＝改表重跑。版面：臉永遠不擋；**字幕帶（Phase 5 的位置）預留出來**；同軌時間重疊的卡用 `data-track-index` 分軌。樣式庫見 `references/card-patterns.md`。渲染 `npx hyperframes render`——**輸出無音軌**，之後 mux 回原音。
✅ checkpoint：字卡版（先 snapshot 抽查再全渲染）。

### Phase 5 繁中字幕
ASR 是簡體＋會有錯字（腳字稿/瞬剪類同音錯）→ **逐句手工轉繁＋修正**，寫進 `gen_subs.py` 的 CAPS 表（模板見 `references/gen_subs_template.py`）。雙樣式 ASS：Default 76 級＋Emph 96 級彈入（關鍵句，關鍵詞變色）。位置預設距底 1/3（MarginV≈610–620），問用戶偏好。**燒錄永遠在最後**（所有疊加層之後），用 ffmpeg-full。
✅ checkpoint 可與 Phase 6 合併。

### Phase 6 聲音
- BGM 兩管道任選：**ElevenLabs Music**（`POST /v1/music`，prompt＋`music_length_ms`）或 **Lyria 3**（`generativelanguage /v1beta/models/lyria-3-pro-preview:generateContent`，回傳 inlineData base64 mp3）。生成後量 `ebur128` 響度校 volume（人聲下墊 ≈ 主觀 0.4 上下）＋首尾 fade
- 人聲鏈：`highpass=f=90, afftdn=nr=12, EQ(-1.5dB@250 / +2.5dB@3.8k / +1.5dB@9.5k), acompressor 2.8:1` → amix `normalize=0` → `loudnorm=I=-14` → **必接 `aresample=48000`**
✅ checkpoint：完整成品。

### Phase 7 交付
`ffprobe` 驗收：音軌必須 48kHz（96kHz＝LINE 拒播）、`+faststart`、時長正確。抽 5–6 格關鍵畫面最終 QC。更新 project.md。

## 核心公式：時間軸映射

任何 word/剪點從「原始素材時間」換到「成品時間」：

```
final_t = (base_offset + (src_t - seg_start)) / speed
```

`base_offset`＝該 EDL 片段在 concat 後的起點；反向換算乘回去即可。`helpers/map_timeline.py` 吃 EDL＋倍速＋逐字稿 JSON 直接產出成品時間軸的 transcript.json——字卡、字幕、B-roll 對點全靠它。

## Provider Fallback

| 需求 | 首選 | 備選 | 備選的代價 |
|------|------|------|-----------|
| 轉錄 | ElevenLabs Scribe | faster-whisper medium（本地免費，繁體直出；輸出鍵名對齊成 Scribe 的 words[text/start/end] 即可餵 map_timeline.py） | **講半截的 false start 會被吞**；破綻＝異常長 word（>3s）當偵測訊號，再用 video-use 的 `timeline_view.py <clip> <start> <end>` 抽波形複查 |
| B-roll 圖 | nano_banana_pro（Higgsfield） | OpenRouter `google/gemini-3-pro-image`、ComfyUI Cloud Flux＋InstantID/PuLID | 見 integrations.md |
| B-roll 影片 | seedance_2_0（Higgsfield） | ComfyUI Cloud Wan 2.x／LTX-Video i2v、即夢/fal.ai | 要自組 workflow、保臉略遜 |
| BGM | Lyria 3（Gemini/OpenRouter key，$0.08）或 ElevenLabs Music | 平台內建曲庫（IG/TikTok 站內配樂，對觸及有加分）、ComfyUI Cloud ACE-Step | 平台曲庫發佈時才能加 |

## 踩雷速查（完整版見 references/gotchas.md）

| 症狀 | 原因＋解法 |
|------|-----------|
| LINE/手機 app 拒播 | loudnorm 輸出 96kHz AAC → 後面必接 `aresample=48000` |
| 燒字幕報 "No option name near" | 預設 ffmpeg 無 libass → 用 ffmpeg-full；字幕用 ASS 檔別用 force_style |
| hyperframes 成品沒聲音 | render 只出畫面 → ffmpeg mux 原音軌 |
| 中文轉錄字元碎裂 `��` | hyperframes transcribe（whisper-cli）不支援 CJK → Scribe 或 faster-whisper |
| B-roll 回來閃一下舊場景 | 結尾貼在跳接點前 1–3 格 → 延長 B-roll 蓋過跳接點 |
| lint clip_overlap error | 同 track 時間重疊 → 錯開時間或 data-track-index 分軌 |
| filter_complex 解析失敗 | 字串裡夾了換行 → 單行 |

## Red Flags（自我檢查）

- 沒開 timeline_view / snapshot 就說「剪好了」→ 先驗再交
- 直接用 ASR 原文上字幕 → 一定有簡體＋錯字，逐句過
- 重跑 Whisper/Scribe 只為了對字卡 → 用 map_timeline.py，轉錄一次就夠
- B-roll 蓋掉 hook 或 CTA 的本人畫面 → 重排
- 交付前沒 ffprobe 音軌取樣率 → LINE 事故重演
