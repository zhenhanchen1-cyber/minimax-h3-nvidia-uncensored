# NOTICE · 第三方组件与许可

本仓库（MiniMax-H3 · N 卡本地部署方案）的**脚本与文档**采用 MIT 许可。
以下第三方组件的版权与许可归其各自作者所有。

## 模型权重（不在本仓库中，由脚本从公开仓库下载）

| 组件 | 来源 | 说明 |
|---|---|---|
| MiniMax-H3 官方权重（fl2va / ref2va / VAE） | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) | 遵循 **MiniMax H3 Community License** |
| 融合加速模型（fused turbo int8 convrot） | [MATLOWAI/minimax-h3-fused-turbo-int8-convrot](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot) | 社区公开权重 |
| GGUF 量化（主模型） | [unsloth/MiniMax-H3-GGUF](https://huggingface.co/unsloth/MiniMax-H3-GGUF)、[Abiray/MiniMax-H3-Pruned-GGUF](https://huggingface.co/Abiray/MiniMax-H3-Pruned-GGUF) | 社区公开权重 |
| 无审查文本编码器（GGUF） | [eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF](https://huggingface.co/eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF) | 社区公开权重 |
| 无审查文本编码器（NVFP4） | [Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) | 社区公开权重 |
| 无审查文本编码器（INT8 ConvRot） | [ethanfel/Qwen3-VL-32B-Ultra-Heretic-MiniMax-H3-ComfyUI-INT8-ConvRot](https://huggingface.co/ethanfel/Qwen3-VL-32B-Ultra-Heretic-MiniMax-H3-ComfyUI-INT8-ConvRot) | 社区公开权重 |
| Turbo LoRA（官方 4 步 / 8 步） | [lightx2v/Minimax-h3-Turbo](https://huggingface.co/lightx2v/Minimax-h3-Turbo) | 蒸馏方法开源于 [ModelTC/Minimax-H3-Turbo](https://github.com/ModelTC/Minimax-H3-Turbo) |
| 换脸 LoRA | [UntMods/FaceSwap_MiniMaxH3_REF2VA](https://huggingface.co/UntMods/FaceSwap_MiniMaxH3_REF2VA) | 社区公开权重 |
| 潜空间放大器 | [LBH-123-AI/Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) | 社区公开权重 |

> **⚠️ 许可提醒（重要）**：MiniMax H3 Community License 定义了 "Applicable Territory"，
> 其中**排除了部分地区**；非商业用途免费，商业用途对年营收有门槛限制。
> 使用前请自行阅读模型仓库中的 LICENSE 全文。社区量化权重属于**
> Model Derivatives**（量化会改变数值），其仓库中通常会附带 NOTICE 说明改动。

## 代码与节点（由 `scripts/install.sh` 从上游克隆，不包含在本仓库）

| 组件 | 来源 | 许可 |
|---|---|---|
| ComfyUI | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | GPL-3.0 |
| GGUF 加载节点 | [calcuis/gguf](https://github.com/calcuis/gguf) | 见仓库 |
| SLA 稀疏注意力节点 | [PlagueKind/ComfyUI-PlagueKind-Nodes](https://github.com/PlagueKind/ComfyUI-PlagueKind-Nodes) | 见仓库 |
| de-rope / DyRoPE / 音频节点 | [MATLOWAI/ComfyUI-MAINodes](https://github.com/matlowai/ComfyUI-MAINodes) | 见仓库 |
| FFN 分块 / SageAttention 补丁 | [kijai/ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes) | GPL-3.0 |
| Turbo 采样节点 | [Larryvrh/ComfyUI-MiniMax-H3-Turbo](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo) | Apache-2.0 |

## 工作流

`workflows/` 下的 JSON 来自上述社区仓库的公开分享（MATLOWAI 系列、Comfy-Org 官方模板），
本仓库仅做归档与显存适配整理。原始作者与出处见各文件名前缀。

## 免责声明

本仓库只提供**部署配方**（脚本 / 文档 / 工作流），不包含也不分发任何模型权重。
模型权重由使用者自行从公开仓库下载，由此产生的许可、合规与内容责任由使用者自行承担。
