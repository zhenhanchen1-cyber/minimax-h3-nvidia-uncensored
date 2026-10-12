#!/usr/bin/env bash
# =============================================================
# MiniMax-H3 · N 卡可选增强件安装（社区热门单点工具）
#
#   bash scripts/install_extras.sh              # 全部装
#   bash scripts/install_extras.sh spectrum     # 只用 Spectrum（省 30~35% 时间）
#   bash scripts/install_extras.sh upscaler     # 只用潜空间放大器（低分辨率出片再放大）
#   bash scripts/install_extras.sh list         # 看看有哪些
#
# 说明：这些是"可选增强"，不在 install.sh 里默认装，
#       因为它们属于近似加速 / 后处理，会改变出片结果，需要你自己 A/B 确认。
# =============================================================
set -uo pipefail

COMFY_HOME="${COMFY_HOME:-$HOME/ComfyUI}"
NODES="$COMFY_HOME/custom_nodes"
TARGET="${1:-all}"

mkdir -p "$NODES"
echo "ComfyUI 目录: $COMFY_HOME"
echo "安装目标: $TARGET"
echo

clone () {   # $1=目录名 $2=仓库URL $3=说明
    if [ -d "$NODES/$1" ]; then
        echo "  已存在，跳过: $1"
    else
        git clone --depth 1 "$2" "$NODES/$1" 2>/dev/null \
            && echo "  ✓ $1 — $3" \
            || echo "  ✗ $1 克隆失败，手动装: $2"
    fi
}

install_spectrum () {
    echo "【Spectrum】免训练推理加速（省 30~35% 时间，非无损）"
    clone ComfyUI-Spectrum-MiniMax-H3 \
        https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3.git \
        "节点在 sampling/spectrum → Spectrum Apply MiniMax H3"
    cat <<'EOF'

  用法：
    模型加载 → LoRA/补丁 → MiniMax H3 Sigma Shift → [Spectrum] → Guider/Sampler
  注意：
    - 与 EasyCache / LazyCache 冲突，二选一
    - 快速动作、眼睛/手指细节可能畸形 → 关键出片前关掉 enabled 做 A/B 对比
    - 只支持 Euler / RES multistep / H3 Turbo；其他采样器自动回退原生路径
EOF
    echo
}

install_upscaler () {
    echo "【Latent Upscaler】潜空间放大（低分辨率出片 → 放大 → 精化）"
    clone Comfyui_Minimax_h3_latent_Upscaler \
        https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler.git \
        "节点在 video/MinimaxH3 → Latent Upscaler (2D/3D)"

    MODEL_DIR="$COMFY_HOME/models/latent_upscale_models"
    mkdir -p "$MODEL_DIR"
    FILE="minimax_h3_latent_upscaler_3d_fp16.safetensors"
    if [ -f "$MODEL_DIR/$FILE" ]; then
        echo "  模型已存在，跳过: $FILE"
    else
        echo "  下载放大模型（约 691MB）→ $MODEL_DIR/$FILE"
        if command -v curl >/dev/null 2>&1; then
            curl -L --fail -o "$MODEL_DIR/$FILE" \
                "https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/main/$FILE" \
                && echo "  ✓ 模型下载完成" \
                || echo "  ✗ 下载失败，手动下: https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler"
        else
            echo "  ✗ 没找到 curl，手动下载到 $MODEL_DIR/"
        fi
    fi
    cat <<'EOF'

  用法：
    低分辨率 H3 Latent → [Latent Upscaler] → 精化/再采样 → VAE Decode
  注意：
    - 省时间不省显存（精化仍跑目标分辨率）
    - 放大倍数 1.0×~4.0×（默认 2.0×）
    - 只吃 H3 的 24 通道 latent，喂别的模型会报 channel 错误
EOF
    echo
}

case "$TARGET" in
    spectrum) install_spectrum ;;
    upscaler) install_upscaler ;;
    all)      install_spectrum; install_upscaler ;;
    list)
        echo "可选增强件："
        echo "  spectrum — 免训练加速，省 30~35% 时间（非无损）"
        echo "  upscaler — 潜空间放大，低分辨率出片再放大到高清"
        ;;
    *) echo "未知选项: $TARGET（可选：spectrum / upscaler / all / list）"; exit 1 ;;
esac

echo "============================================================"
echo "完成。重启 ComfyUI 后生效："
echo "  cd $COMFY_HOME && python main.py --listen"
echo
echo "建议：先用同一 prompt + 同一 seed，分别开着和关着增强件各跑一次，"
echo "      确认画质能接受再用于正式出片。"
echo "============================================================"
