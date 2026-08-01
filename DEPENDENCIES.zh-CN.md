# 依赖清单

[中文](DEPENDENCIES.zh-CN.md) | [English](DEPENDENCIES.md)

安装说明请参阅[环境安装](docs/SETUP.zh-CN.md)，许可证及状态详情请参阅 [THIRD_PARTY_LICENSES.zh-CN.md](THIRD_PARTY_LICENSES.zh-CN.md)。

## 仓库目录角色

| 路径 | 分类 | 当前角色 |
| --- | --- | --- |
| `deps/SURF2026_VoiceModule-main/` | 核心运行时源代码 | 唤醒词、VAD、ASR、说话人上下文和麦克风输入。 |
| `deps/qwen_ros_node_edg_tts/` | 兼容层 + 内置第三方代码 | 保留旧名称的软件包，仍提供 Unitree Python SDK 适配器；旧版 Qwen 代码不是默认回复路径。 |
| `deps/unitree_g1_action_classifier_package/` | 适配器 + 内置第三方代码 | G1 动作分类/运行器以及 Unitree SDK2 C++ 源代码。 |
| `xjtlu-rag-system/` | 可选 | XJTLU 检索服务和获准公开的小型数据库；默认禁用。 |
| `research/` | 研究/参考 | 实验性源代码和可复现性参考材料；默认对话路径不需要。 |
| `docs/archive/` | 历史资料 | 早期记录，并非当前运行时事实依据。 |

## Python 环境

- `requirements-llm.txt`：供 `llm` Python 3.12 环境使用的主编排、HTTP、TTS、ML/动作以及 Unitree Python 适配器依赖。
- `requirements-voice.txt`：供 `voice312` Python 3.12 环境使用的音频、ASR、唤醒词、VAD 和声纹依赖。

默认外部解释器路径：

```text
${HOME}/miniconda3/envs/llm/bin/python
${HOME}/miniconda3/envs/voice312/bin/python
```

ROS 2 Python 软件包由 ROS 2 Jazzy 提供，而不是由这些 pip 文件提供。请根据需要安装适配目标机器的 PyTorch CPU/CUDA wheel。

## 原生 DDS/Unitree 依赖

```text
deps/qwen_ros_node_edg_tts/third_party/unitree_sdk2_python/
    Unitree Python 适配器；声明 cyclonedds==0.10.2

deps/unitree_g1_action_classifier_package/unitree_sdk2/
    Unitree SDK2 C++；随附自身的嵌套第三方许可证树
```

生成的 CMake 输出和 Jetson 原生库不受版本控制。请为目标架构构建或安装它们。

## 外部/安装时下载的资产

| 资产 | 需要条件 |
| --- | --- |
| sherpa-onnx KWS ONNX 文件 | 使用语音唤醒时。 |
| ModelScope Paraformer ASR | 使用语音 ASR 时。 |
| Hugging Face WeSpeaker 缓存 | 启用说话人识别时。 |
| Ollama + `nomic-embed-text` | 仅当 `LLM_REPLY_BACKEND=rag` 时。 |
| 本地 Qwen 模型 | 仅当 `LLM_REPLY_BACKEND=local` 时。 |

默认 `deepseek` 回复后端不需要 Ollama 或本地 Qwen。下载的资产、环境、构建输出、运行时状态和 `config/local.env` 均有意排除在 Git 和公开发布包之外。
