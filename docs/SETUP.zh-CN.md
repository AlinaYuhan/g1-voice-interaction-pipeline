# 环境安装

[English](SETUP.md) | [中文](SETUP.zh-CN.md)

> 本项目当前采用本机/WSL2 安装和 `config/local.env`，不以 Docker
> 作为真机部署入口。默认 DeepSeek 链路不需要 Ollama 或本地 Qwen 权重；唤醒词、
> ASR 和声纹模型需按下文在本机准备。

## 1. 支持的部署方式

经过验证的架构需要：

- 安装了 ROS 2 Jazzy（路径为 `/opt/ros/jazzy`）的 Ubuntu 或 WSL2；
- 两个 Python 3.12 conda 环境（`llm` 和 `voice312`）；
- DeepSeek 兼容 API 的密钥；
- 主机能够访问 Jetson/机器人侧中继；
- 能够通过网络访问 G1 及其外置麦克风链路。

Docker 不是主要部署方式。ROS 2 DDS 发现、USB/音频设备、WSL 网络、SSH 部署以及
Jetson 的原生 Unitree 库都需要与主机集成。容器仍然需要特权设备和网络配置，因此
目前的可复现方案是在本机安装，并搭配被 Git 忽略的 `config/local.env`。

## 2. 系统软件包和 ROS 2

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake curl ffmpeg git \
  portaudio19-dev python3-dev python3-pip
```

按照 ROS 官方文档安装 ROS 2 Jazzy，并验证：

```bash
test -f /opt/ros/jazzy/setup.bash
```

## 3. Python 环境

在仓库根目录运行：

```bash
./scripts/setup_conda_envs.sh
```

该脚本会创建采用 Python 3.12 的 `llm` 和 `voice312` 环境，并安装
`requirements-llm.txt` 和 `requirements-voice.txt`。如果 PyTorch 需要与机器匹配的
CPU/CUDA wheel，请先在相应环境中安装该 wheel，再安装其余依赖。

## 4. 外部模型资产

下载的模型文件和缓存会被特意排除在 Git 之外。

### 唤醒词 KWS（语音唤醒必需）

运行时要求 `deps/SURF2026_VoiceModule-main/models/kws/` 下存在以下文件：

```text
encoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx
decoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx
joiner-epoch-12-avg-2-chunk-16-left-64.int8.onnx
tokens.txt
keywords.txt
```

通过 [THIRD_PARTY_LICENSES.zh-CN.md](../THIRD_PARTY_LICENSES.zh-CN.md) 中链接的
sherpa-onnx 官方预训练 KWS 文档获取匹配的
`sherpa-onnx-kws-zipformer-wenetspeech-3.3M-2024-01-01` 资产。仓库不再分发 ONNX
权重或模型的 `tokens.txt`；请从同一份官方模型归档复制两者，确保词表匹配。
项目专用的 `keywords.txt` 仍由仓库跟踪。用以下命令验证完整的模型目录：

```bash
deps/SURF2026_VoiceModule-main/scripts/check_project.sh
```

### ASR（必需）

配置的 ModelScope 模型标识符/路径为：

```text
iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
${HOME}/.cache/modelscope/hub/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
```

请在目标机器上使用 ModelScope/FunASR 获取该模型。官方模型页面链接见
[THIRD_PARTY_LICENSES.zh-CN.md](../THIRD_PARTY_LICENSES.zh-CN.md)。如果缓存位于其他位置，
可用 `VOICE_ASR_MODEL` 覆盖路径。

### 声纹（启用说话人识别时必需）

配置的 Hugging Face 模型 ID 为：

```text
pyannote/wespeaker-voxceleb-resnet34-LM
```

让 pyannote/Hugging Face 将模型下载到本地缓存，或将 `VOICE_VOICEPRINT_MODEL`
指向已有的本地副本。模型条款和官方页面列于
[THIRD_PARTY_LICENSES.zh-CN.md](../THIRD_PARTY_LICENSES.zh-CN.md)。

### 默认后端不需要的资产

- 仅当 `LLM_REPLY_BACKEND=rag` 时才需要 Ollama 和 `nomic-embed-text`。
- 只有旧版/本地后端会使用 `deps/Qwen3.5-0.8B/model/`。
- 直接使用 DeepSeek 时既不需要 Ollama，也不需要本地 Qwen 权重。

## 5. 本地配置

```bash
cp config/local.env.example config/local.env
```

填写 API 密钥、Python 路径以及机器专用的机器人/中继地址。参阅
[配置说明](CONFIGURATION.zh-CN.md)。切勿提交 `config/local.env`。

## 6. 构建/检查机器人原生依赖

C++ 动作示例是本地生成的构建产物：

```bash
cd deps/unitree_g1_action_classifier_package/unitree_sdk2
mkdir -p build && cd build
cmake ..
make -j
```

预期二进制文件为
`deps/unitree_g1_action_classifier_package/unitree_sdk2/build/bin/g1_arm_action_example`。
Jetson 中继还需要机器本地安装的 Unitree/CycloneDDS；参阅
[G1 中继与操作](G1_RELAY.zh-CN.md)。

## 7. 验证并启动

```bash
./scripts/check_pipeline.sh
./scripts/check_robot_relay.sh
./scripts/run_pipeline.sh --mode wake
```

只有回复后端确实为 `rag` 时，`check_pipeline.sh` 才会验证 RAG/Ollama 资产。
硬件就绪情况仍需在目标机器上验证。
