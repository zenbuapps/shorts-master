# 服務串接指南（沒有現成 AI 服務的用戶從這裡開始）

本 skill 的 AI 依賴共四類能力：**轉錄、生圖（保臉）、生影片、音樂**。缺哪類就照下表補。推薦三條主路線：**Higgsfield**（最省事）、**ComfyUI Cloud**（官方託管、workflow 全客製）、**OpenRouter**（一把 key 吃多模型）。

## 能力 × 管道對照

| 能力 | Higgsfield | OpenRouter | ComfyUI Cloud（官方託管） | 其他 |
|------|-----------|------------|--------------------|------|
| 轉錄（word-level） | — | — | — | ElevenLabs Scribe（最準）或 **faster-whisper（免費本地，零 key）** |
| 生圖・保臉首幀 | nano_banana_pro / soul_2 ✅ | `google/gemini-3-pro-image`（同為 Nano Banana Pro） | Flux/SDXL＋**InstantID / PuLID**（臉部參考） | Gemini API 直呼（同模型） |
| 生影片（i2v） | seedance_2_0 / kling ✅ | ❌ 無影片模型 | **Wan 2.x / HunyuanVideo / LTX-Video** i2v workflow | 即夢（Dreamina）、fal.ai |
| 音樂 | ❌（無通用音樂） | `google/lyria-3-pro-preview`（$0.08/首） | ACE-Step / Stable Audio Open | ElevenLabs Music；或乾脆用發佈平台內建曲庫 |

**最省事組合（推薦預設）**：Higgsfield（圖＋影片）＋ OpenRouter（音樂）＋ Scribe 或 faster-whisper（轉錄）。
**最低成本組合**：faster-whisper（免費）＋ OpenRouter（生圖＋音樂，按次計費）＋ 影片砍掉或用 ComfyUI Cloud 按量計費——B-roll 本來就是可選強化，hook/CTA 都是真人實拍。

## 路線 A：Higgsfield（推薦首選——圖＋影片一站式）

官方 hosted MCP，OAuth 登入、不用管 API key，訂閱制 credits（seedance 1080p 約 45 credits/4s）。

```bash
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
# 重啟 session → /mcp → 選 higgsfield → 瀏覽器 OAuth 登入
```

接上後 Phase 3 的用法照 SKILL.md：`media_upload` 傳臉照 → `generate_image`（model `nano_banana_pro`，臉照當 `image` role 參考）→ `generate_video`（model `seedance_2_0`，首幀當 `start_image`）。
注意：MCP 是 session 啟動時載入的，加完要重啟；被 `preset_recommendation` 攔截就帶 `declined_preset_id` 重送。

## 路線 B：OpenRouter（一把 key，圖＋音樂＋LLM）

註冊 openrouter.ai 拿 key，OpenAI 相容 API。**覆蓋生圖與音樂，不覆蓋影片**——影片仍需 Higgsfield 或 ComfyUI Cloud。

```bash
export OPENROUTER_API_KEY=sk-or-...
# 生圖（保臉：臉照以 image_url 附在 messages 裡當參考）
#   model: google/gemini-3-pro-image
# 音樂（回傳 base64 audio）
#   model: google/lyria-3-pro-preview（完整曲 $0.08）或 lyria-3-clip-preview（30s $0.04）
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"google/lyria-3-pro-preview","messages":[{"role":"user","content":"Happy upbeat instrumental, ukulele and marimba, no vocals"}],"modalities":["audio"]}'
```

已有 `GEMINI_API_KEY` 的用戶可跳過 OpenRouter 直呼 Gemini API：
`POST generativelanguage.googleapis.com/v1beta/models/lyria-3-pro-preview:generateContent`（回傳 `inlineData` base64 mp3＋段落標記 text part）；生圖同理用 gemini image 模型。

## 路線 C：ComfyUI Cloud（官方託管，workflow 自由度最高）

comfy.org 官方雲端版（cloud.comfy.org）：**不用顯卡、不用架設**，用量計費（只算 workflow 實際執行的 GPU 時間，月費含 credits 池），**支援 API 程式化跑 workflow**——適合想完全客製生成管線、或要用開源模型（Wan / Flux）的用戶。

1. 註冊 Comfy Cloud → 拿 API key（方案與 credits 見 comfy.org/cloud/pricing）
2. **保臉生圖**：Flux/SDXL＋ **InstantID / PuLID** 節點吃臉部參考照 → 9:16 首幀；或用它的 **Partner Nodes（含 Nano Banana Pro）**——跟 Higgsfield 同款模型、但包在自訂 workflow 裡
3. **圖生影片**：**Wan 2.x / HunyuanVideo / LTX-Video** 的 i2v workflow，首幀進、4–5s 直式出
4. **音樂**（可選）：ACE-Step / Stable Audio Open workflow
5. agent 串接：workflow 先在 UI 調好 → Save (API Format) 匯出 JSON → 以 API 提交執行、輪詢取結果

定位：比 Higgsfield 多一層 workflow 客製自由（換模型、加節點、控制每個參數），代價是要自己組 workflow；標準管線需求用 Higgsfield 較快。自架版 ComfyUI 同一套 workflow 通用，有 GPU 的進階用戶可本地跑，非預設建議。

## 轉錄補充（所有路線共用）

- **有 ELEVENLABS_API_KEY**：Scribe（word-level＋false start 逐字保留，最適合順剪）
- **沒有**：faster-whisper（`uv venv && uv pip install faster-whisper`，medium/int8 CPU 可跑）——繁體直出、時間戳夠準；唯一缺陷是吞 false start，用「>3s 異常長 word」偵測＋波形複查補救（見 gotchas.md）
- 別用 whisper.cpp 系（hyperframes transcribe 後端）處理中文：CJK 字元會碎裂
