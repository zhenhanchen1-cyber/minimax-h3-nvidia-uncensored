#!/usr/bin/env bash
# =============================================================
# MiniMax-H3 · N 卡本地部署 一键安装
# 适用: NVIDIA 显卡（8GB 起，推荐 16GB+），CUDA 环境
# 用法: bash scripts/install.sh [COMFY_HOME]
# =============================================================
set -euo pipefail

COMFY_HOME="${1:-${COMFY_HOME:-$HOME/ComfyUI}}"
COMFY_COMMIT="${COMFY_COMMIT:-bd34f338ac505ea79e43968753968a464060e609}"
# 必须在任何 cd 之前算好，否则后面 dirname 会相对当前目录解析（曾导致工作流拷贝失败）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"

echo "=== [1/5] 环境检查 ==="
python3 - <<'PY'
import torch
print(f"torch {torch.__version__} | CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print(f"显卡: {torch.cuda.get_device_name(0)} | 显存 {p.total_memory/1e9:.1f} GB")
else:
    print("!! 未检测到 CUDA，请检查驱动与 torch 版本（需要 torch+cu121/cu124）")
    print("   安装示例: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
PY

echo "=== [2/5] 克隆 ComfyUI（锁定 commit，保证可复现）==="
if [ ! -d "$COMFY_HOME/.git" ]; then
    if [ -d "$COMFY_HOME" ] && [ -n "$(ls -A "$COMFY_HOME" 2>/dev/null)" ]; then
        # 目录已存在且非空（比如 models 已软链到数据盘）：克隆到临时目录再拷进去
        echo "  目录非空（保留已有内容，如 models 软链），改用临时目录克隆"
        TMP="$(mktemp -d)"
        git clone https://github.com/Comfy-Org/ComfyUI.git "$TMP/comfy"
        cp -a "$TMP/comfy/." "$COMFY_HOME/" 2>/dev/null || true
        rm -rf "$TMP"
    else
        git clone https://github.com/Comfy-Org/ComfyUI.git "$COMFY_HOME"
    fi
fi
cd "$COMFY_HOME"
git fetch --depth 1 origin "$COMFY_COMMIT"
git checkout --detach FETCH_HEAD
git log --oneline -1

echo "=== [3/5] 安装依赖 ==="
python3 -m pip install -q --upgrade pip -i "$PIP_MIRROR"
grep -v -E 'comfyui-workflow-templates|comfyui-embedded-docs' requirements.txt > /tmp/req_core.txt
python3 -m pip install -q -i "$PIP_MIRROR" -r /tmp/req_core.txt
python3 -m pip install -q --no-deps -i "$PIP_MIRROR" comfyui-workflow-templates comfyui-embedded-docs
# 可选加速（失败不影响主流程）
python3 -m pip install -q -i "$PIP_MIRROR" sageattention 2>/dev/null && echo "  SageAttention 已安装" || echo "  SageAttention 跳过（可选）"

echo "=== [4/5] 安装自定义节点 ==="
mkdir -p "$COMFY_HOME/custom_nodes"
cd "$COMFY_HOME/custom_nodes"

clone_node () {   # $1=目录名 $2=仓库URL
    if [ -d "$1" ]; then
        echo "  已存在，跳过: $1"
    else
        git clone --depth 1 "$2" "$1" 2>/dev/null && echo "  ✓ $1" || echo "  ✗ $1 克隆失败，可手动安装: $2"
    fi
}

clone_node ComfyUI-GGUF            https://github.com/calcuis/gguf.git
clone_node ComfyUI-PlagueKind-Nodes https://github.com/PlagueKind/ComfyUI-PlagueKind-Nodes.git
clone_node ComfyUI-MAINodes        https://github.com/matlowai/ComfyUI-MAINodes.git
clone_node ComfyUI-KJNodes         https://github.com/kijai/ComfyUI-KJNodes.git
clone_node ComfyUI-MiniMax-H3-Turbo https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo.git

echo "=== [5/5] 安装工作流 ==="
mkdir -p "$COMFY_HOME/user/default/workflows/minimax-h3-nvidia"
cp "$REPO_DIR"/workflows/*.json "$COMFY_HOME/user/default/workflows/minimax-h3-nvidia/"

cat <<EOF

============================================================
✅ 安装完成！

下一步：
  1) 下载模型（会按你的显存自动推荐档位）:
       bash scripts/download.sh
  2) 启动:
       cd $COMFY_HOME
       python main.py --listen                # 24GB+
       python main.py --listen --lowvram      # 16GB 及以下
  3) 浏览器打开 http://127.0.0.1:8188
     从 Workflows → minimax-h3-nvidia 选择工作流

节点说明：
  ComfyUI-GGUF            → 加载 GGUF 量化模型（低显存必备）
  ComfyUI-PlagueKind-Nodes → H3SLAAttention 稀疏注意力（提速关键）
  ComfyUI-MAINodes        → de-rope / DyRoPE / 音频节点（02/03 号工作流需要）
  ComfyUI-KJNodes         → FFN 分块（低显存工作流需要）
  ComfyUI-MiniMax-H3-Turbo → Turbo 采样节点
============================================================
EOF
