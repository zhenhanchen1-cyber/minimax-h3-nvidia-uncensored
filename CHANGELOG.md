# 更新记录

> 这个仓库是**活的** —— 每次新增模型档位、每个社区新工具、每个速度实测都会记在这里。
> 如果你看到某个仓库内容和这里一模一样但**没有后续更新**，那大概率是搬运的死仓库。

## 2026-10-13

- **新增 [`docs/真机踩坑与前置要求.md`](docs/真机踩坑与前置要求.md)**（本次实测算总账）：
  开机 30 秒自检清单 → 磁盘不够的三种解法 → GGUF 编码器为何不可用 → SLA 崩溃的完整因果链 →
  两个已修的脚本 bug → 远程运维小坑 → 实测数据与读数须知。
- **口径修正（重要）：文本编码器只能 safetensors**。所有 H3 的 GGUF 文本编码器仓库（eraiko / unsloth）
  都缺 **mmproj 视觉塔**，`ClipLoaderGGUF` 必崩（`TypeError: the JSON object must be str...`，
  日志先出现 `No mmproj file found`）。README 首屏决策表、模型全家桶、`docs/模型选择指南.md`、
  `docs/教程-文生视频与图生视频.md`、`NOTICE.md` 全部改口径；GGUF 保留为**主模型**可用路线。
- **修一个真 bug**：`download.py` 的 minimal 档同时下了 GGUF 编码器（13.1G，装不上）和
  INT8 safetensors 编码器（26.4G）—— 白下 13GB。已删除 GGUF 编码器条目。
- **前置条件写进 README**：① 磁盘可用 **≥ 60GB**（balanced 档实测 **48.25GB** + ComfyUI 约 5GB；
  云主机"数据盘 50G"刚好不够，给出 `COMFY_HOME` + `models` 软链的解法）；
  ② **SLA 需要 driver cu130+**，否则用新增的 4 套「无SLA版」工作流。
- **`.gitignore` 补齐**（此前没有，`scripts/__pycache__/*.pyc` 被误入库，本次一并清理）。
- 文档一致性：工作流清单 9 → **13 套**（含 4 套无SLA版）；教程与工作流对照表补上"驱动不够用哪套"的对应关系。

## 2026-10-12

- **社区增强件章节** + `scripts/install_extras.sh`：可选安装
  ComfyUI-Spectrum-MiniMax-H3（省 30~35% 时间，非无损）与
  Comfyui_Minimax_h3_latent_Upscaler（潜空间放大，跳过 VAE 往返）；
  含收益 / 风险 / 节点串联位置 / 按显存的推荐组合。
  刻意**不放进 `install.sh` 默认流程** —— 近似加速会改变出片结果，不该破坏"一键跑通"。
- **Issue 模板**：实测数据提交 / 报错求助 / 文档引导。
- **README 流量优化**：首屏「30 秒决策表」+ 徽章 + 目录 + 英文摘要 + 姊妹项目互链 + Star CTA。
- **口径修正（重要）**：新增「无审查文本编码器的真相」——
  Heretic 作者本人公开劝阻把 heretic 模型当 H3 文本编码器（PSA 约 2450 赞）；
  社区 ClipProj 实测条件张量余弦差仅 **0.0023（≈0.23%）**，基本是噪声。
  **修掉一个真 bug**：8GB（minimal）档所谓"无审查编码器"其实指向官方 Q2_K_M ——
  因为不存在小体积无审查编码器（最小 15.7G 仅 Blackwell）。
- **新增**：ClipProj 低显存路线（15.7G → 4.5G）、4GB 笔记本实测数据、
  官方 AMA 确认的能力上限（远景糊脸 / 细节颗粒感 / ref2v 偏软，都在 DiT 里，调参救不回来）。

## 2026-10-12（初版）

- 初始版本：README（三大看点 / N 卡 vs 昇腾对照 / 显存选型速查 / 15+ 模型全家桶）
  + `docs/模型选择指南.md` + `docs/教程-文生视频与图生视频.md`
  + `install.sh`（一键装 ComfyUI + GGUF/SLA/MAINodes/KJNodes）
  + `download.py/sh`（按显存自动选档、32 路分片并行、断点续传）
  + 9 套工作流（MATLOWAI 4 步 SLA 全套 + 官方 i2v + 低显存 FFN 分块版）。
