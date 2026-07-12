# 踩雷全集（來源：ai-cut-flow 專案實戰 2026-07-12）

## ffmpeg

- **預設 `/opt/homebrew/bin/ffmpeg` 是精簡編譯**：無 libass／subtitles／drawtext。燒字幕報錯是誤導性的 `No option name near '...'`（不是 No such filter）。→ 一律用 `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` 燒字幕。
- **`loudnorm` 之後必接 `aresample=48000`**：loudnorm 內部以 192kHz 運算，直接出 AAC 會變 96kHz——桌面播放器正常、**LINE 與多數手機 app 拒播**，QC 很難發現。交付前 `ffprobe -select_streams a:0 -show_entries stream=sample_rate` 驗收。
- **`-filter_complex` 字串不能夾換行**（ffmpeg 8 解析直接炸），全部單行。
- 字幕燒錄用 **ASS 檔（樣式內嵌）**，不要用 `subtitles=xx.srt:force_style=...`——引號跨層轉義極易炸。ASS header 設 `PlayResX/Y` 等於成品解析度，Fontsize/MarginV 就是實際像素。
- overlay 疊 B-roll 前先 `ffprobe` 底片實際解析度——render.py --preview 直式輸出是 1080×1920 不是 720×1280，縮錯只會蓋左上 2/3。
- 拼接前每段重編碼成密集 keyframe（`-g <fps> -keyint_min <fps>`），否則 HyperFrames renderer seek 會凍格。

## 轉錄／ASR

- **Scribe 輸出簡體＋同音錯字**（腳字稿→逐字稿、順剪→瞬剪），上字幕前逐句人工轉繁＋修正，沉澱在 gen_subs.py 的 CAPS 表。
- **hyperframes transcribe（whisper-cli 後端）中文不可用**：CJK 多 byte 字元被 token 邊界切碎成 `��`，且整段只有一個時間戳。
- **faster-whisper（medium, int8, CPU）中文實測**：完整句重講逐字保留、「呃」抓得到、繁體直出、時間戳 vs Scribe 漂移 ±0.1–0.3s；**但講半截斷掉的 false start 會被 decoder 吞掉**——破綻是被吞處出現異常長的 word（例：「只是」3.38→10.64s），拿 >3s 的 word 當「此處有隱藏內容」偵測訊號，再用波形複查。
- Scribe 的 word token 會把尾隨標點黏進字裡（`'Claude，'` 一個 token、佔到下一字起點），排剪點時 end 時間要保守。

## Higgsfield / 生成

- generate_video 有時被 `preset_recommendation` 通知攔截（例：IN THE DARK preset）→ 帶 `declined_preset_id` 原 prompt 重送即可。
- 圖生影用 `start_image` role 鎖首幀＝保臉最穩；臉部參考照上傳一次，media_id 跨 session 有效。
- 同場景多鏡位連戲：後一張圖用前一張的 job_id 當 `image` 參考。
- nano_banana_pro 提交後實際跑的 model 名是 `nano_banana_2`，正常。
- Higgsfield `generate_audio` 不做通用音樂（sonilo_music 鎖在遊戲管線）；BGM 走 ElevenLabs Music 或 Lyria。
- MCP server 中途閃斷會報 `No such tool available` → ToolSearch 重載工具即可，不用重啟。

## HyperFrames / 字卡

- **render 輸出無音軌**（hasAudio:false）→ 成品必 mux 原音：`-map 0:v -map 1:a -c copy`。
- 同一 track 的 clip 時間重疊＝lint error → 錯開時間或 `data-track-index` 分軌（強調卡、STEP chip 常態放 track 3）。
- body 的 font-family 必須列具體字型名；系統中文字型（PingFang TC）用 `@font-face { src: local('PingFang TC') }` 宣告過 lint。
- `snapshot --at` 每次執行會覆蓋 snapshots/ → 逐次執行逐次 cp 出來。
- 中文粗體：PingFang TC weight 800 → 實際映射 Semibold，大字報夠用。
- 卡片位置變更後一定重抽 snapshot——「往上移」很容易壓到嘴巴/下巴（臉在直式自拍畫面裡佔 25–75% 寬、15–55% 高）。

## B-roll 合成

- **B-roll 結尾不能貼在 EDL 場景跳接點前 1–3 格**（會閃回舊場景又跳走）→ 延長 B-roll 蓋過跳接點，讓 B-roll 本身變成兩場景間的轉場。
- 進出各 0.2s alpha crossfade：`format=yuva420p,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st=<len-0.2>:d=0.2:alpha=1`，fade 的 st 用「offset 前」的本地時間，之後才 `setpts=PTS+<起點>/TB`。
- 換任一段 B-roll 的重組 SOP：重跑 composite → 重編 input-video.mp4（g=fps）→ hyperframes render → 音訊鏈＋字幕 assemble。
- **完整合成模板**（實戰版，單行、多段 B-roll 一次疊；`W:H` 用底片實際解析度）：

```bash
ffmpeg -y -i base.mp4 -i b1.mp4 -i b2.mp4 -filter_complex "[1:v]trim=1.3:4.8,setpts=PTS-STARTPTS,scale=W:H,fps=30,format=yuva420p,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st=3.3:d=0.2:alpha=1,setpts=PTS+15.0/TB[b1];[2:v]trim=0.3:3.2,setpts=PTS-STARTPTS,scale=W:H,fps=30,format=yuva420p,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st=2.7:d=0.2:alpha=1,setpts=PTS+27.0/TB[b2];[0:v][b1]overlay=enable='between(t,15.0,18.5)':eof_action=pass[v1];[v1][b2]overlay=enable='between(t,27.0,29.9)':eof_action=pass[vout]" -map "[vout]" -map 0:a -c:v libx264 -preset fast -crf 20 -c:a copy -movflags +faststart out.mp4
```

## 剪輯決策

- Scribe timestamps 漂移 50–100ms：剪點 padding 30–200ms；間隙 <150ms 的高風險剪點靠 30ms audio fade 兜底，剪完必抽波形驗證。
- 變速超過 ~1.35x 語速明顯偏快，先語意砍冗余再變速。
- BGM 換曲要先 `ebur128` 量響度差校 volume，混音比例才守恆。

## 磁碟空間

- **開工前 `df -h` 確認 ≥5GB**：render.py 每輪產生 clips_preview/（數百 MB）＋ base/prenorm/preview 各百餘 MB，hyperframes render 再 100-200MB；2026-07-12 實測磁碟滿時 ffmpeg 中途炸掉、且 agent 連 shell 暫存檔都寫不進去（完全癱瘓，需用戶手動清）。
- 每階段收尾清一次：clips_preview/、*.prenorm.mp4、被下一版取代的 preview；成品在交付目錄留一份即可。
