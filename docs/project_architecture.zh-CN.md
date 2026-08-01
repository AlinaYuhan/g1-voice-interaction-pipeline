# 当前项目架构

[English](project_architecture.md) | [中文](project_architecture.zh-CN.md)

> **当前事实来源（2026-07-31）。** 本文档描述正在使用的 DeepSeek + Jetson 中继部署。
> 旧版架构说明仅保留在 [`docs/archive/`](archive/README.md) 下。
>
> **摘要：** 当前默认主链是 SURF 语音感知、DeepSeek 直连回复、Edge TTS
> 和 Jetson 机器人中继。XJTLU RAG 是保留的可选实验后端，不是默认主链。

## 系统边界

```text
机器人侧                                  主机 / WSL2

G1 外置麦克风 -- UDP 音频 ---> SURF 语音运行时
                                          | 唤醒 / VAD / ASR / 说话人
                                          v
                                     surf_ros_bridge.py
                                          | ROS 2 /audio_msg + 上下文话题
                                          v
                                   llm_surf_context_node.py
                                          | HTTP /infer, /tts
                                          v
                                       llm_server.py
                                          | 直接调用 DeepSeek 兼容 API
                                          v
                                    unitree_audio_player.py
                                          | 基于 TCP 的中继协议
                                          v
Jetson 中继 ------------------------- robot_relay/jetson_robot_relay.py
  | Unitree DDS / 原生 SDK
  +-------------------------------> G1 音频、灯光、预定义动作
```

主机负责对话状态、语言模型调用、TTS 生成、日志记录和操作员控制。在推荐部署方式中，
Jetson 负责机器本地的 Unitree SDK/DDS 边界。

## 运行时组件

| 层 | 主要实现 | 职责 |
| --- | --- | --- |
| 音频输入与感知 | `surf_voice_runtime.py`, `deps/SURF2026_VoiceModule-main/` | 机器人麦克风输入、唤醒词、VAD、ASR、说话人身份。 |
| ROS 桥接 | `surf_ros_bridge.py` | 将 SURF 结果发布到 ROS 2 话题。 |
| 对话编排 | `llm_surf_context_node.py`, `pipeline_control/`, `first_turn/`, `turn_detection/` | 唤醒/会话状态、过滤、多轮时序、打断/结束命令、提示词上下文。 |
| 回复/TTS 服务 | `llm_server.py` | 默认直接使用 DeepSeek 回复；TTS 端点；可选后端。 |
| 机器人输出 | `unitree_audio_player.py`, `scripts/g1_robot_skill_command.py` | TTS 播放、灯光、允许列表中的动作/技能。 |
| 中继边界 | `robot_relay/` | 面向 Unitree 原生操作的主机客户端与 Jetson TCP 服务。 |
| 可观测性/操作员界面 | `pipeline_log/`, `pipeline_monitor/`, `ui/pipeline_monitor/` | 结构化事件、延迟、就绪状态、启动/停止和会话控制。 |

## 进程编排

`scripts/run_pipeline.sh --mode wake` 加载配置，并通过 `systemd-run` 启动用户服务：

```text
surf-ros-bridge.service
surf-voice-runtime.service
surf-llm-server.service
surf-llm-node.service
surf-llm-audio-player.service
```

当且仅当 `LLM_REPLY_BACKEND=rag` 时，还会启动：

```text
surf-llm-ollama.service
surf-llm-rag.service
```

`scripts/stop_pipeline.sh` 停止托管服务。`scripts/check_pipeline.sh` 检查路径和语法，
并根据所选后端决定是否执行 Ollama/RAG 检查。

## 配置边界

- `config/default.env`：安全、与机器无关的公开默认值。
- `config/local.env.example`：各目标机器使用的模板。
- `config/local.env`：被忽略的密钥、路径、主机地址和接口。
- `project_config.py`：同一配置约定经规范化后的 Python 视图。
- `deps/SURF2026_VoiceModule-main/config/default.env`：语音运行时默认值。

公开默认值为 `LLM_REPLY_BACKEND=deepseek` 和 `UNITREE_BACKEND=relay`。
机器人/Jetson 端点值有意保持为空，直至在本地配置。参阅
[配置说明](CONFIGURATION.zh-CN.md)。

## 状态与数据

```text
runtime/    临时控制文件、状态、聊天记忆和生成的 TTS
logs/       每个会话的结构化流水线日志
config/local.env
            本地密钥与机器配置
```

这些位置不属于公开发布内容。轮次模式和首轮模式会持久化到 `runtime/` 下；Monitor
仅在流水线停止时更改它们。

## 可选、兼容与研究区域

- `xjtlu-rag-system/`：可选 RAG 服务以及允许公开的小型数据库。由于已观察到的延迟较高且
  收益有限，该服务默认禁用。
- `deps/qwen_ros_node_edg_tts/`：保留旧名称的兼容目录。当前链路仍使用其中随附的
  Unitree Python 适配器，但默认不使用其早期 Qwen 回复实现。
- `deps/unitree_g1_action_classifier_package/`：当前动作适配器以及随附的 Unitree SDK
  源码。
- `research/`：实验和分析，不是默认回复链路的依赖。教师波束成形参考资产随项目提供，
  用于固定波束成形的可复现性。
- `docs/archive/`：仅包含历史信息。

这些路径尚未重新组织，因为启动器和部署脚本依赖它们的既有位置。

## 部署决策

1. **直接使用 DeepSeek 是受支持的默认方式。**它将本地聊天模型和 RAG 嵌入服务从常规
   延迟链路中移除。
2. **优先使用 Jetson 中继，而不是由 WSL 直接初始化 Unitree。**Jetson 具备机器人网络
   接口和原生 SDK 库；WSL 保留应用程序和开发环境。
3. **下载的模型保留在 Git 之外。**KWS、ASR、声纹、Ollama 和本地 Qwen 资产安装或
   缓存在目标机器上。
4. **Markdown 是文档入口。**项目中唯一的 HTML 是运行时 Monitor UI。

## 相关文档

- [语音到机器人调用链](voice_to_robot_call_chain.zh-CN.md)
- [环境安装](SETUP.zh-CN.md)
- [G1 中继与操作](G1_RELAY.zh-CN.md)
- [可选 RAG](OPTIONAL_RAG.zh-CN.md)
- [第三方声明](../THIRD_PARTY_LICENSES.zh-CN.md)
