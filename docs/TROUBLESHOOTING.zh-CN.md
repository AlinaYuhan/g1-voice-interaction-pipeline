# 故障排查

[English](TROUBLESHOOTING.md) | [中文](TROUBLESHOOTING.zh-CN.md)

> 先运行 `./scripts/check_pipeline.sh`，再查看 Monitor 的组件状态和
> `journalctl --user` 日志。不要用仓库公开默认值猜测 IP，真机网卡和地址必须写入
> `config/local.env`。

## 初步检查

```bash
./scripts/check_pipeline.sh
./scripts/check_robot_relay.sh
./scripts/tail_pipeline_logs.sh all
```

查看特定服务的日志：

```bash
journalctl --user -u surf-voice-runtime -f
journalctl --user -u surf-ros-bridge -f
journalctl --user -u surf-llm-server -f
journalctl --user -u surf-llm-node -f
journalctl --user -u surf-llm-audio-player -f
```

## 缺少 `ROBOT_RELAY_HOST` 或 `VOICE_ROBOT_MIC_IF`

这些值有意不提供公开的机器默认值。使用 `UNITREE_BACKEND=relay` 或
`VOICE_AUDIO_SOURCE=robot` 时，请在 `config/local.env` 中设置它们。如果在没有机器人
输出的情况下测试，请显式禁用无关链路，不要提供虚假地址。

## 流水线启动后某个组件显示 `not ready`

- **语音运行时：**检查 `voice312` Python 路径、ASR/KWS 模型资产、麦克风 UDP
  目标和 ROS 2 环境。
- **LLM 节点/服务器：**检查 `llm` Python 路径、API 密钥、DNS/HTTPS 访问以及
  `/opt/ros/jazzy/setup.bash`。
- **音频/动作播放器：**检查中继健康状况；若使用直接模式，还需检查 Unitree DDS
  接口/库设置。
- **机器人麦克风流传输程序：**检查 SSH 密钥权限、远程账户、USB 设备可见性和目标地址。

## DeepSeek 请求失败

在不打印密钥的情况下确认当前设置：

```bash
source config/default.env
printf '%s\n' "$LLM_REPLY_BACKEND" "$OPENAI_BASE_URL" "$CHAT_MODEL"
test -n "$OPENAI_API_KEY" && echo 'API key is set'
```

默认链路应报告 `deepseek`。除非后端为 `rag`，否则 Ollama 状态与此无关。

## 唤醒时说出“我在”，但无法识别语音

- 等待唤醒确认语播放完毕，然后在配置的首轮窗口内讲话。
- 若起步较慢，请使用 Monitor 的**兼容**首轮模式（默认监听窗口为 30 秒，静音确认时间为
  2 秒）。
- 检查麦克风流和 ASR 日志，不要只检查 LLM 日志。
- **唤醒**与语音唤醒使用相同的首轮监听流程；如果两者都失败，应排查输入/VAD/ASR，
  而不是按钮本身。

## 讲话在停顿处被截断

停止 Pipeline，将轮次模式从**快速**切换为**停顿**，然后重新启动。只有在观察真实音频后
才应在 `config/local.env` 中调整 `VOICE_PAUSE_ENDPOINT_GRACE_SEC`；值越大，每个轮次
都会越慢。

## 打断或会话关闭只完成了一部分

相关控件会先请求停止机器人音频并释放机械臂，然后再继续。部分成功意味着其中某个中继
调用失败。重试前请检查中继健康状况和实体机器人状态。**静默结束**只会取消语音确认，
不会削弱停止请求。

## DDS 或网络发现失败

- 验证指定接口是否存在：`ip -o link show`。
- 将主机和 Jetson 的机器人网络路由与 WSL 虚拟适配器区分开。
- 在直接模式下，确认 CycloneDDS 和 Unitree 原生库能够正确解析。
- 仅在组播发现不可用时使用显式的 `CYCLONEDDS_URI` 对等节点。
- WSL 无法可靠初始化 Unitree 音频/DDS 时，优先使用 Jetson 中继链路。

## DeepSeek 配置上的 RAG 检查失败

确认 `config/local.env` 中为 `LLM_REPLY_BACKEND=deepseek`。检查脚本只有在
`LLM_REPLY_BACKEND=rag` 时才要求 Ollama 和 RAG 数据库。

## 无法打开 Monitor

默认地址是 `http://127.0.0.1:8765/`。使用当前机器人操作示例时，以
`--port 8766` 启动并打开 `http://127.0.0.1:8766/`。绑定到 `127.0.0.1` 仅允许
本地访问；只有在受信任的网络中并配置适当主机防火墙控制时，才应使用其他绑定地址。
