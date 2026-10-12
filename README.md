# MiniMax-H3 · N 卡本地部署（8GB 显存起 · 无审查版）

> 在 **NVIDIA 显卡**上用 ComfyUI 本地跑 **MiniMax-H3** 全模态视频生成：文生视频 / 图生视频 / 参考图锁角色，
> **原生音画同步**，文本编码器可选 **无审查（Uncensored）版本**，全程本地、无云端限制、免费无限量。
>
> **最低 8GB 显存可跑，16GB 舒适，24GB（4090）畅快。**

## 🔥 三大看点

1. **低显存门槛** —— 靠 **GGUF 量化（最小 6.7GB）+ 融合加速模型（21GB）+ FFN 分块卸载**，
   实测 **16GB 卡上 4 步生成仅占 11 GiB / 65 秒**；8GB 卡配合极限卸载同样能跑（见下方显存表）
2. **无审查生态权重可选** —— 文本编码器提供 **GGUF / NVFP4 / INT8** 三种格式的社区 uncensored 版本，
   一键切换，也提供官方原版（**但请先读下面的「⚠️ 关于"无审查"的真相」，它没有传说中那么神**）
3. **模型全家桶自选** —— 从 6.7GB 的 Q2_K 到 66GB 的 BF16，从 4 步蒸馏到 25 步精修，
   **15+ 个主模型 / 6 种文本编码器** 全列出，你按自己显卡挑

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
> 但**不再把"越狱"当唯一卖点**——H3 在本地跑时本来就没有云端那层内容过滤机制，
> 真正的自由度来自"本地 + 你自己的提示词"，而不是那个文件名。
> 两条路线的详细对比见 [`docs/模型选择指南.md`](docs/模型选择指南.md)。

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
| 昇腾 2×910B（本仓库姊妹项目实测） | 官方 INT8 + 8 步 | 12 秒片约 **11 分钟** |

> 上表 N 卡数据来自 [MATLOWAI/minimax-h3-fused-turbo-int8-convrot](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot) 的公开实测；
> 昇腾数据来自姊妹项目 [minimax-h3-ascend-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored) 的实测。
> 结论：**达到相近成片，N 卡所需算力约为昇腾的 1/5 ~ 1/8**。

## 🎯 显存选型速查（先看这张表）

| 你的显存 | 主模型推荐 | 文本编码器推荐 | 分辨率/时长 | 预期 |
|---|---|---|---|---|
| **8GB** | GGUF Q2_K（6.7G） | GGUF Q2_K_M（13.1G，分层卸载） | 480P / 5s | ⚠️ 能跑，慢（靠极限卸载） |
| **12GB** | GGUF Q3_K（8.8G） | GGUF Q2~Q3（卸载） | 480P / 5s | ✅ 可用 |
| **16GB** | 融合模型 21GB 或 GGUF Q4_K（11.4G） | GGUF Q4 / NVFP4（50系） | 576P~768P / 5~10s | ✅ **11 GiB / 65 秒**（实测） |
| **24GB（4090）** | 融合模型 21GB / fp8（21G）/ GGUF Q5 | TE Q4~Q5 GGUF | 768P / 10s | ✅ 畅快 |
| **32GB（5090）** | fp8 **或 NVFP4** / pruned_bf16（40G 需卸载） | **NVFP4 无审查（15.7G）** | 768P / 10~15s | ✅ 更快 |
| **48GB+** | 完整 BF16 / fp8 全精度 | Q8 GGUF 或 INT8 | 768P~1080P | ✅ 满血 |

> 文本编码器是低显存的最大瓶颈（Qwen3-VL-32B 即使 Q5 也要 17.8GB）——
> 解决办法是 **GGUF 分层加载**（ComfyUI-GGUF 节点）或干脆用 **NVFP4**（50 系仅 15.7GB）。

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

