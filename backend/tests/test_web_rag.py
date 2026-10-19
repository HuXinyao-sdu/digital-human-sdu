"""Offline regression tests: no credentials or paid network calls required."""
import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch

import httpx

from app.core.config import settings
from app.services import web_rag, local_rag, query_rewrite
from app.api.chat import chat
from app.models.request import ChatRequest

URL = 'https://www.archives.sdu.edu.cn/info/1001/1234.htm'
TEXT = '侯宝璋在齐鲁大学从事医学教育，相关历史资料记载了医学教学的发展。' * 8

def result(url=URL, text=TEXT):
    return {'url': url, 'title': '医学教育资料', 'raw_content': text}

def doc():
    return dict(id='local-1', title='本地资料', summary=TEXT, details=[], year='1932',
                sort_year=1932, source_labels=['本地文献'], source_urls=[], search_text=TEXT)

class WebRagTests(unittest.IsolatedAsyncioTestCase):
    async def test_rare_entity_passage_reaches_reranker(self):
        async def rank(question, candidates, limit):
            matches = [d for d in candidates if '侯宝璋' in d['search_text'] and '留校' in d['search_text']]
            self.assertTrue(matches, 'Known short entity passage must reach reranker')
            return matches[:limit]
        with patch.object(local_rag,'semantic_scores',AsyncMock(return_value={})), patch.object(local_rag,'rerank_is_configured',return_value=True), patch.object(local_rag,'rerank',side_effect=rank):
            docs = await local_rag.retrieve_hybrid('侯宝璋与齐鲁大学医学教育有什么关系？',6)
        self.assertIn('留校',docs[0]['summary'])

    def test_museum_footer_is_not_visit_evidence(self):
        raw = TEXT + '\n联系我们\n开放时间：周一8:30，参观地址文史楼三层'
        self.assertEqual(web_rag.normalize_results([result(text=raw)], '校史馆开馆时间和参观地址'), [])
        useful = '校史馆开放时间：周一8:30至11:30，参观地址文史楼三层。' * 5
        self.assertEqual(len(web_rag.normalize_results([result(text=useful)], '校史馆开馆时间和参观地址')), 1)

    async def test_official_timeout_still_tries_auxiliary(self):
        def handler(req):
            payload = json.loads(req.content)
            if payload.get('include_domains') == list(web_rag.OFFICIAL):
                raise httpx.ReadTimeout('simulated')
            return httpx.Response(200, json={'results':[result('https://zh.wikipedia.org/wiki/山东大学校友列表')]})
        with self.mock_client(handler):
            docs, status = await web_rag.search('侯宝璋医学教育')
        self.assertEqual(status, 'ok')
        self.assertEqual(docs[0]['trust'], 'encyclopedia')

    async def test_extract_rejects_unrequested_page(self):
        calls = []
        def handler(req):
            calls.append(req.url.path)
            if req.url.path == '/extract':
                return httpx.Response(200,json={'results':[result(text='校史馆开放时间：周一8:30，参观地址文史楼。'*6)]})
            return httpx.Response(200,json={'results':[]})
        with self.mock_client(handler):
            docs, status = await web_rag.search('校史馆开馆时间和参观地址')
        self.assertEqual(calls, ['/extract','/search','/search'])
        self.assertEqual(status, 'empty')
        self.assertFalse(docs)

    async def test_followup_rewrite_rejects_invented_year(self):
        context = '当前问题：后来他在哪任教？ 上下文问题：老舍在齐鲁大学任教吗？'
        for value, expected in [('老舍后来在哪任教？','老舍后来在哪任教？'),('老舍1934年在哪任教？',context)]:
            def handler(req):
                return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps({'query':value})}}]})
            with patch.object(settings,'RAG_USE_LLM',True), patch.object(settings,'DEEPSEEK_API_KEY','test'), self.mock_client(handler):
                self.assertEqual(await query_rewrite.rewrite('后来他在哪任教？',context),expected)
        with patch('httpx.AsyncClient') as client:
            self.assertEqual(await query_rewrite.rewrite('学校何时成立？',context),'学校何时成立？')
            client.assert_not_called()

    def setUp(self):
        self.patches = []
        for name, value in dict(RAG_WEB_ENABLED=True, TAVILY_API_KEY='test-key',
            RAG_USE_RERANK=False, RAG_USE_LLM=False, DEEPSEEK_API_KEY='', RAG_WEB_TIMEOUT=2,
            RAG_WEB_CACHE_SECONDS=60).items():
            p = patch.object(settings, name, value); p.start(); self.patches.append(p)
        web_rag._CACHE.clear()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        web_rag._CACHE.clear()

    def mock_client(self, handler):
        cls = httpx.AsyncClient
        return patch('httpx.AsyncClient', side_effect=lambda **kw: cls(transport=httpx.MockTransport(handler), trust_env=False, verify=False, **kw))

    def test_url_boundaries(self):
        self.assertEqual(web_rag.source_kind(URL), 'official')
        self.assertEqual(web_rag.source_kind('https://zh.wikipedia.org/wiki/山东大学校友列表'), 'encyclopedia')
        for url in ['https://www.archives.sdu.edu.cn.evil.test/a', 'http://127.0.0.1/a',
                    'https://www.sdu.edu.cn@evil.test/a', 'https://www.sdu.edu.cn:8888/a',
                    'file:///etc/passwd', 'https://zh.wikipedia.org/wiki/任意词条',
                    'https://baike.baidu.com/item/其他学校', 'http://tclib.sdu.edu.cn/a']:
            self.assertIsNone(web_rag.source_kind(url), url)

    def test_body_required_and_duplicates_removed(self):
        values = [result(), result(URL + '?tracking=1'),
                  {'url': URL, 'content': TEXT}, result('https://evil.test/a'), None]
        docs = web_rag.normalize_results(values, '侯宝璋医学教育')
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['trust'], 'official')
        self.assertIn('获取时间', docs[0]['source_labels'][1])

    async def test_disabled_never_calls_provider(self):
        with patch.object(settings, 'RAG_WEB_ENABLED', False), patch.object(web_rag, '_search', new_callable=AsyncMock) as search:
            self.assertEqual(await web_rag.search('山大'), ([], 'disabled'))
            search.assert_not_awaited()

    async def test_sufficient_local_skips_search(self):
        with patch.object(web_rag, 'sufficient', AsyncMock(return_value=True)), patch.object(web_rag, 'search', new_callable=AsyncMock) as search:
            docs, note = await web_rag.supplement('何时创办', '山大何时创办', [doc()])
            self.assertEqual(docs, [doc()]); self.assertEqual(note, '')
            search.assert_not_awaited()

    async def test_official_search_and_cache(self):
        calls = []
        def handler(req):
            calls.append(json.loads(req.content))
            self.assertEqual(req.headers['Authorization'], 'Bearer test-key')
            return httpx.Response(200, json={'results': [result()]})
        with self.mock_client(handler):
            docs, status = await web_rag.search('侯宝璋')
            self.assertEqual(status, 'ok'); self.assertEqual(len(docs), 1)
            self.assertEqual((await web_rag.search('侯宝璋'))[1], 'cached')
        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0]['include_answer'])
        self.assertEqual(calls[0]['include_domains'], list(web_rag.OFFICIAL))

    async def test_auxiliary_only_after_no_official_body(self):
        calls = []
        def handler(req):
            calls.append(json.loads(req.content))
            items = [] if len(calls) == 1 else [result('https://zh.wikipedia.org/wiki/山东大学校友列表')]
            return httpx.Response(200, json={'results': items})
        with self.mock_client(handler):
            docs, note = await web_rag.supplement('侯宝璋的医学教育经历', '侯宝璋的医学教育经历', [])
        self.assertEqual(len(calls), 2)
        self.assertEqual(docs[0]['trust'], 'encyclopedia')
        self.assertIn('尚需官方资料核验', note)

    async def test_timeout_and_bad_payload_degrade(self):
        for handler in [lambda r: httpx.Response(429), lambda r: httpx.Response(200, json=[]),
                        lambda r: httpx.Response(200, text='not json')]:
            with self.mock_client(handler):
                self.assertEqual((await web_rag.search('山大'))[1], 'unavailable')
        async def slow(q):
            await asyncio.sleep(1)
        with patch.object(settings, 'RAG_WEB_TIMEOUT', 1), patch.object(web_rag, '_search', AsyncMock(side_effect=httpx.ReadTimeout('timeout'))):
            self.assertEqual((await web_rag.search('山大'))[1], 'unavailable')

    async def test_current_question_does_not_use_stale_local_on_failure(self):
        with patch.object(web_rag, 'search', AsyncMock(return_value=([], 'unavailable'))):
            docs, note = await web_rag.supplement('现在的开馆时间', '山大校史馆现在的开馆时间', [doc()])
        self.assertFalse(docs); self.assertIn('最新', note)

    async def test_gate_validates_evidence_ids(self):
        for response, expected in [({'sufficient': True, 'evidence_ids':['0']}, True),
                                   ({'sufficient': True, 'evidence_ids':['999']}, False),
                                   ({'sufficient': 'true', 'evidence_ids':['0']}, False),
                                   ({'sufficient': True, 'evidence_ids':[]}, False)]:
            def handler(req):
                return httpx.Response(200, json={'choices':[{'message':{'content':json.dumps(response)}}]})
            with patch.object(settings, 'RAG_USE_LLM', True), patch.object(settings, 'DEEPSEEK_API_KEY', 'test'), self.mock_client(handler):
                self.assertEqual(await web_rag.sufficient('侯宝璋的经历', '侯宝璋的经历', [doc()]), expected)

    async def test_live_copy_replaces_stale_same_url(self):
        local = doc(); local['source_urls'] = [URL]
        web = web_rag.normalize_results([result()], '医学')
        with patch.object(web_rag, 'sufficient', AsyncMock(return_value=False)), patch.object(web_rag, 'search', AsyncMock(return_value=(web,'ok'))):
            docs, _ = await web_rag.supplement('校史', '校史', [local])
        self.assertEqual(len(docs), 1); self.assertEqual(docs[0]['origin'], 'web')

    async def test_generation_receives_mixed_evidence_and_sources(self):
        web = web_rag.normalize_results([result()], '医学')
        def handler(req):
            payload = json.loads(req.content)
            self.assertIn(URL, payload['messages'][1]['content'])
            self.assertIn('百科', payload['messages'][0]['content'])
            return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps({'answer':'依据资料的回答','used_source_ids':[2],'information_sufficient':True})}}]})
        with patch.object(local_rag, 'retrieve_hybrid', AsyncMock(return_value=[doc()])), patch.object(web_rag, 'supplement', AsyncMock(return_value=([doc()]+web,''))), patch.object(settings,'RAG_USE_LLM',True), patch.object(settings,'DEEPSEEK_API_KEY','test'), self.mock_client(handler):
            answer, sources = await local_rag.answer('医学')
        self.assertEqual(answer, '依据资料的回答'); self.assertEqual(len(sources),1)
        self.assertIn(URL, sources[0])

    async def test_chat_records_web_turn_and_keeps_contract(self):
        with patch('app.api.chat.contextualize', return_value='当前问题：后来呢 上下文问题：侯宝璋'), patch('app.api.chat.local_rag_answer', AsyncMock(return_value=('回答',['来源']))) as answer, patch('app.api.chat.record_turn') as record, patch.object(settings, 'RAG_USE_EXTERNAL_API', True), patch.object(settings, 'RAG_API_URL', 'https://unused.test'):
            response = await chat(ChatRequest(question='后来呢',session_id='session-test'))
            self.assertEqual(response.model_dump(), {'answer':'回答','sources':['来源'],'session_id':'session-test'})
            record.assert_called_once_with('session-test','后来呢','回答')
            self.assertIn('侯宝璋', answer.call_args.args[1])

    async def test_latest_bypasses_gate_model(self):
        with patch('httpx.AsyncClient') as client:
            self.assertFalse(await web_rag.sufficient('现在开放吗', '校史馆', [doc()]))
            client.assert_not_called()

    async def test_missing_key_is_local_only(self):
        with patch.object(settings, 'TAVILY_API_KEY', ''), patch.object(web_rag, 'search', new_callable=AsyncMock) as search:
            self.assertEqual(await web_rag.supplement('问题', '问题', [doc()]), ([doc()], ''))
            search.assert_not_awaited()

    async def test_no_llm_does_not_present_web_as_verified_answer(self):
        web = web_rag.normalize_results([result()], '医学')
        with patch.object(local_rag, 'retrieve_hybrid', AsyncMock(return_value=[])), patch.object(web_rag, 'supplement', AsyncMock(return_value=(web, ''))):
            answer, sources = await local_rag.answer('医学')
        self.assertIn('无法确认', answer)
        self.assertNotIn(TEXT, answer)
        self.assertEqual(len(sources), 0)

    async def test_expired_cache_is_refetched(self):
        with patch.object(web_rag, '_search', AsyncMock(return_value=[doc()])) as search, patch.object(settings, 'RAG_WEB_CACHE_SECONDS', 0):
            await web_rag.search('同一问题'); await web_rag.search('同一问题')
            self.assertEqual(search.await_count, 2)

if __name__ == '__main__':
    unittest.main()
