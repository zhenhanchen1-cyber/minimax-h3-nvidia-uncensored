<div align="center">

# 🎬 MiniMax-H3 · N 卡本地部署（8GB 显存起）

**在 NVIDIA 显卡上用 ComfyUI 本地跑 MiniMax-H3 全模态视频生成**
文生视频 · 图生视频 · 参考图锁角色 · **原生音画同步** · 全程离线 · 免费无限量

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GPU: NVIDIA CUDA](https://img.shields.io/badge/GPU-NVIDIA_CUDA-76B900)]()
[![VRAM: 8GB+](https://img.shields.io/badge/VRAM-8GB+-blue)]()
[![Models: 15+](https://img.shields.io/badge/Models-15+-purple)]()
[![Workflows: 9](https://img.shields.io/badge/Workflows-9-orange)]()

**中文** ｜ [English](#english)

</div>

> **🔥 一句话卖点**：8GB 显存就能跑 · **4 步出片** · 一条命令自动装 + 自动下模型 · **9 套现成工作流** · **15+ 模型按显卡自选**
>
> **姊妹项目**：昇腾 910B/910C 路线 → [minimax-h3-ascend-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored)（真机实测 · 免费算力）
>
> **🟢 活跃维护中** · 最近更新：2026-10-12（新增 Spectrum / 潜空间放大增强件）·
> 完整历史见 [CHANGELOG.md](CHANGELOG.md) —— 内容可以被复制，**持续的实测与更新不能**。

---

## 📑 目录

- [30 秒决策：我的卡能跑到什么程度？](#-30-秒决策我的卡能跑到什么程度)
- [三大看点](#-三大看点)
- [N 卡 vs 昇腾：为什么同样的视频 N 卡更省力](#-n-卡-vs-昇腾为什么同样的视频-n-卡更省力)
- [快速开始（两条命令）](#-快速开始两条命令)
- [三种玩法](#-三种玩法)
- [模型全家桶（按自己显卡挑）](#-模型全家桶按自己显卡挑)
- [加速全家桶（按收益排序）](#-加速全家桶按收益排序)
- [社区增强件（Spectrum / 潜空间放大）](#-社区增强件强烈推荐装了就能用)
- [工作流清单](#-工作流清单)
- [⚠️ 先读这个：「无审查文本编码器」的真相](#️-先读这个无审查文本编码器的真相)
- [注意事项](#-注意事项)
- [FAQ](#-faq)
- [📚 详细文档](#-详细文档)
- [⭐ 如果对你有帮助](#-如果对你有帮助)

---

## 🎯 30 秒决策：我的卡能跑到什么程度？

| 你的显存 | 主模型 | 文本编码器（**必须 safetensors**） | 分辨率 / 时长 | 预期 |
|---|---|---|---|---|
| **8GB** | GGUF Q2_K（6.7G） | INT8 ConvRot 26.4G（靠系统内存卸载） | 480P / 5s | ⚠️ 能跑，慢（分钟级，靠极限卸载） |
| **12GB** | GGUF Q3_K（8.8G） | 同上（卸载） | 480P / 5s | ✅ 可用 |
| **16GB** | 融合模型 21G 或 GGUF Q4_K（11.4G） | 同上（50 系可换 NVFP4 15.7G） | 576P~768P / 5~10s | ✅ **11 GiB / 65 秒**（社区实测） |
| **24GB（4090）** | 融合模型 21G / fp8 21G / GGUF Q5 | 同上（或官方 INT8 27.1G） | 768P / 10s | ✅ 畅快 |
| **32GB（5090）** | fp8 或 NVFP4 / pruned_bf16 | **NVFP4（15.7G）** | 768P / 10~15s | ✅ 更快 |
| **48GB（4090-48G 实测）** | 融合 Turbo 21G | INT8 ConvRot 26.4G | 0.4~0.98MP / 5s | ✅ **实测 54~243 秒**（见下表） |

> ⚠️ **文本编码器不要用 GGUF**（2026-10-13 真机验证）：所有 H3 的 GGUF 编码器仓库都**没有 mmproj 视觉塔**，
> `ClipLoaderGGUF` 必定崩溃（`TypeError: the JSON object must be str...`）。
> 必须用 **safetensors + 官方 `CLIPLoader`**；低显存靠 ComfyUI 的卸载机制（`--lowvram` / RAM offload）扛，
> 而不是靠换更小的 GGUF 编码器。`download.py` 已改为默认只下 safetensors。
> 文本编码器仍是低显存的**最大瓶颈**（Qwen3-VL-32B，最小可用档就是 26.4GB）；50 系可换 NVFP4（15.7GB）。
> 更低门槛：社区有 **4GB 笔记本**跑通的记录（低分辨率、分钟级）。

---

## 🔥 三大看点

1. **低显存门槛** —— 靠 **GGUF 量化（最小 6.7GB）+ 融合加速模型（21GB）+ FFN 分块卸载**，
   社区实测 **16GB 卡上 4 步生成仅占 11 GiB / 65 秒**；8GB 卡配合极限卸载同样能跑
2. **一键脚本 + 全模型自选** —— 从 6.7GB 的 Q2_K 到 66GB 的 BF16，从 4 步蒸馏到 25 步精修，
   **15+ 主模型 / 8 种文本编码器**全列出，按自己显卡挑；`install.sh` + `download.sh` 自动按显存选档
3. **13 套现成工作流** —— MATLOWAI 4 步全套（含 4 套**无SLA版**，驱动不够也能跑）+ 官方 i2v + 低显存 FFN 分块版，拖进 ComfyUI 即用
   （另附工作流 UI→API 转换脚本，可脚本化批量出片）

## ⚡ N 卡 vs 昇腾：为什么同样的视频 N 卡更省力

N 卡（CUDA）生态有昇腾目前没有的一整套加速件，同样的成片所需算力**低一个量级**：

| 加速手段 | 效果（N 卡实测） |
|---|---|
| **SLA 稀疏注意力**（sparsity 0.9） | 跳过 90% 注意力计算；且作者指出稀疏注意力下**音轨更饱满** |
| **融合 Turbo 模型**（21GB，4 步蒸馏已内置） | 4 步出片，官方模板要 8 步 |
| **NVFP4**（Blackwell / 50 系） | 权重减半、提速 |
| **SageAttention** | 注意力加速 |
| **GGUF 分层卸载** | 低显存跑大模型的关键 |
| **FFN 分块（KJNodes）** | 低显存档再省一点 |

**实测对照**（同一任务：约 10 秒、1152×640）：

| 平台 | 配置 | 耗时 |
|---|---|---|
| **RTX PRO 6000（96GB）** | 融合模型 + 4 步 + SLA | **76 秒** |
| 同上 | 8 步 | 103 秒 |
| 同上 | 25 步（精修） | 292 秒 |
| **16GB 卡** | 融合模型 + 4 步 + SLA | **11.0 GiB / 65 秒** |
| 昇腾 2×910B（姊妹项目实测） | 官方 INT8 + 8 步 | 12 秒片约 **11 分钟** |

> 上表 N 卡数据来自 [MATLOWAI/minimax-h3-fused-turbo-int8-convrot](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot) 的公开实测；
> 昇腾数据来自姊妹项目 [minimax-h3-ascend-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored) 的实测。
> 结论：**达到相近成片，N 卡所需算力约为昇腾的 1/5 ~ 1/8**。

---

## 📊 真机实测数据（RTX 4090 48GB · 2026-10-13）

固定同一张图 + 同一段提示词，seed=42，图生视频 124 帧（5.17 秒）：

| 档位 | 分辨率 | 步数 | **端到端** | 每步 | 显存峰值 |
|---|---|---|---|---|---|
| 极速 | 832×480（0.4MP） | 4 | **54.0 s** | ≈8 s | 48.5 GB |
| 日常 | 1024×576（0.6MP） | 4 | **84.1 s** | ≈16.5 s | 48.2 GB |
| 质量 | 1024×576（0.6MP） | 6 | **117.1 s** | 15.35 s | 48.2 GB |
| 高清 | 1344×768（0.98MP） | 6 | **243.1 s** | ≈37 s | 48.1 GB |

**三条结论：**

1. **分辨率是最大杠杆** —— 0.4MP→0.98MP 分辨率只涨 2.4 倍，**每步耗时涨 4.6 倍**。想快先降分辨率。
2. **步数是线性杠杆** —— 多 2 步多约 33 秒。日常 4 步，要画质 6 步。
3. **48GB 刚好够** —— 峰值稳定 48.1~48.5GB，说明 **24GB 卡必须走 offload，会明显更慢**。

> ⚠️ 读数须知：① 这批数据**未启用 SLA**（测试机驱动偏旧，`comfy_kitchen` 注意力核起不来），
> 属**保守值**，驱动正常的环境会更快；② 冷启动额外 20~25 秒（要加载 26GB 编码器 + 21GB 主模型）。
> 完整记录见 [N卡实测数据-4090-48G.md](https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored) 与
> [docs/工作流对照表.md](docs/工作流对照表.md)。

---

## 🚀 快速开始（两条命令）

**先确认三件事**（真机踩过，见 [docs/真机踩坑与前置要求.md](docs/真机踩坑与前置要求.md)）：

| 项目 | 要求 | 不满足会怎样 |
|---|---|---|
| 磁盘可用空间 | **≥ 60GB**（balanced 档模型约 48.25GB + ComfyUI 约 5GB） | 下到一半磁盘满；云主机"数据盘 50G"刚好不够 |
| 显卡驱动 | 想用 **SLA 加速**需驱动支持 **cu130+** | SLA 节点报 `detect_k_anchor kernel launch failed`，改用「无SLA版」工作流 |
| 文本编码器格式 | **必须 safetensors**（GPT 式 GGUF 编码器不可用） | `ClipLoaderGGUF` 崩（缺 mmproj 视觉塔），`download.py` 已默认只下 safetensors |

```bash
git clone https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored.git
cd minimax-h3-nvidia-uncensored

bash scripts/install.sh      # ① 装 ComfyUI + 必备节点（GGUF / SLA / MAINodes / KJNodes）
bash scripts/download.sh     # ② 按显存自动选档下载（会先问你是几 GB 的卡）

# ③ 启动
cd ~/ComfyUI && python main.py --listen                 # 24GB 及以上
cd ~/ComfyUI && python main.py --listen --lowvram       # 16GB 及以下
```

> **磁盘不够又不想扩盘？** 把 ComfyUI 装系统盘、模型放数据盘：
> `COMFY_HOME=/root/ComfyUI bash scripts/install.sh && ln -sfn /hy-tmp/models /root/ComfyUI/models`

浏览器打开 `http://127.0.0.1:8188`，从 `Workflows → minimax-h3-nvidia` 导入对应工作流即可。

想手动指定档位 / 显卡世代：

```bash
bash scripts/download.sh --vram 24         # 手动指定显存
bash scripts/download.sh --tier balanced   # minimal / balanced / quality / max
bash scripts/download.sh --nvfp4           # RTX 50 系用 NVFP4 编码器
```

> **环境还没配好？** `install.sh` 第 1 步会自动检测显卡与 torch，打印显存和 CUDA 可用状态，
> 环境不对会直接告诉你该装哪个 torch 版本，不会让你在一堆报错里猜。

---

## 🎬 三种玩法

| 玩法 | 用什么工作流 | 说明 |
|---|---|---|
| **文生视频（T2V）** | `MATLOWAI-01_reference_4step_sla.json` | 只给提示词，直接出片（最快基线档） |
| **图生视频（I2V / 首尾帧）** | `01_官方-图生视频-i2v.json` 或 `MATLOWAI-04_i2v_fl2v_4step_sla.json` | 给一张首帧图（可再加尾帧做插值），让画面动起来 |
| **参考图锁角色（Ref2VA）** | `MATLOWAI-05_ref2va_4step_sla.json` | 喂一张/多张参考图，锁住人物、服装、画风 |

**九宫格分镜玩法**：把 3×3 分镜图整张喂给 I2V 工作流，配合分镜脚本提示词，
一次生成一段按顺序推进的连续剧情 → 详见 [`docs/教程-文生视频与图生视频.md`](docs/教程-文生视频与图生视频.md)。

**做长片**：单次最长 15 秒（362 帧）。更长用「**尾帧接首帧**」分段接力 + ffmpeg 流拷贝拼接（1 秒完成，不重编码）。

---

## 📦 模型全家桶（按自己显卡挑）

### ① 融合加速模型（推荐首选，4 步出片）

| 模型 | 大小 | 特点 | 链接 |
|---|---|---|---|
| `minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot` | **21 GB** | ⭐ **图生视频 + 参考图二合一**，已内置 8 步 Turbo 蒸馏 + Mystic 运动平滑 LoRA，**4 步出片** | [MATLOWAI](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot) |

### ② 官方原版（Comfy-Org）

| 模型 | 大小 | 说明 |
|---|---|---|
| `minimax_h3_fl2va_bf16` | 66.3G | 文生/图生/首尾帧，全精度 |
| `minimax_h3_fl2va_pruned_bf16` | 40.2G | 剪枝全精度 |
| `minimax_h3_fl2va_pruned_fp8_scaled` | 21.0G | **4090 甜点位** |
| `minimax_h3_fl2va_pruned_int8_convrot` | 21.0G | INT8 |
| `minimax_h3_fl2va_pruned_w6a8` | 16.0G | 更省显存 |
| `minimax_h3_ref2va_*`（同系列） | 同上 | **参考图锁角色**版本 |

全部在 [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)。

### ③ GGUF 量化（低显存的救星）

**主模型**（[unsloth/MiniMax-H3-GGUF](https://huggingface.co/unsloth/MiniMax-H3-GGUF)）：

| 档位 | fl2va | ref2va |
|---|---|---|
| Q2_K | **6.72G** | 6.68G |
| UD-Q2_K_XL | 8.06G | — |
| Q3_K | 8.76G | 8.72G |
| UD-Q3_K_XL | 9.56G | — |
| Q4_K | 11.42G | 11.38G |
| Q5_0 | 13.89G | 13.89G |

> 另有 [Abiray/MiniMax-H3-Pruned-GGUF](https://huggingface.co/Abiray/MiniMax-H3-Pruned-GGUF) 的 Q3~Q8 系列可作备选
> （pruned 架构压到 8.9G~21.6G，更贴消费级显卡）。

### ④ 文本编码器（**只认 safetensors，GGUF 一律不可用**）

✅ **可用（safetensors + 官方 `CLIPLoader`，`type` 选 `minimax`）**：

| 文件 | 大小 | 适用 |
|---|---|---|
| `qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors` | **15.68G** | **仅 Blackwell（50 系）** |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 15.69G | 50 系（官方参考档） |
| `qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot` | 26.36G | ⭐ **本仓库默认**（去审查 + 通用） |
| `qwen3vl_32b_minimax_h3_int8_convrot` | 27.14G | 官方原版，通用 |

❌ **不可用（GGUF 文本编码器，全部缺 mmproj 视觉塔，加载即崩）**：

| 文件 | 大小 | 为什么不行 |
|---|---|---|
| `qwen3vl_32b_minimax_h3-Q2_K_M.gguf` | 13.10G | 缺视觉塔 → `ClipLoaderGGUF` 崩 |
| `qwen3-vl-32b-ultra-heretic-minimax-h3-q5_k_m.gguf` | 17.81G | 同上（eraiko 仓库实测确认） |
| `qwen3-vl-32b-ultra-heretic-minimax-h3-q6_k.gguf` | 20.64G | 同上 |
| `qwen3-vl-32b-ultra-heretic-minimax-h3-q8.gguf` | 26.74G | 同上 |

> ⚠️ **这是 2026-10-13 真机验证的结论，也是很多教程的过时点**：
> H3 的文本编码器是 Qwen3-VL（多模态），**GGUF 仓库里没有 mmproj 视觉塔**，
> `ClipLoaderGGUF` 会报 `TypeError: the JSON object must be str, bytes or bytearray, not NoneType`
> （日志先出现 `No mmproj file found for ...`）。GGUF 只适合**主模型**，编码器必须 safetensors。
> 低显存不是靠"换小编码器"解决，而是靠**卸载到内存**（`--lowvram` / RAM offload）。

来源：[ethanfel INT8 ConvRot](https://huggingface.co/ethanfel/Qwen3-VL-32B-Ultra-Heretic-H3-ComfyUI-INT8-ConvRot) ·
[Momoking NVFP4](https://huggingface.co/Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) ·
[Comfy-Org](https://huggingface.co/Comfy-Org/MiniMax-H3) ·
~~eraiko GGUF / unsloth GGUF~~（H3 不可用）

> ⚠️ 选型理由见下方[「真相」章节](#️-先读这个无审查文本编码器的真相)。
> 显存极紧？关注 **ClipProj** 路线：Qwen3-VL 4B/8B 编码器 + 学习到的投影，把编码器从 15.7GB 压到 **4.5GB**。

### ⑤ 必备配套

| 文件 | 大小 | 说明 |
|---|---|---|
| `minimax_h3_video_vae_fp16` | 5.21G | 视频 VAE（必需） |
| `minimax_h3_audio_vae_fp32` | 0.61G | **音频 VAE 必须 fp32**，用 fp16 会没声音 |
| `minimax_h3_fl2v_turbo_4step_v1.0` | 2.0G | 官方 4 步加速 LoRA |
| `minimax_h3_fl2v_turbo_8step_v1.0` | 2.0G | 官方 8 步加速 LoRA |
| [潜空间放大器](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) | — | 出片后放大到 1080P/2K |

---

## 🧰 加速全家桶（按收益排序）

| 手段 | 怎么做 | 收益 |
|---|---|---|
| **融合 Turbo 模型** | 直接用 21GB 融合模型 | 8 步 → **4 步**，速度翻倍 |
| **SLA 稀疏注意力** | 装 `ComfyUI-PlagueKind-Nodes`，用 `H3SLAAttention`（sparsity 0.9 / block 64） | 跳过 90% 注意力；作者称音轨更饱满。⚠️ **需驱动支持 cu130+**，否则报 `detect_k_anchor` 崩，改用「无SLA版」工作流 |
| **GGUF 量化（仅限主模型）** | 装 `ComfyUI-GGUF`，用 Q2~Q5 档加载 **diffusion model** | 让 8~16GB 卡也能跑。⚠️ **GGUF 文本编码器不可用**（缺 mmproj 视觉塔，必崩） |
| **NVFP4** | 50 系专用权重 | 权重减半 + 提速 |
| **FFN 分块** | KJNodes 的 `MiniMaxChunkFeedForward` | 低显存档再省一点（见 `低显存-*.json`） |
| **SageAttention** | `pip install sageattention` | 注意力加速 |
| **官方 Turbo LoRA** | 4 步 / 8 步 LoRA | 步数减半 |

> 社区还有一批**缓存类加速节点**（block cache / first-block cache / TE-Speed 等），最高 star 约 700，
> 属于"再榨一点"的手段，建议先跑通基线再装。

---

## 🔌 社区增强件（强烈推荐，装了就能用）

下面这几个是 H3 社区**最火的单点工具**（star 数远超同类的部署仓库）。它们解决的是同一个痛点：**H3 太慢**。
本仓库不强装它们，避免把"一键跑通"变成"一键装崩"，所以做成可选安装：

```bash
bash scripts/install_extras.sh              # 全部装
bash scripts/install_extras.sh spectrum     # 只装某一个
```

| 增强件 | 做什么 | 收益 | 代价 / 注意 |
|---|---|---|---|
| **[ComfyUI-Spectrum-MiniMax-H3](https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3)**（682★） | 用 Chebyshev 岭回归拟合 transformer 后的隐层特征，在"预测步"**整个跳过 transformer 计算** | **省 30~35% 时间**（20 步里实际只算 11~13 步）；免训练、零依赖 | ⚠️ **不是无损**：快速动作、眼睛/手指细节偶尔畸形，同 seed 也可能不同 → 关键出片前 A/B 对比。不要和 EasyCache/LazyCache 同分支用 |
| **[Comfyui_Minimax_h3_latent_Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler)**（707★） | 在 **24 通道 VAE latent 上直接放大**（1×~4×），跳过 H3 那个约 50 亿参数 VAE 的"解码→放大→重编码"往返 | 低分辨率出片 + 潜空间放大，**比直接生成高分辨率快得多**，还避免朴素插值的重影/双影 | ⚠️ **省时间不省显存**（精化仍跑目标分辨率）。模型约 691MB 放 `models/latent_upscale_models/` |
| [Kijai TAE（微型预览解码器）](https://github.com/Kijai/ComfyUI-KJNodes) | 快速预览解码，比 latent2rgb 快 | 预览省时间 | 只用于预览，别拿它出片 |
| 缓存类节点（block cache / first-block cache / TE-Speed） | 缓存中间结果跳过计算 | 再榨一点速度 | 与 Spectrum 冲突，二选一 |

**推荐组合**（按你的显存档）：

| 场景 | 组合 |
|---|---|
| **8~16GB** | 低分辨率（0.4MP）+ 4 步 Turbo + **Latent Upscaler 放大** ← 这条路线性价比最高 |
| **24GB+** | 0.6~0.98MP + 6~8 步 + **Spectrum**（有画质要求就关掉 A/B 一次） |
| 低显存但想要高清 | 480P 出片 → Latent Upscaler 2× → 轻步数精化 |

> **节点串联位置**（最容易接错的地方）：
> `H3 模型加载 → LoRA / 模型补丁 → MiniMax H3 Sigma Shift → **Spectrum** → Guider / Sampler`
> `低分辨率 H3 Latent → **Latent Upscaler** → 精化 / 再采样 → VAE Decode`

---

## 📁 工作流清单

**先分清要喂不喂图**：文生视频（只写提示词）／图生视频（喂首帧图）／参考图锁角色（喂参考图）。
完整对照见 **[docs/工作流对照表.md](docs/工作流对照表.md)**。

| 文件 | 类型 | 用途 |
|---|---|---|
| `MATLOWAI-01_reference_4step_sla.json` | **文生视频** | ⭐ 基线档，最快（0.7MP / 4 步） |
| `MATLOWAI-02_derope_4plus4_sla.json` | 文生视频 | 4+4 去绳索 + 运动平滑（慢但运镜更顺） |
| `MATLOWAI-03_derope_dyrope_pb3049_warm375.json` | 文生视频 | 上者 + DyRoPE + warm375 适配器 |
| `MATLOWAI-04_i2v_fl2v_4step_sla.json` | **图生视频** | ⭐ 主力，首帧图 → 视频；`last_frame` 再喂一张即首尾帧 |
| `01_官方-图生视频-i2v.json` | 图生视频 | Comfy-Org 官方模板，可作对照基线 |
| `MATLOWAI-05_ref2va_4step_sla.json` | **参考图锁角色** | ⭐ 锁人物 / 服装 / 画风（需换 ref2va 主模型） |
| `低显存-*.json`（3 个） | 各类型 | 加了 FFN 分块，**16GB 及以下用这套**；24GB+ 别用（反而更慢） |
| `MATLOWAI-01_文生视频_无SLA版.json` | **文生视频** | ⭐ **驱动 < cu130 就用这个**（SLA 节点已摘掉） |
| `MATLOWAI-04_i2v_无SLA版.json` | **图生视频** | ⭐ 主力档的无 SLA 版 |
| `MATLOWAI-05_ref2va_无SLA版.json` | **参考图锁角色** | 无 SLA 版 |
| `低显存-04_i2v_无SLA版.json` | 图生视频 | 低显存 **+** 无 SLA 双保险 |

> ⚠️ **三个已知坑（2026-10-13 真机验证，详见 [docs/真机踩坑与前置要求.md](docs/真机踩坑与前置要求.md)）**
> 1. **不要用 GGUF 文本编码器** —— 所有 H3 的 GGUF 编码器仓库都没有 mmproj 视觉塔，
>    `ClipLoaderGGUF` 会崩。必须用 safetensors + 官方 `CLIPLoader`（`download.py` 已改成默认下 safetensors）。
> 2. **`H3SLAAttention` 需要 cu130+ 驱动**，否则报 `CUDA driver version is insufficient` /
>    `detect_k_anchor kernel launch failed`。驱动偏旧时用上面的「**无SLA版**」工作流，即可正常出片（只是慢一些）。
> 3. **磁盘要留 ≥ 60GB** —— balanced 档模型实测约 **48.25GB**（主模型 21G + 编码器 24.6GiB + 两个 VAE + 两个 LoRA），
>    再加 ComfyUI 约 5GB。云主机"数据盘 50G"刚好不够：要么扩盘，要么把 models 软链到数据盘。

> 依赖节点：`ComfyUI-GGUF`（GGUF 加载）、`ComfyUI-PlagueKind-Nodes`（SLA）、
> `ComfyUI-MAINodes`（de-rope / DyRoPE / 音频）、`KJNodes`（FFN 分块）。
> `scripts/install.sh` 会全部装上。

---

## ⚠️ 先读这个：「无审查文本编码器」的真相

社区流传"把文本编码器换成 heretic/uncensored 版就能解锁内容"——**这个说法已被 Heretic 作者本人公开否认**。
（Heretic 是最主流的 LLM 去审查工具，社区发布了 5000+ 个无审查模型；作者的 PSA 帖在 r/StableDiffusion 拿到约 2450 赞。）

原因在于 **H3 的文本编码器根本不"说话"**：

| 它做的事 | 会不会触发审查 |
|---|---|
| 把你的提示词编码成条件张量 `[token数, 5120]` 交给 DiT | **不会**。它只做"文字→向量"，不生成任何回答，没有"拒答"这个环节 |
| 接上生成尾层当 LLM 用，做**提示词增强 / 改写** | **会**。这才是真正的生成阶段，越狱在这里才有意义 |

所以结论是：

- **只做条件编码**（CLIPLoader 指向哪个文件）→ 换 heretic 基本是**安慰剂**；最坏情况是因为条件偏离了训练分布，
  反而**降低提示词遵循度、引入伪影**。社区项目 ClipProj 实测：abilitated 编码器与官方编码器的条件张量余弦差仅 **0.0023（≈0.23%）**，就是噪声。
- **想真正放宽限制**，正确姿势是：用无审查 LLM 做**提示词改写 / 增强**，再把改写好的提示词交给官方编码器。
- 官方编码器还有个被忽略的优势：**它"懂得最多"**（32B 见过更多人物/场景/物体），而高度量化的小编码器会掉知识与专有名词能力。

> 本仓库仍提供社区 uncensored 权重的一键切换（你若在意，可以自己固定 seed 做 A/B 对比），
> 但**不把"越狱"当唯一卖点**——H3 在本地跑时本来就没有云端那层内容过滤机制，
> 真正的自由度来自"本地 + 你自己的提示词"，而不是那个文件名。
> 两条路线的详细对比见 [`docs/模型选择指南.md`](docs/模型选择指南.md)。

---

## ⚠️ 注意事项

1. **音频 VAE 必须 fp32**，用 fp16 会没声音或音画不同步
2. 16GB 及以下启动务必带 `--lowvram`
3. 融合模型（21GB）与官方模板的模型名不同，**工作流里要对应改选**
4. 单次最长约 15 秒（训练区间 124~362 帧，必须落在 `17k+5` 网格上）；更长用分段接力
5. **CFG 必须 1.0** —— H3 是蒸馏模型，无需 CFG，设大于 1 会崩
6. NVFP4 权重**仅限 Blackwell（RTX 50 系）**，40 系用 fp8 / INT8
7. **GGUF 只用于主模型** —— GGUF 文本编码器缺 mmproj 视觉塔、不可用；GGUF 主模型画质略低于 fp8/bf16，属正常权衡
8. 模型放 **NVMe 固态**，放机械盘 offload 速度会慢十倍
9. **磁盘留 ≥ 60GB** —— balanced 档实测约 48.25GB + ComfyUI 约 5GB；云主机数据盘偏小时，
   把 ComfyUI 装系统盘、`models` 软链到数据盘（命令见「快速开始」）
10. **云主机随时会被回收** —— 出片后立刻 scp 拉回本地并校验字节数，别把成片留在云上
11. **许可提醒**：MiniMax H3 Community License 有 "Applicable Territory"（排除部分地区）与商业营收门槛，
    使用前请阅读模型仓库里的 LICENSE 全文（详见 [NOTICE.md](NOTICE.md)）

## ❓ FAQ

**Q：8GB 真的能跑吗？**
能跑，但要用 Q2_K GGUF（6.7GB）+ 极限分层卸载 + 480P/5 秒，速度会慢（分钟级）。想要体面体验建议 12GB 起步、16GB 舒适。
社区还有人在 **4GB 笔记本**上跑通了（低分辨率约 12 分钟一条），所以 8GB 不是硬门槛，是"能舒服用"的门槛。

**Q：无审查版和原版差别在哪？**
只差文本编码器这一个文件，主模型完全相同。但要清楚一点：H3 在本地跑时，**两条路都不会在生成端"拒绝"你**——
编码器只把文字转成向量，不存在"拒答"这个动作。所以换 uncensored 编码器**不等于"解锁"**，更可能是白换
（原因见上面的「真相」小节）。真正决定"能不能生成、生成得好不好"的，是提示词写法和模型自身的能力上限。

**Q：4090 24GB 怎么配最舒服？**
融合模型 21GB + 无审查 INT8 编码器 26.4G（卸载）+ 4 步，768P/10 秒档很流畅；
驱动支持 cu130 就开 SLA，否则用「无SLA版」工作流。想更好画质换 fp8 / pruned_bf16 + 6~8 步。
（我们实测用的是 **4090-48G 魔改版**：0.6MP/4 步 **84 秒**、6 步 **117 秒**、0.98MP/6 步 **243 秒**；
24GB 卡因为要 offload，会明显更慢。）

**Q：我按老教程下了 GGUF 文本编码器，`ClipLoaderGGUF` 直接报错？**
这是**教程过时**，不是你的环境问题：H3 的文本编码器是 Qwen3-VL（多模态），
而所有 H3 的 GGUF 编码器仓库都**没放 mmproj 视觉塔**，构建不出 tokenizer → 必崩。
删掉那个 GGUF 文件，改用 safetensors 编码器 + 官方 `CLIPLoader`（`type` = `minimax`）即可。
详见 [docs/真机踩坑与前置要求.md](docs/真机踩坑与前置要求.md) 第二节。

**Q：远景人脸糊 / 细节有颗粒感 / ref2video 比 i2v 软，能调吗？**
**不能**。MiniMax 官方在 AMA 里确认这三项都出在 DiT 与训练阶段，是当前模型的**能力上限**——
加步数、升分辨率、换编码器都救不回来。可行的做法是：喂更高质量的参考图 + 让主体靠近镜头。

---

## 📚 详细文档

| 文档 | 内容 |
|---|---|
| [`docs/真机踩坑与前置要求.md`](docs/真机踩坑与前置要求.md) | ⭐ **先读这个**：开机自检 → 磁盘不够的三种解法 → GGUF 编码器为何不可用 → SLA 崩溃的完整因果链 → 已修的两个脚本 bug → 远程运维小坑 → 实测数据 |
| [`docs/教程-文生视频与图生视频.md`](docs/教程-文生视频与图生视频.md) | 从零到出片：环境自检 → 放模型 → 六节点核对表 → 三种玩法 → 提示词写法 → 参数速查 → 排障表 |
| [`docs/模型选择指南.md`](docs/模型选择指南.md) | 主模型 × 文本编码器 × 量化档三个自由度怎么组合，附「抄作业」组合表 |
| [`NOTICE.md`](NOTICE.md) | 所有第三方权重 / 节点 / 工作流的出处与许可 |

---

## 🔗 相关项目

| 项目 | 平台 | 说明 |
|---|---|---|
| **本项目**（N 卡） | [GitCode](https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored) ｜ [GitHub](https://github.com/zhenhanchen1-cyber/minimax-h3-nvidia-uncensored) | NVIDIA 显卡，8GB 显存起 |
| **姊妹项目**（昇腾） | [GitCode](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored) ｜ [GitHub](https://github.com/zhenhanchen1-cyber/minimax-h3-ascend) | 华为昇腾 910B/910C，真机实测 + 免费算力路线 |

---

## ⭐ 如果对你有帮助

**点个 Star** 是最实在的支持 —— 它能让更多"卡在装环境那一步"的人搜到这个仓库。
有实测数据、更好的工作流、或踩到新坑，欢迎开 [Issue](https://github.com/zhenhanchen1-cyber/minimax-h3-nvidia-uncensored/issues) / PR。

---

## English

**MiniMax-H3 local deployment on NVIDIA GPUs — from 8GB VRAM.**

Run MiniMax-H3 (the omni-modal video model behind Hailuo 3.0) locally with ComfyUI:
text-to-video, image-to-video, reference-locked characters, native synchronized stereo audio, fully offline.

- **One-command setup**: `bash scripts/install.sh` installs ComfyUI + all required custom nodes
  (GGUF / SLA / MAINodes / KJNodes); `bash scripts/download.sh` auto-picks the right model tier for your VRAM.
- **Runs from 8GB VRAM**: GGUF Q2_K diffusion model (6.7GB) + layered offload; 16GB is comfortable
  (community-measured **11 GiB peak / 65 s** for a 4-step generation); 24GB (RTX 4090) is fast.
- **15+ diffusion checkpoints, safetensors-only text encoders** (NVFP4 / INT8), 13 ready-to-use ComfyUI workflows
  (including **4 SLA-free variants** for drivers older than cu130).
- **Speed stack on CUDA**: fused 4-step Turbo model, SLA sparse attention, NVFP4 (Blackwell), SageAttention,
  GGUF offload, FFN chunking.
- **Verified on real hardware (RTX 4090 48GB, 2026-10-13)**: 0.4MP/4 steps **54 s**, 0.6MP/4 steps **84 s**,
  0.6MP/6 steps **117 s**, 0.98MP/6 steps **243 s** — see `docs/真机踩坑与前置要求.md`.
- **Two hard prerequisites**: **≥ 60GB free disk** (the balanced tier is 48.25GB) and a **safetensors text
  encoder** — every GGUF text-encoder repo for H3 lacks the mmproj vision tower, so `ClipLoaderGGUF` crashes.
- **Sister project**: Huawei Ascend NPU (910B/910C) deployment — see
  [minimax-h3-ascend-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored).

> ⚠️ **About "uncensored" text encoders**: swapping in an abliterated (heretic) text encoder does **not**
> decensor MiniMax-H3. The text encoder only produces a conditioning tensor `[tokens, 5120]`; it never
> generates text, so there is no refusal step to bypass. The creator of Heretic has publicly advised against
> this swap (measured cosine gap vs. the stock encoder: **0.0023**). See the Chinese section above for details.

Model weights are **not** included — the scripts download them from public repositories
([Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3), [unsloth](https://huggingface.co/unsloth/MiniMax-H3-GGUF),
[MATLOWAI](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot)). Check the
MiniMax H3 Community License (it defines an "Applicable Territory" and a commercial revenue cap) before use.

**License**: MIT for scripts and docs — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

---

## 许可与致谢

本仓库脚本与文档采用 MIT。你可以自由使用、修改、二次分发 ——
**只要求一件事：保留原作者署名与本仓库链接**（这也是 MIT 的条款）。
如果你做了改进，欢迎开 PR 回流，比另起一个副本更有价值。

模型权重与第三方节点版权归各自作者，详见 [NOTICE.md](NOTICE.md)。
特别感谢：[Comfy-Org](https://huggingface.co/Comfy-Org/MiniMax-H3)、[unsloth](https://huggingface.co/unsloth/MiniMax-H3-GGUF)、
[MATLOWAI](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot)、[eraiko](https://huggingface.co/eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF)、
[Momoking](https://huggingface.co/Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)、[ComfyUI](https://github.com/Comfy-Org/ComfyUI)。
