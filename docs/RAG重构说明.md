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
   RAG_EMBEDDING_BATCH_SIZE=20
   ```

2. 在项目根目录运行 `python scripts/rebuild_rag_index.py`。生成的向量索引不会提交到 Git。
3. 运行时先进行关键词与向量双路召回，再按关键词覆盖度、标题匹配和语义相似度重排序。
4. 前端会保存后端返回的 `session_id`。同一页面中的追问会把最近两轮问题加入检索式；会话默认保存到本地 SQLite 1 小时，后端重启后仍可恢复。`data/rag-sessions.sqlite3` 为本地运行数据，不提交 Git；部署时可通过 `RAG_SESSION_DB_PATH` 指定持久化目录。

如需进一步提高候选资料的排序精度，可启用千问的 `qwen3-rerank`：

```dotenv
RAG_USE_RERANK=true
RAG_RERANK_API_KEY=你的千问API_Key
RAG_RERANK_BASE_URL=https://maas.qianwenaiapi.com/compatible-api/v1
RAG_RERANK_MODEL=qwen3-rerank
RAG_RERANK_CANDIDATES=12
```

它会对关键词与向量检索召回的前 12 条候选资料进行二次排序，只返回最相关的 3 条。服务不可用时系统自动使用原有混合检索结果。

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

## 2026-10-15：按需联网兜底（不采集入库）

### 启用

在 backend/.env 中填写独立的 Tavily Search API Key，并配置：

```dotenv
RAG_WEB_ENABLED=true
TAVILY_API_KEY=你的搜索服务密钥
RAG_USE_EXTERNAL_API=false
RAG_USE_LLM=true
# 沿用现有 DEEPSEEK_API_KEY
RAG_WEB_TIMEOUT=45
RAG_WEB_REQUEST_TIMEOUT=15
RAG_WEB_GATE_TIMEOUT=6
RAG_WEB_CACHE_SECONDS=300
RAG_WEB_MAX_RESULTS=5
```

重启后端生效。默认关闭；没有搜索密钥时沿用本地 RAG。Tavily Key 与 DeepSeek、千问、MiniMax Key 不通用。搜索接口参考：https://docs.tavily.com/documentation/api-reference/endpoint/search 。无需新增 SDK 依赖。

### 流程与来源边界

1. 本地混合检索仍按原流程运行。启用联网后，使用 DeepSeek 判断这些证据能否直接覆盖全部子问题；最新/当前类问题直接触发联网。判定故障时保守地尝试联网。这是模型判断，不是已校准的可信概率。
2. 首先搜索 www.archives.sdu.edu.cn、www.sdu.edu.cn、www.sdu.org.cn 三个精确主机（不泛化到全部子域名）。官方搜索没有可用正文时，尝试百度百科“山东大学”（122748）及维基百科“山东大学校友列表”的指定页面；其他百科页面不进入证据。
3. tclib.sdu.edu.cn 尚未核验，暂不启用。全站采集、定时更新、原文入库均未实现。
4. 仅接受服务返回的 raw_content 正文，拒绝只有搜索摘要的结果，不使用搜索服务生成的 answer。按问题截取相关片段，记录原 URL、来源类型、抓取时间；发布时间缺失时不以抓取时间代替。
5. 内外部证据合并去重后，沿用已配置的 Rerank 模型统一排序；没有配置或超时时保留候选顺序。百科最多一条，带“未经独立核验”提示。同 URL 的联网正文替换本地副本，避免旧副本重复。
6. DeepSeek 统一生成回答，提示中要求区分任教/就读/毕业，处理冲突与时效，忽略资料夹带指令，证据不足时不推断。提示约束不能保证零幻觉，仍需人工评测。
7. 联网超时/限流/异常时回退并提示；当前类问题无法联网核实时不返回旧资料冒充最新信息。生成服务故障且有联网资料时，只提示查看来源，不把网页正文当作已核实答案直接朗读。

成功的搜索结果仅在进程内缓存五分钟（最多128个查询）；不保存到已审核知识库，重启后失效。不同进程缓存互不共享。搜索服务接收当前问题及最多900字符的近期问题上下文，不传本地证据全文、会话ID或密钥；统一生成/重排仍使用已配置服务。

### 接口与协作说明

- 未新增端点，POST /api/chat 的 question/session_id 和 answer/sources/session_id 签名保持不变。
- sources 仍为字符串列表，联网来源增加类型、时间与URL标签。正常生成时仅显示模型声明实际使用且编号通过校验的证据；仍不是逐句事实验证。生成失败时展示候选依据供查阅。
- RAG_WEB_ENABLED=true 时优先本地+联网模式，不再走旧 RAG_API_URL 整体答案代理（即使搜索密钥缺失，也使用本地路径）。旧代理模式成功后补记会话记录。
- 前端仅将 chat 请求超时调为120秒；frontend/nginx.conf 的 API 代理读取超时调为150秒，页面布局未变。
- 默认最多两次搜索（官方一次，必要时百科一次），另可有一次正文提取请求（最多3个网址；校史馆参观问题优先提取已知官方首页）。证据判断、网页相关性筛选和有指代的追问改写可能增加模型请求。平台用量和费用按实际账户计费。

### 验证

从 backend 目录运行：

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p test_web_rag.py -v
```

离线测试模拟搜索/生成服务，覆盖白名单、正文要求、超时限流、缓存、百科降级、证据门控、内外融合和会话记录，不需要真实API Key。

配置真实密钥后再验收：本地能回答的问题应跳过搜索；“校史馆现在的开放时间”应联网；追问沿用主体；不存在的史实应说明无证据；搜索服务不可用时本地问答仍可用。真实搜索召回率、首字延迟和事实准确率需在配置后实测，不能由离线测试推断。


### 2026-10-15 联网质量修复

- 联网阶段总预算45秒、单次Tavily请求15秒，官方请求异常仍尝试百科。相关性筛选和正文提取包含在总预算内；预算不是整个问答的耗时上限。
- 严格校验返回URL，搜索增加site限定；正文提取仅接受本次请求的URL。搜索供应商仍可能返回范围外页面，应用会丢弃，不扩大白名单。
- 清理联系页脚，对开馆/参观问题要求实际服务信息；再以模型筛选直接相关正文。正文不足或服务失败继续保守降级。
- 多轮追问先改写为独立问题，禁止新增上下文未出现的年份，失败则保留原上下文；新话题不拼入旧问题。
- 本地送入生成的候选由3条增加到6条；启用重排时，将包含稀有查询短语的资料补入重排候选，修复侯宝璋“毕业留校”漏检。
- 生成内部使用answer/used_source_ids结构化结果，外部POST /api/chat字段不变。仅展示实际使用来源，空证据时拒绝给出确定结论。
- 原始建筑档案“第二次在齐鲁大学任教”措辞仍待人工核验；在生成约束中标明，不改动原文、不推断另一段任教时间。

验证：21项联网离线测试通过。完成10问真实接口测试及3问定向复测：校史馆开放时间能够引用官方参观信息；侯宝璋留校资料能被召回；无依据问题拒绝编造。老舍追问能明确主体，但当前限定网站未提供足够任教年份证据，仍保守回答无法核实。扩大官方子站范围需另行讨论，不能将HTTP 200当成事实正确率。