> 另有 [Abiray/MiniMax-H3-Pruned-GGUF](https://huggingface.co/Abiray/MiniMax-H3-Pruned-GGUF) 的 Q3~Q6 系列可作备选。

### ④ 文本编码器（决定审查）

| 文件 | 大小 | 审查 | 适用 |
|---|---|---|---|
| `qwen3-vl-32b-ultra-heretic-minimax-h3-q5_k_m.gguf` | 17.81G | **无审查** 🔥 | 24GB+ |
| `qwen3-vl-32b-ultra-heretic-minimax-h3-q6_k.gguf` | 20.64G | **无审查** 🔥 | 32GB+ |
| `qwen3-vl-32b-ultra-heretic-minimax-h3-q8.gguf` | 26.74G | **无审查** 🔥 | 48GB+ |
| `qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors` | **15.68G** | **无审查** 🔥 | **仅 Blackwell（50 系）** |
| `qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot` | 26.36G | **无审查** 🔥 | INT8 路线 |
| `qwen3vl_32b_minimax_h3-Q2_K_M.gguf` | 13.10G | 官方有审查 | 低显存保底 |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 15.69G | 官方有审查 | 50 系 |
| `qwen3vl_32b_minimax_h3_int8_convrot` | 27.14G | 官方有审查 | 通用 |

来源：[eraiko 无审查 GGUF](https://huggingface.co/eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF) ·
[Momoking 无审查 NVFP4](https://huggingface.co/Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) ·
[unsloth GGUF](https://huggingface.co/unsloth/MiniMax-H3-GGUF) ·
[Comfy-Org](https://huggingface.co/Comfy-Org/MiniMax-H3)

### ⑤ 必备配套

| 文件 | 大小 | 说明 |
|---|---|---|
| `minimax_h3_video_vae_fp16` | 5.21G | 视频 VAE（必需） |
| `minimax_h3_audio_vae_fp32` | 0.61G | **音频 VAE 必须 fp32**，用 fp16 会没声音 |
| `minimax_h3_fl2v_turbo_4step_v1.0` | 2.0G | 官方 4 步加速 LoRA |
| `minimax_h3_fl2v_turbo_8step_v1.0` | 2.0G | 官方 8 步加速 LoRA |
| [潜空间放大器](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) | — | 出片后放大到 1080P/2K |

## 🚀 快速开始

```bash
git clone <本仓库地址> minimax-h3-nvidia-uncensored
cd minimax-h3-nvidia-uncensored
bash scripts/install.sh        # ① 装 ComfyUI + 必备节点（GGUF/SLA/MAINodes/KJNodes）
bash scripts/download.sh       # ② 按显存自动选档下载（会先问你是几 GB 的卡）
# ③ 启动
cd ~/ComfyUI && python main.py --listen        # 24GB+ 用这个
cd ~/ComfyUI && python main.py --listen --lowvram   # 16GB 及以下加 --lowvram
```

浏览器打开 `http://127.0.0.1:8188`，从 `workflows/` 导入对应工作流即可。

## 🎬 三种玩法

| 玩法 | 用什么 | 说明 |
|---|---|---|
| **文生视频（T2V）** | `MATLOWAI-01_reference_4step_sla.json` | 只给提示词，直接出片 |
| **图生视频（I2V / 首尾帧）** | `01_官方-图生视频-i2v.json` 或 `MATLOWAI-04_i2v_fl2v_4step_sla.json` | 给一张首帧图（可再加尾帧做插值），让画面动起来 |
| **参考图锁角色（Ref2VA）** | `MATLOWAI-05_ref2va_4step_sla.json` | 喂一张/多张参考图，锁住人物、服装、画风 |

**九宫格分镜玩法**：把 3×3 分镜图整张喂给 I2V 工作流，配合分镜脚本提示词，
一次生成一段按顺序推进的连续剧情（详见 `docs/教程-文生视频与图生视频.md`）。

## 🧰 加速全家桶（按收益排序）

| 手段 | 怎么做 | 收益 |
|---|---|---|
| **融合 Turbo 模型** | 直接用 21GB 融合模型 | 8 步 → **4 步**，速度翻倍 |
| **SLA 稀疏注意力** | 装 `ComfyUI-PlagueKind-Nodes-only-sparse`，用 `H3SLAAttention`（sparsity 0.9 / block 64） | 跳过 90% 注意力；作者称音轨更饱满 |
| **GGUF 量化** | 装 `ComfyUI-GGUF`，用 Q2~Q5 档 | 让 8~16GB 卡也能跑 |
| **NVFP4** | 50 系专用权重 | 权重减半 + 提速 |
| **FFN 分块** | KJNodes 的 `MiniMaxChunkFeedForward` | 低显存档再省一点（见 `低显存-*.json`） |
| **SageAttention** | `pip install sageattention` | 注意力加速 |
| **官方 Turbo LoRA** | 4 步 / 8 步 LoRA | 步数减半 |

## 📁 工作流清单

| 文件 | 用途 |
|---|---|
| `01_官方-图生视频-i2v.json` | Comfy-Org 官方图生视频模板（九宫格分镜已内置提示词） |
| `MATLOWAI-01_reference_4step_sla.json` | ⭐ 文生/参考，4 步 + SLA（**最快**） |
| `MATLOWAI-02_derope_4plus4_sla.json` | 4+4 去绳索 + 运动平滑（慢但运镜更顺） |
| `MATLOWAI-03_derope_dyrope_pb3049_warm375.json` | 上者 + DyRoPE + warm375 适配器 |
| `MATLOWAI-04_i2v_fl2v_4step_sla.json` | ⭐ 图生视频 4 步（实测 107 帧 @1152×640 仅 25 秒） |
| `MATLOWAI-05_ref2va_4step_sla.json` | ⭐ 参考图锁角色 4 步 |
| `低显存-*.json`（3 个） | 加了 FFN 分块的低显存版，**16GB 及以下用这套** |

> 依赖节点：`ComfyUI-GGUF`（GGUF 加载）、`ComfyUI-PlagueKind-Nodes-only-sparse`（SLA）、
> `ComfyUI-MAINodes`（de-rope / DyRoPE / 音频）、`KJNodes`（FFN 分块）。
> `scripts/install.sh` 会全部装上。

## ⚠️ 注意事项

1. **音频 VAE 必须 fp32**，用 fp16 会没声音或音画不同步
2. 16GB 及以下启动务必带 `--lowvram`
3. 融合模型（21GB）与官方模板的模型名不同，**工作流里要对应改选**
4. 单次最长约 15 秒（训练区间 124~362 帧）；更长用分段接力
5. NVFP4 权重**仅限 Blackwell（RTX 50 系）**，40 系用 fp8 / GGUF
6. GGUF 出片画质略低于 fp8/bf16，属正常权衡

## ❓ FAQ

**Q：8GB 真的能跑吗？**
能跑，但要用 Q2_K GGUF（6.7GB）+ 极限分层卸载 + 480P/5 秒，速度会慢（分钟级）。想要体面体验建议 12GB 起步、16GB 舒适。

**Q：无审查版和原版差别在哪？**
只差文本编码器这一个文件，主模型完全相同。但要清楚一点：H3 在本地跑时，**两条路都不会在生成端"拒绝"你**——
编码器只把文字转成向量，不存在"拒答"这个动作。所以换 uncensored 编码器**不等于"解锁"**，更可能是白换
（原因见上面的「真相」小节）。真正决定"能不能生成、生成得好不好"的，是提示词写法和模型自身的能力上限。

**Q：4090 24GB 怎么配最舒服？**
融合模型 21GB + TE Q4_K_M GGUF（19.8G，卸载）+ 4 步 + SLA，768P/10 秒很流畅；想更好画质换 fp8 + Q5。

## 许可与致谢

**姊妹项目**：[MiniMax-H3 · 昇腾 NPU 本地部署](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored)
—— 同一套模型的国产算力路线（910B/910C），含多卡/低显存档与实测数据，可与本仓库互相参照。

本仓库脚本与文档采用 MIT。模型权重与第三方节点版权归各自作者，详见 [NOTICE.md](NOTICE.md)。
特别感谢：[Comfy-Org](https://huggingface.co/Comfy-Org/MiniMax-H3)、[unsloth](https://huggingface.co/unsloth/MiniMax-H3-GGUF)、
[MATLOWAI](https://huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot)、[eraiko](https://huggingface.co/eraiko/Qwen3-VL-32B-Ultra-Heretic-Minimax-H3-GGUF)、
[Momoking](https://huggingface.co/Momoking/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)、[ComfyUI](https://github.com/Comfy-Org/ComfyUI)。
