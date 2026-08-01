# 可选 XJTLU RAG

[English](OPTIONAL_RAG.md) | [中文](OPTIONAL_RAG.zh-CN.md)

> `xjtlu-rag-system/` 保留了学校知识检索源码，
> `xjtlu_knowledge.db` 和 `rag_index.db` 已确认允许公开。该后端默认不启用，
> 因为在目标交互中带来较大延迟，且效果收益有限。

## 状态

生产环境/默认回复后端为直接使用 DeepSeek：

```text
LLM_REPLY_BACKEND=deepseek
```

可选 RAG 链路保留用于研究和未来迭代。除非显式选择，否则不会启动、检查或要求该链路。

## 包含的可选文件

```text
xjtlu-rag-system/app.py               FastAPI 服务
xjtlu-rag-system/chat_engine.py       检索与生成编排
xjtlu-rag-system/rag_config.py        RAG 专用设置
xjtlu-rag-system/vector_store.py      向量查找
xjtlu-rag-system/memory_store.py      可选的运行时对话记忆
xjtlu-rag-system/xjtlu_knowledge.db   允许公开的小型知识数据库
xjtlu-rag-system/rag_index.db         允许公开的小型向量索引数据库
```

运行时记忆写入 `runtime/` 下，不属于公开源码或发布产物。

## 为实验启用

单独安装 Ollama，并拉取配置的嵌入模型：

```bash
ollama pull nomic-embed-text
ollama list
./scripts/env_set.sh LLM_REPLY_BACKEND rag
./scripts/check_pipeline.sh
./scripts/run_pipeline.sh --mode wake
```

默认值为：

```text
EMBED_PROVIDER=ollama
EMBED_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://127.0.0.1:11434
RAG_SERVER_PORT=8010
```

RAG 服务仍使用配置的 DeepSeek/OpenAI 兼容聊天提供方进行生成。默认情况下 Ollama
提供嵌入；它不是默认聊天模型。

## 恢复为受支持的默认配置

```bash
./scripts/stop_pipeline.sh
./scripts/env_set.sh LLM_REPLY_BACKEND deepseek
./scripts/check_pipeline.sh
```

直接使用 DeepSeek 不需要 RAG 数据库、Ollama 二进制文件/缓存或
`nomic-embed-text`。进行性能对比时，请明确说明启用了哪个后端。
