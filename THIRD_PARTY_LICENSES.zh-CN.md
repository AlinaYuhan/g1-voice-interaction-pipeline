# 第三方许可证与发布说明

[中文](THIRD_PARTY_LICENSES.zh-CN.md) | [English](THIRD_PARTY_LICENSES.md)

本文档是工程清单，不构成法律建议，也不保证每种使用或分发方式均获得许可。它区分了本源代码树中随附的材料，以及运行时单独获取的软件、模型和服务。第一方项目代码采用根目录下的 Apache-2.0 许可证；该许可证不会取代下述单独条款和许可边界说明。

## 内置的第三方材料

### Unitree SDK2 (C++)

- **路径：** `deps/unitree_g1_action_classifier_package/unitree_sdk2/`
- **许可证/状态：** BSD-3-Clause。内置副本包含 `deps/unitree_g1_action_classifier_package/unitree_sdk2/LICENSE`，源代码分发时必须保留该文件，二进制分发时也必须按要求重现其内容。内置修订版本仍需记录。
- **官方源代码：** [Unitree SDK2](https://github.com/unitreerobotics/unitree_sdk2)

该 SDK 还随附其自身的嵌套第三方许可证树。请将这些文件与对应材料一起保留；根目录的 Apache-2.0 许可证不会取代其中声明的条款：

| 内置路径 | 声明的许可证 | 官方源代码 |
| --- | --- | --- |
| `deps/unitree_g1_action_classifier_package/unitree_sdk2/licenses/eclipse-cyclonedds/cyclonedds/LICENSE` | EPL-2.0 or EDL-1.0 | [Eclipse Cyclone DDS](https://github.com/eclipse-cyclonedds/cyclonedds) |
| `deps/unitree_g1_action_classifier_package/unitree_sdk2/licenses/eclipse-cyclonedds/cyclonedds-cxx/LICENSE` | EPL-2.0 or EDL-1.0 | [Eclipse Cyclone DDS C++](https://github.com/eclipse-cyclonedds/cyclonedds-cxx) |
| `deps/unitree_g1_action_classifier_package/unitree_sdk2/licenses/eclipse-iceoryx/iceoryx/LICENSE` | Apache-2.0 | [Eclipse iceoryx](https://github.com/eclipse-iceoryx/iceoryx) |
| `deps/unitree_g1_action_classifier_package/unitree_sdk2/licenses/Tencent/rapidjson/LICENSE` | MIT，但有该文件所述的例外 | [Tencent RapidJSON](https://github.com/Tencent/rapidjson) |
| `deps/unitree_g1_action_classifier_package/unitree_sdk2/thirdparty/include/ddscxx/dds/LICENSE` | Apache-2.0 | [Eclipse Cyclone DDS C++](https://github.com/eclipse-cyclonedds/cyclonedds-cxx) |

### Unitree SDK2 Python

- **路径：** `deps/qwen_ros_node_edg_tts/third_party/unitree_sdk2_python/`
- **许可证/状态：** BSD-3-Clause。内置 `setup.py` 声明版本为 `1.0.1`，并以 `deps/qwen_ros_node_edg_tts/third_party/unitree_sdk2_python/LICENSE` 保留了匹配的官方许可证文本。
- **修订状态：** 此副本包含本地集成修改，且未保留确切的上游提交标识。如果能够找回，应记录其上游基础版本；在此之前，请将此目录视为经过修改的内置副本，不要声称它与某个特定上游修订版本一致。
- **官方源代码：** [Unitree SDK2 Python](https://github.com/unitreerobotics/unitree_sdk2_python)

## 运行时软件、模型和服务

这些项目应在安装期间从官方、固定版本的来源获取，而不是内置到公开源代码或发布归档中。请记录下载的修订版本或摘要以及校验和。如果日后再分发任何模型，请审查并满足所分发确切字节内容的条款。

当前 `scripts/build_release_bundle.sh` 会创建经过筛选的 Git 跟踪源代码快照。它排除下载的模型权重、缓存、生成的音频、运行时数据、机密信息、符号链接和预构建库。模型仍属于安装时下载项目。如果以后创建独立的离线产物，则必须核准每个确切模型或二进制文件，并将其与所需的许可证、声明、署名、修订版本和校验和一同打包。

| 组件及仓库位置/引用 | 公布的条款与官方来源 | 当前发布处理方式 |
| --- | --- | --- |
| Edge TTS，从 `requirements-llm.txt` 安装，并由 `llm_server.py` 和 `deps/qwen_ros_node_edg_tts/qwen_server.py` 使用 | 客户端采用 LGPLv3，但 `src/edge_tts/srt_composer.py` 除外；其[官方许可证](https://github.com/rany2/edge-tts/blob/master/LICENSE)将该文件标识为 MIT。[官方仓库](https://github.com/rany2/edge-tts)。 | **仅安装；不要内置。** Microsoft 托管的 TTS 服务和语音条款独立于客户端许可证。 |
| Paraformer，通常缓存在 `${HOME}/.cache/modelscope/hub/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch` | [ModelScope 官方模型页面](https://modelscope.cn/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch)声明为 Apache-2.0。 | **建议安装时下载。** 打包时必须提供确切的修订版本、许可证/声明、来源和校验和。 |
| WeSpeaker `pyannote/wespeaker-voxceleb-resnet34-LM`，通常缓存在 `${HOME}/.cache/huggingface/hub/models--pyannote--wespeaker-voxceleb-resnet34-LM` 下 | [官方模型页面](https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM)声明为 CC-BY-4.0。 | **建议安装时下载。** 打包时必须提供确切修订版本、署名、许可证链接/文本以及变更说明。 |
| Ollama `nomic-embed-text`，由 `EMBED_MODEL` 引用 | [Ollama 官方条目](https://ollama.com/library/nomic-embed-text)链接到源模型；[Nomic 官方模型页面](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)声明为 Apache-2.0。 | **可选，仅下载**，使用 `ollama pull nomic-embed-text`。如果未固定数据块的摘要并将其与符合许可证的源产物匹配，请勿再分发该数据块。 |
| 预期位于 `deps/Qwen3.5-0.8B/model/` 的 Qwen 模型 | [官方 `Qwen/Qwen3.5-0.8B` 模型页面](https://huggingface.co/Qwen/Qwen3.5-0.8B)声明为 Apache-2.0，但本地路径无法证明其中字节来自该模型，也未标识修订版本。 | **不要打包本地目录。** 建议从官方固定版本下载；任何现有本地副本的来源和哈希值均未解决。 |
| 预期位于 `deps/SURF2026_VoiceModule-main/models/kws/` 下的 sherpa-onnx KWS 文件 | [官方预训练 KWS 文档](https://k2-fsa.github.io/sherpa/onnx/kws/pretrained_models/index.html)标明了预期的 `sherpa-onnx-kws-zipformer-wenetspeech-3.3M-2024-01-01` 归档。[sherpa-onnx 软件](https://github.com/k2-fsa/sherpa-onnx)采用 Apache-2.0，但这不能确定单独训练的权重或词元表的许可证。 | **许可证未解决；不要打包。** ONNX 权重和 `tokens.txt` 已排除在公开源代码树/发布包之外；用户必须从官方模型归档获取匹配文件。 |

## 随附的参考材料与项目许可边界

仓库随附以下教师参考脚本、滤波器和录音，作为固定波束成形路径的可复现参考资产。它们保持在一起，以便使用当前波束成形实现和参考验证。本清单不将这些参考资产标识为 Apache-2.0；其适用条款与第一方项目代码相互独立：

- `research/beamforming/teacher_reference_20260630/Fixed_Mini_Beamformer.m`
- `research/beamforming/teacher_reference_20260630/test.m`
- `research/beamforming/teacher_reference_20260630/DCF_Targ7.mat`
- `research/beamforming/teacher_reference_20260630/DCF_Targ7_runtime.npz`
- `research/beamforming/teacher_reference_20260630/mixture.wav`
- `research/beamforming/teacher_reference_20260630/out0.wav`

以下项目相关目录中的第一方封装与集成代码适用根目录的 Apache-2.0 许可证。另行标识的内置组件和随附参考材料保留各自条款，不会因根许可证而被重新许可为 Apache-2.0：

- `deps/SURF2026_VoiceModule-main/`
- `deps/qwen_ros_node_edg_tts/`（不包括另行列出的内置 Unitree SDK2 Python 副本）
- `deps/unitree_g1_action_classifier_package/`（不包括另行列出的内置 Unitree SDK2 C++ 副本）
