# 语音到机器人调用链

[English](voice_to_robot_call_chain.md) | [中文](voice_to_robot_call_chain.zh-CN.md)

> **当前事实来源（2026-07-31）。** 以下序列对应默认的 `deepseek` 回复后端和
> `relay` Unitree 后端。
>
> **摘要：** 音频从 G1 外置麦克风进入 SURF，经唤醒/VAD/ASR 后发布到
> ROS 2；上下文节点调用本地 `llm_server.py`，默认直接请求 DeepSeek，再由
> Edge TTS 生成音频，通过 Jetson relay 交给 G1 播放并执行允许的灯光/动作。

## 1. 启动与就绪

`scripts/run_pipeline.sh --mode wake`：

1. 加载 `config/default.env` 和被忽略的 `config/local.env`。
2. 验证所选音频模式和 Unitree 模式需要的端点。
3. 加载 ROS 2 Jazzy 环境。
4. 启动桥接、语音、LLM 服务器、上下文节点和音频播放器服务。
5. 仅在 `LLM_REPLY_BACKEND=rag` 时启动 Ollama/RAG 服务。
6. 等待 LLM 健康端点和音频播放器服务就绪。

Monitor 使用相同配置，并分别展示服务、中继和机器人麦克风的就绪状态。

## 2. 音频与唤醒

使用 `VOICE_AUDIO_SOURCE=robot` 时，机器人侧麦克风流传输程序将音频发送到
`VOICE_ROBOT_MIC_IF:VOICE_ROBOT_MIC_PORT`。SURF 运行时执行：

```text
音频帧 -> 唤醒词 -> VAD -> ASR -> 可选的说话人识别
```

唤醒可由口述唤醒词或 Monitor 的**唤醒**命令触发。两者都会进入相同的首轮状态。
播放配置的确认语（默认为 `我在`）后，运行时开始监听用户的第一句话。

以下时序控制彼此独立：

- **快速/停顿：**用多长的静音判断一个录音轮次结束；
- **标准/兼容：**首轮监听策略。兼容模式的默认监听时限为 30 秒，静音确认时间为 2 秒。

## 3. ROS 2 上下文

`surf_ros_bridge.py` 发布识别到的输入和上下文话题，包括：

```text
/audio_msg
/wake_word_event
/vad_state
/speaker_id
```

`llm_surf_context_node.py` 消费 `/audio_msg`，应用唤醒/会话和自身语音防护；启用时加入
说话人/会话上下文，并调用本地推理端点（默认为 `http://127.0.0.1:8000/infer`）。

集成工作区保持 `LLM_AUTOSTART_ASR_BRIDGE=0`，因为 SURF 是唯一的 ASR 发布者。

## 4. 回复选择

`llm_server.py` 根据 `LLM_REPLY_BACKEND` 选择后端：

```text
deepseek  -> 直接调用 DeepSeek 兼容 HTTP API（默认）
rag       -> 本地 xjtlu-rag-system /chat，使用 Ollama 嵌入
local     -> 旧版本地 Qwen 兼容模型路径
dashscope -> 可选的 DashScope 兼容 API
```

默认链路使用 `OPENAI_BASE_URL`、`OPENAI_API_KEY` 和配置的 DeepSeek 模型，
不涉及 RAG 数据库、Ollama 进程、嵌入模型或本地 Qwen 权重。

回复约定包含口述回复和可选动作信息。动作执行仍受项目允许列表和执行开关限制。

## 5. TTS 与机器人输出

上下文节点向本地 LLM 服务请求 TTS。Edge TTS 生成运行时音频文件，
`unitree_audio_player.py` 负责协调：

1. 播放状态和自身语音防护；
2. G1 灯光状态；
3. TTS 音频传输；
4. 可选的允许列表动作执行；
5. 转回追问监听或待机状态。

使用 `UNITREE_BACKEND=relay` 时，命令发送到 `RobotRelayClient`，再经 TCP 到达
`robot_relay/jetson_robot_relay.py`。Jetson 使用自身的 Unitree 原生库和机器人网络接口
执行实体操作。

## 6. 多轮对话与手动控制

回复结束后，追问监听会在配置的超时时间内保持开放。终止短语或 Monitor 控件会关闭对话。

- **打断：**使进行中的生成失效，请求停止机器人音频并释放机械臂，然后开始监听。
- **结束：**执行相同的立即停止输出/释放操作，关闭会话，并播放配置的终止确认语。
- **静默结束：**执行相同的停止输出/释放和关闭操作，但不播放终止确认语。

生成/请求协议可以防止打断后仍接受过期的 LLM、TTS 或动作任务。Monitor 返回部分成功
意味着某项机器人中继操作失败，需要进行实体/人工验证。

## 7. 日志与观测

`pipeline_log/` 将结构化事件写入 `logs/<session>/pipeline.log`。Monitor 读取这些数据以
展示：

- 最新 ASR、回复和动作；
- 已完成轮次的延迟；
- 实时事件时间线；
- 会话状态和组件就绪状态。

`runtime/` 包含临时控制/状态文件以及生成的 TTS。这两个目录都不属于公开源码包。

## 8. 可选 RAG 分支

显式设置 `LLM_REPLY_BACKEND=rag` 时，编排流程会插入：

```text
llm_server.py -> xjtlu-rag-system /chat
              -> SQLite 向量/知识数据库
              -> Ollama nomic-embed-text
              -> DeepSeek 兼容生成
```

此分支保留用于实验；由于延迟较高且观察到的收益有限，默认禁用。参阅
[可选 RAG](OPTIONAL_RAG.zh-CN.md)。

## 相关文档

- [当前架构](project_architecture.zh-CN.md)
- [配置说明](CONFIGURATION.zh-CN.md)
- [G1 中继与操作](G1_RELAY.zh-CN.md)
- [故障排查](TROUBLESHOOTING.zh-CN.md)
