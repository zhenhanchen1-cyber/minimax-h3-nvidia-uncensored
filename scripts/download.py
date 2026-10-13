# -*- coding: utf-8 -*-
"""
MiniMax-H3 · N 卡模型下载器（按显存分档，分片并行 + 断点续传）

用法:
    python3 scripts/download.py                    # 自动探测显存并推荐
    python3 scripts/download.py --vram 24          # 手动指定显存(GB)
    python3 scripts/download.py --tier balanced    # 手动指定档位: minimal/balanced/quality/max
    python3 scripts/download.py --uncensored 0     # 改用官方原版文本编码器
"""
import os, sys, threading, argparse, requests
from concurrent.futures import ThreadPoolExecutor

BASE = "https://hf-mirror.com"
M = os.environ.get("COMFY_HOME", os.path.expanduser("~/ComfyUI")) + "/models"
NCHUNK = int(os.environ.get("MAX_CONN", "32"))
CHUNK = 64 * 1024 * 1024

# (repo, 仓库内路径, 本地子目录, 说明)
TIERS = {
    "minimal": [   # 8~12GB
        ("unsloth/MiniMax-H3-GGUF", "minimax_h3_fl2va_pruned-Q2_K.gguf", "diffusion_models", "主模型 Q2_K 6.7G"),
        ("unsloth/MiniMax-H3-GGUF", "qwen3vl_32b_minimax_h3-Q2_K_M.gguf", "text_encoders", "文本编码器 Q2_K_M 13.1G"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_fp16.safetensors", "vae", "视频VAE 5.2G"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors", "vae", "音频VAE 0.6G(必须fp32)"),
        ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", "loras", "4步LoRA"),
    ],
    "balanced": [  # 16~24GB：推荐 融合模型 21G
        ("MATLOWAI/minimax-h3-fused-turbo-int8-convrot",
         "diffusion_models/minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot.safetensors",
         "diffusion_models", "融合Turbo 21G（4步出片，图生+参考二合一）"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_fp16.safetensors", "vae", "视频VAE"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors", "vae", "音频VAE(必须fp32)"),
        ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", "loras", "4步LoRA"),
        ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "loras", "8步LoRA"),
    ],
    "quality": [   # 24~32GB
        ("Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "diffusion_models", "剪枝 fp8 21G"),
        ("Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors", "diffusion_models", "参考图版 fp8 21G"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_fp16.safetensors", "vae", "视频VAE"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors", "vae", "音频VAE"),
        ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", "loras", "4步LoRA"),
        ("Comfy-Org/MiniMax-H3", "loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "loras", "8步LoRA"),
    ],
    "max": [       # 48GB+
        ("Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_fl2va_bf16.safetensors", "diffusion_models", "全精度 66G"),
        ("Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_ref2va_pruned_bf16.safetensors", "diffusion_models", "参考图剪枝 40G"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_fp16.safetensors", "vae", "视频VAE"),
        ("Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors", "vae", "音频VAE"),
    ],
}

# 文本编码器：无审查 / 官方
# 注意：8GB 档（minimal）目前**没有**体积可接受的无审查编码器（最小 15.7G NVFP4 仅 Blackwell、
# 其次 17.8G eraiko GGUF Q5_K_M），所以 minimal 档下的是官方 Q2_K_M 小档，先把流程跑通。
# 另外请阅读 README「关于无审查的真相」：编码器只做条件编码，换 heretic 并不等于解锁内容。
TEXT_ENCODERS = {
    ("uncensored", "minimal"): ("unsloth/MiniMax-H3-GGUF", "qwen3vl_32b_minimax_h3-Q2_K_M.gguf", 13.1),
    ("uncensored", "balanced"): ("eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF",
                                 "qwen3-vl-32b-ultra-heretic-minimax-h3-q5_k_m.gguf", 17.8),
    ("uncensored", "quality"): ("eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF",
                                "qwen3-vl-32b-ultra-heretic-minimax-h3-q6_k.gguf", 20.6),
    ("uncensored", "max"): ("eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF",
                            "qwen3-vl-32b-ultra-heretic-minimax-h3-q8.gguf", 26.7),
    ("official", "minimal"): ("unsloth/MiniMax-H3-GGUF", "qwen3vl_32b_minimax_h3-Q2_K_M.gguf", 13.1),
    ("official", "balanced"): ("Comfy-Org/MiniMax-H3", "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors", 27.1),
    ("official", "quality"): ("Comfy-Org/MiniMax-H3", "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors", 27.1),
    ("official", "max"): ("Comfy-Org/MiniMax-H3", "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors", 27.1),
}

lock = threading.Lock()
total = [0]


def dl(repo, rpath, subdir, note=""):
    url = f"{BASE}/{repo}/resolve/main/{rpath}"
    path = os.path.join(M, subdir, os.path.basename(rpath))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    size = int(requests.head(url, allow_redirects=True, timeout=60).headers["Content-Length"])
    fname = os.path.basename(path)
    done = path + ".done"
    # 注意：文件是预先 truncate 到全尺寸的，只比大小会把"没下完的"误判为已完成
    # 所以额外用 .done 标记判断是否真的下完过
    if os.path.exists(path) and os.path.getsize(path) == size and os.path.exists(done):
        print(f"[跳过] {fname} ({size/1e9:.2f}GB 已存在)")
        return
    if os.path.exists(done):
        os.remove(done)
    print(f"[下载] {fname} ({size/1e9:.2f}GB) {note}", flush=True)
    if not os.path.exists(path) or os.path.getsize(path) != size:
        open(path, "wb").truncate(size)

    ranges, s = [], 0
    while s < size:
        e = min(s + CHUNK - 1, size - 1)
        ranges.append((s, e)); s = e + 1

    def get(rg):
        a, b = rg
        pf = f"{path}.p{a}"
        pos = a + (os.path.getsize(pf) if os.path.exists(pf) else 0)
        for _ in range(6):
            try:
                while pos <= b:
                    r = requests.get(url, headers={"Range": f"bytes={pos}-{b}"}, stream=True, timeout=90)
                    r.raise_for_status()
                    with open(pf, "ab") as f, open(path, "r+b") as t:
                        t.seek(pos)
                        for buf in r.iter_content(1 << 20):
                            if buf:
                                f.write(buf); t.write(buf); pos += len(buf)
                                with lock: total[0] += len(buf)
                break
            except Exception as e:
                print(f"  [重试] {fname} @{a}: {repr(e)[:60]}", flush=True)
        if os.path.exists(pf):
            os.remove(pf)
    with ThreadPoolExecutor(max_workers=NCHUNK) as ex:
        list(ex.map(get, ranges))
    # 只有所有分片都成功、且残留分片文件都被清掉，才算真正完成
    leftover = [f for f in os.listdir(os.path.dirname(path))
                if f.startswith(os.path.basename(path) + ".p")]
    if leftover:
        print(f"[未完成] {fname} 仍有 {len(leftover)} 个分片未下完，重跑本命令可续传", flush=True)
        return
    open(done, "w").close()
    print(f"[完成] {fname}", flush=True)


def detect_vram():
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / 1e9
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vram", type=float, default=None, help="显存 GB，不填则自动探测")
    ap.add_argument("--tier", choices=["minimal", "balanced", "quality", "max"], default=None)
    ap.add_argument("--uncensored", type=int, default=1, help="1=无审查文本编码器(默认), 0=官方原版")
    ap.add_argument("--nvfp4", action="store_true", help="RTX 50 系：使用 NVFP4 文本编码器(15.7G)")
    a = ap.parse_args()

    vram = a.vram or detect_vram()
    if vram is None:
        print("无法自动探测显存，请用 --vram 指定，例如 --vram 24")
        sys.exit(1)
    tier = a.tier or ("minimal" if vram < 14 else "balanced" if vram < 24 else "quality" if vram < 40 else "max")
    print(f"=== 显存 {vram:.0f}GB → 档位 [{tier}]，文本编码器: {'无审查' if a.uncensored else '官方原版'}")

    files = list(TIERS[tier])
    if tier != "minimal":
        files = [f for f in files if "qwen3vl" not in f[1]]      # 移除档位里自带的 TE
    if a.nvfp4:
        files.append(("Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4",
                      "qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors", "text_encoders", "NVFP4 无审查 15.7G"))
    else:
        key = "uncensored" if a.uncensored else "official"
        repo, rpath, gb = TEXT_ENCODERS[(key, tier)]
        note = f"文本编码器 {gb}G"
        if key == "uncensored" and tier == "minimal":
            note += "（提示：8GB 档无小体积无审查编码器，此为官方小档；无审查见 README「真相」节）"
        files.append((repo, rpath, "text_encoders", note))

    print(f"共 {len(files)} 个文件，下载到 {M}\n")
    for f in files:
        dl(*f)
    print("\n全部完成！启动 ComfyUI 后在工作流里选中对应模型即可。")


if __name__ == "__main__":
    main()
