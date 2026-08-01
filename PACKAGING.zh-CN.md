# 打包说明

[中文](PACKAGING.zh-CN.md) | [English](PACKAGING.md)

## 推荐的公开产物

发布构建器从 Git 跟踪的文件创建仅包含源代码且可审计的快照：

```bash
cd <repo-root>
./scripts/build_release_bundle.sh \
  --output ./release-output \
  --name surf_llm_source \
  --tar
```

生成的目录包含：

- `source/`：公开源代码快照；
- `MANIFEST.sha256`：每个已打包源文件的校验值；
- `README.md`：验证与安装指南。

使用解包后的产物前请先进行校验：

```bash
cd surf_llm_source
sha256sum --check MANIFEST.sha256
```

可选 `xjtlu-rag-system/` 源代码和获准公开的 `rag_index.db`/`xjtlu_knowledge.db` 知识数据库可以包含在快照中。它们的存在不会启用 RAG；默认回复后端仍为 DeepSeek。

## 有意排除的内容

公开产物**不会**复制本地机器状态或下载的资产，即使其中某个文件被意外加入 Git。排除项包括：

- `config/local.env`、`.env` 变体、API 密钥/凭据文件和私钥（保留安全的 `config/local.env.example` 模板）；
- 运行时/会话状态、日志、缓存、聊天记忆和生成的音频；
- 下载的模型权重，例如 ONNX、SafeTensors、GGUF 和 PyTorch 文件；
- Git 跟踪的符号链接，因为它们可能指向快照之外，并且无法在校验清单中表示为普通文件；
- 已编译对象和预构建原生库/可执行文件（`.a`、`.so`、带版本号的 `.so.*`、`.dll`、`.dylib`、`.exe`、`.lib`、`.o` 和 `.obj`）；
- 内部计划、工作日志和工作报告。`docs/archive/` 下整理过的历史说明仍会包含在内，因为公开 README 链接到了这些内容。

因此，必须在目标机器上从所记录的上游源代码本地安装或构建第三方 SDK 和原生组件。

### 教师参考材料

受版本控制的目录 `research/beamforming/teacher_reference_20260630/` 包含用于波束成形复现的教师参考 MATLAB 脚本、滤波器数据和参考音频。构建器有意保留完整目录，使用户能够复现当前固定波束成形路径。其他本地录音和生成的音频仍会排除。

## 在目标机器上安装

这不是离线或开箱即用的二进制包。解包后，请按照 `source/README.zh-CN.md` 和相关安装文档创建 Python 环境、安装 ROS 2 与 Unitree 前置依赖，并从官方来源下载模型。只在目标机器的本地环境中设置 API 密钥和机器特定的网络值。

当前阶段有意不支持打包模型，这可避免不明确的再分发权利、体积过大的发布包以及过时的本地缓存。任何人创建独立的私有离线产物时，均须对其中每个模型和数据集的许可证及再分发条款负责。

## 安全的输出行为

构建器会校验发布包名称，并拒绝覆盖现有目录或 tar 归档。再次构建前，请显式移除旧产物或重命名；脚本绝不会递归删除所选目标。
