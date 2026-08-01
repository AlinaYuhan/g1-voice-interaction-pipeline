# XJTLU 智能助手——本地 RAG 知识库系统

[中文](README.zh-CN.md) | [English](README.md)

基于西交利物浦大学知识库的本地检索增强生成（RAG）系统，通过 DeepSeek API 提供智能问答，支持身份切换、会话记忆等功能。

> 这是一个可选的实验后端。主语音流水线默认不会接入或启动该系统；受支持的默认回复后端会直接调用 DeepSeek。集成方式参阅[可选 XJTLU RAG](../docs/OPTIONAL_RAG.zh-CN.md)。

## 技术架构

| 功能 | 服务提供者 | 说明 |
|------|-----------|------|
| 对话生成 | DeepSeek API | `deepseek-v4-pro` 模型 |
| 向量嵌入 | Ollama（本地） | `nomic-embed-text` 模型 |

## 流水线

```
用户消息 → 身份推断 → 画像提取 → 闲聊检测
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             RAG 向量检索      FAQ 关键词直查     专业库直查
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                               Prompt 组装（身份 + 画像 + 历史 + 知识库）
                                      │
                                      ▼
                               DeepSeek API（deepseek-v4-pro）
                                      │
                                      ▼
                               答案截断（150 字）+ 来源列表
                                      │
                                      ▼
                     返回 JSON: { answer, identity, profile, sources, action, timing }
```

## 目录结构

```
xjtlu-rag-system/
├── app.py                 # FastAPI 主应用（/chat, /health, /profile）
├── chat_engine.py         # 对话引擎（身份推断、RAG 检索、提示词组装）
├── vector_store.py        # SQLite 向量检索（余弦相似度）
├── memory_store.py        # SQLite 会话记忆（用户画像 + 对话历史）
├── ingest.py             # 知识库向量化脚本
├── knowledge_extract.py    # 知识提取器（6 类数据源）
├── ollama_client.py      # 模型客户端（DeepSeek + Ollama）
├── rag_config.py         # 环境变量配置加载
├── test_connection.py    # 连接测试工具
├── ros_bridge.py         # ROS2 桥接（订阅 /audio_msg，发布 /xjtlu_reply）
├── requirements.txt      # 复用仓库根目录的 LLM 依赖
├── xjtlu_knowledge.db    # Git 跟踪、随仓库提供的原始知识库
├── rag_index.db          # Git 跟踪的向量索引，可由 ingest.py 重建
├── chat_memory.db        # 自动生成的本地会话记忆数据库
├── start.bat             # Windows 批处理启动脚本
├── start.ps1             # Windows 一键启动
├── start_ros_bridge.ps1  # ROS2 桥接启动脚本
└── static/              # 前端静态文件
    ├── index.html
    ├── main.js
    └── style.css
```

`xjtlu_knowledge.db` 是 Git 跟踪、随仓库提供的原始知识数据库，构建索引时会读取它。`rag_index.db` 同样由 Git 跟踪，用于保存检索所需的生成向量；运行 `python ingest.py --reset` 可重建该文件。`chat_memory.db` 保存运行时用户画像和对话历史，属于自动生成且不受 Git 跟踪的本地状态，默认主流水线不依赖它。

## 快速开始

### 步骤 1：安装依赖

```bash
pip install -r requirements.txt
```

`xjtlu-rag-system/requirements.txt` 复用仓库根目录的 `requirements-llm.txt`，不重复维护版本号。其完整内容为：

```
-r ../requirements-llm.txt
```

### 步骤 2：安装 Ollama 并配置 Embedding 模型

