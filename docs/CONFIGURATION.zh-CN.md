# 配置说明

[English](CONFIGURATION.md) | [中文](CONFIGURATION.zh-CN.md)

> `config/default.env` 只保留公开且与机器无关的默认值；
> `config/local.env` 保存 API key、Python 路径、IP 和网卡，已被 Git 忽略。默认组合是
> `LLM_REPLY_BACKEND=deepseek` + `UNITREE_BACKEND=relay`。

## 优先级与安全

从公开模板创建本地文件：

```bash
cp config/local.env.example config/local.env
```

启动和检查脚本会先加载 `config/default.env` 及本地覆盖值，再启动各组件。请勿把凭据或
个人绝对路径写入 `config/default.env`、服务文件、提交到仓库的 shell 历史或文档示例。

## 推荐机器人链路的最小配置

```bash
LLM_PYTHON="${HOME}/miniconda3/envs/llm/bin/python"
VOICE_PYTHON="${HOME}/miniconda3/envs/voice312/bin/python"

LLM_REPLY_BACKEND="deepseek"
OPENAI_BASE_URL="https://api.deepseek.com"
OPENAI_API_KEY="<your-api-key>"
CHAT_MODEL="deepseek-v4-pro"

VOICE_AUDIO_SOURCE="robot"
VOICE_ROBOT_MIC_IF="<this-host-ip-on-the-robot-network>"
VOICE_ROBOT_MIC_PORT="5556"

UNITREE_ENABLE="1"
UNITREE_BACKEND="relay"
ROBOT_RELAY_HOST="<jetson-or-relay-host>"
ROBOT_RELAY_PORT="9999"
```

在 Jetson 中继进程上还需设置：

```bash
UNITREE_NETWORK_INTERFACE="<jetson-interface-connected-to-g1>"
UNITREE_VOICE_PEER="<unitree-voice-peer-address>"
```

机器端点有意默认为空。当当前模式需要某项端点时，入口程序会给出可操作的错误信息。
使用非机器人音频源或禁用 Unitree 输出时，不需要无关的中继设置。

## 后端选择

| 变量 | 值 | 含义 |
| --- | --- | --- |
| `LLM_REPLY_BACKEND` | `deepseek` | 默认；直接调用 DeepSeek 兼容 HTTP API。 |
|  | `rag` | 可选的 XJTLU 检索服务与 Ollama 嵌入。 |
|  | `local` | 旧版本地 Qwen 兼容链路；需要本地权重。 |
|  | `dashscope` | 可选的 DashScope 兼容链路。 |
| `UNITREE_BACKEND` | `relay` | 默认；主机将命令发送到 Jetson 中继。 |
|  | `direct` | 主机直接初始化 Unitree DDS；需要 `UNITREE_NETWORK_INTERFACE`。 |

便捷命令会更新被 Git 忽略的本地文件：

```bash
./scripts/env_set.sh LLM_REPLY_BACKEND deepseek
./scripts/env_set.sh LLM_REPLY_BACKEND rag
```

## 对话时序

重要的公开默认值包括：

| 变量 | 默认值 | 作用 |
| --- | ---: | --- |
| `VOICE_VAD_SILENCE_FRAMES` | `40` | 基础 VAD 静音帧数。 |
| `VOICE_PAUSE_ENDPOINT_GRACE_SEC` | `0.8` | Monitor **停顿**模式的额外宽限时间。 |
| `VOICE_ASR_MAX_RECORDING_SEC` | `20.0` | 录音安全时限。 |
| `LLM_FIRST_TURN_MODE` | `standard` | 初始首轮策略。 |
| `LLM_FIRST_TURN_COMPAT_LISTEN_SEC` | `30` | 兼容首轮的监听时限。 |
| `VOICE_FIRST_TURN_COMPAT_SILENCE_SEC` | `2.0` | 兼容首轮的静音确认时间。 |
| `LLM_FOLLOWUP_ENABLE` | `1` | 启用连续追问对话。 |
| `LLM_FOLLOWUP_TIMEOUT_SEC` | `8` | 默认追问等待时间。 |

Monitor 会将轮次与首轮选项持久化到 `runtime/` 下，并且只允许在流水线停止时更改模式。

## 回复、确认语和动作

- `SURF_LLM_WAKE_ACK_TEXT_ZH` 默认为 `我在`。
- `LLM_TERMINATE_ACK_TEXT` 默认为 `小浦退下了，有问题随时叫小浦。`。
- `LLM_ACTION_ENABLE` 和 `LLM_ACTION_EXECUTE` 分别控制动作选择与执行。
- `UNITREE_ENABLE=0` 会在禁用 G1 输出/动作执行的同时，保留非机器人对话服务。

Monitor 的**静默结束**与**结束**使用同一条立即停止/关闭控制链路，但不请求播放终止确认语。

## 可选 RAG 变量

默认 DeepSeek 回复链路会忽略 RAG 专用值（`SOURCE_DB`、`RAG_DB`、`MEMORY_DB`、
`OLLAMA_BASE_URL`、`OLLAMA_BIN`、`EMBED_MODEL`、`TOP_K` 和
`SIMILARITY_THRESHOLD`）。参阅[可选 RAG](OPTIONAL_RAG.zh-CN.md)。

## 检查解析后的值

```bash
set -a
source config/default.env
source config/local.env
set +a
printf 'reply=%s unitree=%s relay=%s\n' \
  "$LLM_REPLY_BACKEND" "$UNITREE_BACKEND" "$ROBOT_RELAY_HOST"
```

避免在日志或支持请求中打印 API 密钥。
