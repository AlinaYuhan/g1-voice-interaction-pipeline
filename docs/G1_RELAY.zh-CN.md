# G1 中继与操作

[English](G1_RELAY.md) | [中文](G1_RELAY.zh-CN.md)

> 推荐链路由 WSL/主机运行语音和 LLM，Jetson 在 G1 网络上
> 运行 `robot_relay/jetson_robot_relay.py`，代理音频、灯光和动作。这样可避免 WSL 直接
> 初始化 Unitree 音频/DDS 时的网卡、组播和原生库问题。

## 拓扑结构

```text
G1 外置麦克风 --UDP--> 主机/WSL SURF 语音运行时
主机/WSL LLM + TTS ----TCP----> Jetson 中继 :9999
Jetson 中继 --------Unitree--> G1 音频、灯光、机械臂动作
```

`UNITREE_BACKEND=relay` 是推荐的公开配置。直接 DDS 仅作为高级兼容模式保留，
并非默认设置。

## 主机配置

在 `config/local.env` 中设置以下值：

```bash
VOICE_AUDIO_SOURCE="robot"
VOICE_ROBOT_MIC_IF="<host robot-network IP>"
VOICE_ROBOT_MIC_PORT="5556"
ROBOT_RELAY_HOST="<Jetson host or IP>"
ROBOT_RELAY_PORT="9999"
UNITREE_BACKEND="relay"
```

启动完整流水线前检查连通性：

```bash
./scripts/check_robot_relay.sh
```

## Jetson 中继

中继启动器假定 Jetson 镜像已经安装 Unitree SDK2 Python 和 CycloneDDS。
它还会引用以下原生库目录：

```text
/home/unitree/cyclonedds_ws/install/cyclonedds/lib
/home/unitree/unitree_sdk2-main/thirdparty/lib/aarch64
```

将项目文件部署到 Jetson 前，请先验证这些前置条件：

```bash
python3 -c "import unitree_sdk2py; print('unitree_sdk2py ok')"
test -d /home/unitree/cyclonedds_ws/install/cyclonedds/lib
test -d /home/unitree/unitree_sdk2-main/thirdparty/lib/aarch64
```

如果缺少这些依赖，请按照
[THIRD_PARTY_LICENSES.zh-CN.md](../THIRD_PARTY_LICENSES.zh-CN.md) 中链接的 Unitree
官方说明安装 Unitree SDK2 Python 及其 CycloneDDS 依赖，或调整启动器以使用该
Jetson 镜像上已经验证的路径。

目前还没有通用的中继部署脚本。从主机将两个必需文件复制到 Monitor 预期的目录结构：

```bash
ssh unitree@<jetson-host> 'mkdir -p ~/surf_robot_relay/robot_relay ~/surf_robot_relay/scripts'
scp robot_relay/jetson_robot_relay.py \
  unitree@<jetson-host>:~/surf_robot_relay/robot_relay/
scp scripts/run_jetson_robot_relay.sh \
  unitree@<jetson-host>:~/surf_robot_relay/scripts/
```

然后在 Jetson 上显式设置机器专用值并启动：

```bash
export UNITREE_NETWORK_INTERFACE="<interface-connected-to-g1>"
export UNITREE_VOICE_PEER="<unitree-voice-peer-address>"
export ROBOT_RELAY_BIND_HOST="0.0.0.0"
export ROBOT_RELAY_PORT="9999"
./scripts/run_jetson_robot_relay.sh
```

请在 `~/surf_robot_relay` 中运行该命令。返回主机后，将 Jetson 地址写入
`config/local.env`，并验证 TCP 中继：

```bash
./scripts/check_robot_relay.sh
```

如果其他 Jetson 镜像使用不同的原生库位置，请在本地调整启动器，不要将某台机器的
路径作为通用默认值提交。

中继端口是无身份验证的控制端点，仅供受信任、隔离的机器人网络使用。请勿将其暴露到
公共互联网。

## 机器人麦克风运行时

`scripts/deploy_robot_mic_runtime.sh` 通过 SSH 部署麦克风流传输程序。它需要机器本地的
密钥（默认为 `~/.ssh/surf_robot_ed25519`）和 `unitree` 账户。Monitor 会在检查机器人
就绪状态时检查并启动这条链路。

当前波束成形部署脚本引用
`research/beamforming/teacher_reference_20260630/DCF_Targ7_runtime.npz`。
该固定波束成形资产随项目提供，以支持结果复现。若固定波束成形不适合当前麦克风几何
布局，操作员仍可选择 `mean4`。

## Monitor 操作

在本地启动：

```bash
./scripts/run_pipeline_monitor.sh --host 127.0.0.1 --port 8766
```

然后打开 [http://127.0.0.1:8766/](http://127.0.0.1:8766/)。服务器不带参数时的
默认端口为 8765。

推荐操作顺序：

1. 确认中继和麦克风组件均报告 `ready`。
2. 在 Pipeline 停止时选择轮次模式和首轮模式。
3. 单击**启动**，等待 Pipeline 和各组件进入就绪状态。
4. 使用语音唤醒或**唤醒**。机器人说出“我在”后，正常讲话。
5. 使用**打断**停止当前输出并立即进入监听。
6. 使用**结束**执行带确认语的关闭，或使用**静默结束**执行无语音关闭。
7. 更改模式或关闭主机前使用**停止**。

停止机器人输出的控件也会请求释放机械臂。部分成功/失败状态意味着操作员必须直接检查
机器人和中继；不能仅因浏览器请求已返回就认定实体动作已经停止。

## 直接 DDS 回退模式

仅用于高级部署：

```bash
UNITREE_BACKEND="direct"
UNITREE_NETWORK_INTERFACE="<host-interface-connected-to-g1>"
```

直接模式要求主机的 Unitree Python/C++ SDK 和 CycloneDDS 路由与机器人网络匹配。
它不会免除麦克风输入要求。
