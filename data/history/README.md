# 校史知识库

`sdu_archive.json` 来自同组项目 `SDU_Archive` 的已审核校史时间线，包含 24 个事件节点及其来源信息。

`manifest.json` 管理补充资料。原始文本放在 `documents/`，RAG 会按段落、编号和句子切分后检索。用户提供而未附官方来源的文本会在回答引用中标记为“用户提供资料（待复核）”；不得将其与官网资料混写为唯一结论。

导入命令：

```powershell
node scripts/import_sdu_archive_history.cjs "<SDU_Archive 的 history.ts>" data/history/sdu_archive.json
```

知识库内容应由内容负责人复核后再扩展。RAG 只将检索到的条目作为回答依据，并在响应中返回来源。
