import json
import unittest
from unittest.mock import AsyncMock, patch
import httpx
from app.core.config import settings
from app.services import local_rag
from app.services.persona import INSUFFICIENT, identity_reply


class PersonaTests(unittest.IsolatedAsyncioTestCase):
    async def test_smalltalk_and_ambiguous_question_skip_retrieval(self):
        for question, expected in [('谢谢小山', '不客气'), ('他是谁？', '您指的是'), ('后来呢？', '哪件事')]:
            with patch.object(local_rag, 'retrieve_hybrid', AsyncMock()) as retrieve:
                answer, sources = await local_rag.answer(question)
            self.assertIn(expected, answer)
            self.assertNotIn(INSUFFICIENT, answer)
            retrieve.assert_not_called()

    async def test_service_failure_is_not_missing_knowledge(self):
        document = dict(title='无关候选', year='', summary='不应展示', details=[], source_labels=[], source_urls=[])
        with patch.object(local_rag, 'retrieve_hybrid', AsyncMock(return_value=[document])), patch.object(local_rag.web_rag,'configured',return_value=False), patch.object(settings,'RAG_USE_LLM',False):
            answer, sources = await local_rag.answer('校史问题')
        self.assertIn('服务暂不可用', answer)
        self.assertNotIn(INSUFFICIENT, answer)
        self.assertNotIn('无关候选', answer)
        self.assertEqual(sources, [])

    async def test_identity_without_retrieval(self):
        with patch.object(local_rag, 'retrieve_hybrid', AsyncMock()) as retrieve:
            answer, sources = await local_rag.answer('你是谁？')
        self.assertIn('我是山东大学校史讲解员小山', answer)
        self.assertEqual(sources, [])
        retrieve.assert_not_called()
        self.assertIsNone(identity_reply('你是谁？山东大学哪年创办？'))

    async def test_no_evidence(self):
        with patch.object(local_rag, 'retrieve_hybrid', AsyncMock(return_value=[])), patch.object(local_rag.web_rag, 'configured', return_value=False):
            answer, sources = await local_rag.answer('未知史实')
        self.assertTrue(answer.endswith(INSUFFICIENT))
        self.assertFalse(sources)

    async def test_partial_evidence_preserved(self):
        document = dict(title='校史', year='1901', summary='1901年创办', details=[], source_labels=['校史'], source_urls=[])
        payload = {'answer':'资料记载山东大学堂创办于1901年，但未记载当天菜单。', 'used_source_ids':[1], 'information_sufficient':False}
        client_type = httpx.AsyncClient
        def handler(request):
            return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(payload)}}]})
        with patch.object(local_rag,'retrieve_hybrid',AsyncMock(return_value=[document])), patch.object(local_rag.web_rag,'configured',return_value=False), patch.object(settings,'RAG_USE_LLM',True), patch.object(settings,'DEEPSEEK_API_KEY','test'), patch('httpx.AsyncClient',side_effect=lambda **kw:client_type(transport=httpx.MockTransport(handler),trust_env=False,verify=False,**kw)):
            answer, sources = await local_rag.answer('哪年创办，当天菜单是什么？')
        self.assertIn('1901', answer)
        self.assertTrue(answer.endswith(INSUFFICIENT))
        self.assertEqual(len(sources),1)
