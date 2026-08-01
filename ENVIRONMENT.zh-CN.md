# 环境安装

[中文](ENVIRONMENT.zh-CN.md) | [English](ENVIRONMENT.md)

此兼容性入口指向持续维护的安装文档：

- [环境安装](docs/SETUP.zh-CN.md)
- [配置说明](docs/CONFIGURATION.zh-CN.md)
- [G1 中继与操作](docs/G1_RELAY.zh-CN.md)
- [故障排查](docs/TROUBLESHOOTING.zh-CN.md)

当前基线：

```text
Ubuntu 或 WSL2
ROS 2 Jazzy (/opt/ros/jazzy/setup.bash)
Python 3.12：llm + voice312 conda 环境
LLM_REPLY_BACKEND=deepseek
UNITREE_BACKEND=relay
```

全新安装可从以下命令开始：

```bash
# 等效的手动环境创建命令：
conda create -n llm python=3.12 -y
conda create -n voice312 python=3.12 -y

./scripts/setup_conda_envs.sh
cp config/local.env.example config/local.env
./scripts/check_pipeline.sh
```

默认解释器路径为：

```text
${HOME}/miniconda3/envs/llm/bin/python
${HOME}/miniconda3/envs/voice312/bin/python
```

`config/local.env` 已被 Git 忽略，必须包含目标机器的 API 密钥、Python 路径、机器人麦克风地址、Jetson 中继地址及所有必需的网络接口。公开默认配置有意不包含任何机器特定的 IP 或接口。

DeepSeek 是默认回复后端，不需要 Ollama 或本地 Qwen 权重。仅可选 RAG 后端需要 Ollama 和 `nomic-embed-text`。唤醒词 ONNX 文件、ModelScope ASR、Hugging Face 声纹缓存、已编译的 Unitree 产物、日志以及本地环境均不存储在 Git 中。

目前不建议使用 Docker 部署机器人，因为 ROS 2 DDS、WSL 网络、USB/音频设备、SSH 和 Jetson 原生库都需要针对宿主机进行集成。受支持的方式是本地安装并配合 `config/local.env`。
