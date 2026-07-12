#!/usr/bin/env python3
"""把 word-level 逐字稿依 EDL＋變速倍率映射到成品時間軸。

用法:
  map_timeline.py <edl.json> <speed> <transcripts_dir> <out.json>

edl.json 需含:
  sources: {name: path, ...}
  ranges:  [{source, start, end}, ...]   # 依 concat 順序

transcripts_dir: 每個 source 一個 <name>.json（ElevenLabs Scribe 格式，
  含 words[]，每個 word 有 text/start/end；faster-whisper 輸出可先轉成同構）

輸出: 扁平 word array [{text, start, end}]，時間為「變速後成品」時間軸。
公式: final_t = (base_offset + (src_t - seg_start)) / speed
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    edl_path, speed, tdir, out_path = sys.argv[1:]
    speed = float(speed)
    edl = json.load(open(edl_path))
    tdir = Path(tdir)

    clips = {}
    for name in edl["sources"]:
        clips[name] = json.load(open(tdir / f"{name}.json")).get("words", [])

    out, base = [], 0.0
    for rng in edl["ranges"]:
        name, s0, s1 = rng["source"], rng["start"], rng["end"]
        for w in clips[name]:
            ws, we, t = w.get("start"), w.get("end"), (w.get("text") or "").strip()
            if ws is None or not t:
                continue
            if s0 <= ws < s1:
                out.append({
                    "text": t,
                    "start": round((base + (ws - s0)) / speed, 3),
                    "end": round((base + (min(we, s1) - s0)) / speed, 3),
                })
        base += s1 - s0

    out.sort(key=lambda w: w["start"])
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
    print(f"words: {len(out)}  span: {out[0]['start']}–{out[-1]['end']}s  → {out_path}")


if __name__ == "__main__":
    main()
