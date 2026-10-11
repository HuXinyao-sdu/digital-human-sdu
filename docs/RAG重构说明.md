# 本地校史 RAG 重构说明

## 目标

将 Guide 页的演示关键词回答替换为可追溯的校史资料检索，并为 DeepSeek 生成保留接口。

## 知识库

- 文件：`data/history/sdu_archive.json`、`data/history/manifest.json` 与 `data/history/documents/`。
- 内容：7 个时期、24 个已审核校史事件节点；另有校史概况、齐鲁医学史、趵突泉校区建筑档案和山东大学官网历史沿革摘要。
- 来源：时间线来自同组项目 `SDU_Archive/frontend/src/data/history.ts`，其审核口径记录在该项目的 `docs/history-content-review.md`；官网页为 <https://www.sdu.edu.cn/sdgk/lsyg.htm>。
- 标注：未附官方来源的用户提供文本会在回答中显示“用户提供资料（待复核）”。
- 更新：运行 `scripts/import_sdu_archive_history.cjs` 可重新导入时间线。内容扩展或史实订正须由内容负责人复核。

## 运行方式

`POST /api/chat` 的请求与响应合同保持不变：

```json
// 请求
{ "question": "2017年山东大学入选了什么？", "session_id": "可选" }

// 响应
{
  "answer": "……",
  "sources": ["2017｜入选首轮‘双一流’建设高校｜2017年度‘十大新闻’：https://…"],
  "session_id": "……"
}
```

默认采用本地中文 n-gram 检索，返回已召回资料中的事实摘要；没有相关资料时会明确说明，不再返回模拟回答。

如需临时代理其他 RAG 服务，在 `backend/.env` 同时设置 `RAG_API_URL` 与 `RAG_USE_EXTERNAL_API=true`；否则即使保留了旧地址，系统也不会请求它。

## DeepSeek（可选）

在 `backend/.env` 中填写：

```dotenv
DEEPSEEK_API_KEY=你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
RAG_USE_LLM=true
```

只有 `RAG_USE_LLM=true` 时才调用 DeepSeek。模型只能根据检索到的资料组织回答；调用失败会降级为本地事实摘要。

## 语义检索、重排序与多轮问答

1. 在 `backend/.env` 配置一个兼容 OpenAI `/embeddings` 协议的嵌入服务：

   ```dotenv
   RAG_USE_SEMANTIC=true
   RAG_EMBEDDING_API_KEY=你的嵌入服务密钥
   RAG_EMBEDDING_BASE_URL=https://嵌入服务地址/v1
   RAG_EMBEDDING_MODEL=嵌入模型名称
   ```

2. 在项目根目录运行 `python scripts/rebuild_rag_index.py`。生成的向量索引不会提交到 Git。
3. 运行时先进行关键词与向量双路召回，再按关键词覆盖度、标题匹配和语义相似度重排序。
4. 前端会保存后端返回的 `session_id`。同一页面中的追问会把最近两轮问题加入检索式；会话默认仅保存在内存 1 小时，服务重启后清空。

## 检索质量回归测试

`data/history/retrieval-evaluation.json` 记录了校史沿革、齐鲁医学、校区建筑、人物和“双一流”等基础问题的预期命中文档。每次调整资料、切分或排序后运行：

```powershell
python scripts/evaluate_rag.py
```

配置并完成向量索引后，再运行混合检索版本：

```powershell
python scripts/evaluate_rag.py --hybrid
```

测试集只用于检索命中回归；回答内容是否准确、完整、表达自然，仍应由内容负责人抽查。

## 新资料导入

```powershell
python scripts/import_rag_document.py "C:\资料\新档案.txt" --title "新档案标题" --source-url "https://来源页面" --keywords "人物,地点,年份"
python scripts/rebuild_rag_index.py
```

未提供 `--source-url` 的资料默认标注为“用户提供资料（待复核）”。

## 未迁入的旧项目部分

没有迁入 PostgreSQL/pgvector、MinIO、账户体系、题库和管理后台。这些组件对当前数字人项目的校史问答没有必要，而且旧项目在未配置嵌入模型时会使用哈希向量，无法提供语义检索。