1. 下载并安装 [Ollama for Windows](https://ollama.com/download)。
2. 下载 embedding 模型：

```powershell
ollama pull nomic-embed-text
```

### 步骤 3：配置

```powershell
notepad .env
```

存在本地 `.env` 时，`rag_config.py` 会先读取该文件；进程中已经设置的环境变量优先级更高。仓库当前不包含 `.env.example` 模板，因此请手动创建 `.env`，且不要将其提交到 Git。

当前 `start.ps1` 要求 `.env` 存在。如果该文件缺失，脚本会尝试复制同样缺失的 `.env.example`，因而无法继续。使用 `start.ps1` 前请先手动创建 `.env`，也可以按照步骤 6 的命令手动启动 Uvicorn。

关键配置项：

```ini
CHAT_PROVIDER=openai
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-your-deepseek-api-key
CHAT_MODEL=deepseek-v4-pro

EMBED_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
EMBED_MODEL=nomic-embed-text
```

### 步骤 4：测试连接

```bash
python test_connection.py
```

### 步骤 5：构建向量索引（首次运行）

```bash
python ingest.py --reset
```

### 步骤 6：启动服务

```powershell
.\start.ps1
# 或手动：
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

访问 **http://127.0.0.1:8000**。

---

## 功能特性

- **智能问答**：基于 XJTLU 知识库的精准回答。
- **身份切换**：招生顾问、学术导师、校园助手三种身份自动识别。
- **会话记忆**：自动记住用户姓名、专业兴趣、语言偏好和对话上下文。
- **闲聊融合**：闲聊不强制引用知识库，保持自然流畅。
- **参考来源**：回答附带知识库来源链接。
- **DeepSeek 驱动**：通过 DeepSeek API 提供高质量对话生成。

---

## 身份切换

| 身份 | 切换关键词 | 回答特点 |
|------|-----------|---------|
| 校园助手 | （默认） | 自然、友好、简洁 |
| 招生顾问 | "招生顾问"、"招生" + "身份" | 清晰、谨慎、面向学生家长 |
| 学术导师 | "学术导师"、"导师" + "身份" | 专业、课程路径、学术发展 |

---

## API 接口

### POST /chat

```json
// 请求
{
  "session_id": "student-1",
  "message": "西浦有哪些专业？请用中文回答。"
}

// 响应
{
  "answer": "西交利物浦大学提供...",
  "identity": "校园助手",
  "profile": {
    "name": "张三",
    "assistant_identity": "校园助手"
  },
  "sources": [
    {
      "title": "专业列表",
      "url": "https://...",
      "category": "programmes",
      "score": 0.8542
    }
  ],
  "action": {
    "label": "举右手",
    "official_name": "right hand up",
    "action_id": 23,
    "score": 0.92,
    "backend": "deepseek",
    "reason": "普通校园信息说明适合配合举手动作。"
  },
  "timing": {
    "rag_embed_sec": 0.083,
    "rag_search_sec": 0.012,
    "llm_sec": 0.731,
    "total_sec": 0.826
  }
}
```

响应字段如下：

- `answer`：回复文本，默认最多 150 个中文字符。
- `identity`：运行时助手身份字符串之一，例如 `校园助手`。
- `profile`：字符串到字符串的映射；存在相应信息时可包含 `name`、`major_interest`、`language` 和 `assistant_identity`。
- `sources`：来源对象列表；每项包含 `title`、`url`、`category` 和数值类型的 `score`。
- `action`：动作对象；`label`、`official_name`、`backend`、`reason` 为字符串，`action_id` 为整数，`score` 为限制在 0–1 的数值。
- `timing`：耗时秒数对象；`rag_embed_sec`、`rag_search_sec`、`llm_sec`、`total_sec` 均为数值。

### GET /health

```json
{
  "status": "ok",
  "rag_db": "./rag_index.db",
  "memory_db": "./chat_memory.db",
  "embed_model": "nomic-embed-text",
  "chat_model": "deepseek-v4-pro"
}
```

### GET /profile/{session_id}

获取指定会话的用户画像和最近 50 条对话。

### GET /docs

自动生成的 FastAPI 交互式 API 文档（Swagger UI）。

---

## 配置参考

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CHAT_PROVIDER` | chat 接口类型 | `openai` |
| `EMBED_PROVIDER` | embedding 接口类型 | `ollama` |
| `OPENAI_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `OPENAI_API_KEY` | DeepSeek API 密钥 | 需填入 |
| `CHAT_MODEL` | 对话模型名称 | `deepseek-v4-pro` |
| `OLLAMA_BASE_URL` | Ollama 服务地址 | `http://127.0.0.1:11434` |
| `EMBED_MODEL` | Embedding 模型名称 | `nomic-embed-text` |
| `TOP_K` | RAG 返回条数 | `10` |
| `SIMILARITY_THRESHOLD` | 相似度阈值（0–1） | `0.35` |
| `ANSWER_MAX_CHARS` | 回复的最大中文字符数 | `150` |

---

## 常见问题

**Q：提示“连接失败”怎么办？**

1. 确认 Ollama 服务正在运行。
2. 确认已执行 `ollama pull nomic-embed-text`。
3. 检查 `.env` 中 `OPENAI_API_KEY` 有效。
4. 运行 `python test_connection.py` 查看详细错误。

**Q：回答质量不好？**

1. 重新构建索引：`python ingest.py --reset`。
2. 调整 `SIMILARITY_THRESHOLD`（提高至 0.45 更精确，降低至 0.25 返回更多参考）。

---

## 技术栈

- **后端框架**：FastAPI + Uvicorn
- **对话模型**：DeepSeek API（`deepseek-v4-pro`）
- **向量嵌入**：Ollama（`nomic-embed-text`，本地运行）
- **向量存储**：SQLite + NumPy（余弦相似度）
- **会话记忆**：SQLite
- **前端**：原生 HTML/CSS/JavaScript

---

## License

MIT License
