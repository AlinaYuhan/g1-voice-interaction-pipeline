# 可复现性指南

[中文](REPRODUCIBILITY.zh-CN.md) | [English](REPRODUCIBILITY.md)

本仓库旨在成为公开、可从源代码复现的项目，而不是克隆后即可运行的机器人镜像。请先阅读 [README.zh-CN.md](README.zh-CN.md)，再按照[环境安装](docs/SETUP.zh-CN.md)和[配置说明](docs/CONFIGURATION.zh-CN.md)操作。

## Git 中包含的内容

- 核心编排、会话控制、监控服务端/UI 和测试。
- `deps/SURF2026_VoiceModule-main/` 下的 SURF 语音运行时源代码。
- 当前既有路径所需的 Unitree 适配器/内置 SDK 源代码。
- 可选的 XJTLU RAG 源代码，以及获准公开的 `xjtlu_knowledge.db` 和 `rag_index.db` 数据库。
- 安全的默认配置和本地配置模板。
- 研究/实验性源代码和波束成形可复现性参考材料。

## 每台机器上需重新创建的内容

- `config/local.env`、API 密钥、IP 地址、网络接口和 Python 路径。
- Python/conda 环境和 ROS 2 Jazzy 安装。
- 唤醒词 ONNX 资产、ModelScope ASR 和 Hugging Face 声纹缓存。
- 仅供 RAG 使用的可选 Ollama 和 `nomic-embed-text`。
- 仅供旧版/本地后端使用的可选本地 Qwen 权重。
- Unitree C++ 构建输出和 Jetson 原生库。
- 日志、运行时状态、聊天记忆、生成的 TTS 和缓存。

默认 DeepSeek + Jetson 中继路径为：

```text
LLM_REPLY_BACKEND=deepseek
UNITREE_BACKEND=relay
```

此路径不需要可选 RAG/Ollama 服务或本地 Qwen 权重。

## 复现步骤

```bash
./scripts/setup_conda_envs.sh
cp config/local.env.example config/local.env
# 编辑 config/local.env，并安装/下载文档所述的外部资产
./scripts/check_pipeline.sh
./scripts/check_robot_relay.sh
./scripts/run_pipeline.sh --mode wake
```

另行启动操作界面：

```bash
./scripts/run_pipeline_monitor.sh              # http://127.0.0.1:8765/
./scripts/run_pipeline_monitor.sh --port 8766  # 常用机器人测试端口
```

## 证据与限制

自动化测试和 `check_pipeline.sh` 会验证源代码/配置契约，但不会验证目标机器人的 USB 麦克风、物理网络、Jetson 库、中继可达性、扬声器、灯光或动作安全性。每项可复现性声明都应记录本地环境、模型修订版本/校验值和硬件测试结果。

## 发布说明

- 第一方项目代码采用 Apache-2.0 许可；内置的第三方材料保留其各自条款。
- `research/beamforming/teacher_reference_20260630/` 中的教师参考脚本、滤波器和录音，作为固定波束成形路径的可复现性参考材料包含在仓库中；复现该模式时请保持此目录完整。
- 内置的 Unitree Python SDK 现已包含与其匹配的 BSD-3-Clause 声明，但尚未找回其确切的上游基础修订版本；请按照 [THIRD_PARTY_LICENSES.zh-CN.md](THIRD_PARTY_LICENSES.zh-CN.md) 的说明，将其视为经过修改的内置副本。

正式发布前，请解决或记录所有剩余的来源说明。请使用 [PACKAGING.zh-CN.md](PACKAGING.zh-CN.md) 中所述的纯源代码构建器；它会有意排除本地模型、机密信息、运行时状态和已编译输出。
