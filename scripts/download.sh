#!/usr/bin/env bash
# 按显存自动选档下载模型（分片并行，支持断点续传）
# 用法:
#   bash scripts/download.sh                 # 自动探测显存并推荐
#   bash scripts/download.sh --vram 24       # 手动指定显存
#   bash scripts/download.sh --tier quality  # 手动指定档位 minimal/balanced/quality/max
#   bash scripts/download.sh --uncensored 0  # 用官方原版文本编码器（有审查）
#   bash scripts/download.sh --nvfp4         # RTX 50 系：NVFP4 文本编码器（15.7G）
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COMFY_HOME="${COMFY_HOME:-$HOME/ComfyUI}"
echo "模型目录: $COMFY_HOME/models"
python3 "$REPO_DIR/scripts/download.py" "$@"
