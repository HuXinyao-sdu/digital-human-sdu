"""Live RAG smoke evaluation. Uses configured paid APIs; writes evidence for manual review."""
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.chdir(ROOT / 'backend')
import httpx
from app.core.config import settings
from app.main import app
from app.services import local_rag, web_rag

CASES = [
 ('founding', '山东大学堂是哪一年创办的？请简短回答。', None),
 ('merger', '2000年是哪三所学校合并组建新的山东大学？', None),
 ('building', '趵突泉校区的教学三楼原来叫什么？', None),
 ('medicine', '华美医院与齐鲁医院是什么关系？', None),
 ('person', '侯宝璋与齐鲁大学医学教育有什么关系？', None),
 ('current', '山东大学校史馆目前的常规开馆时间和参观地址是什么？', None),
 ('false_premise', '请介绍山东大学2030年获得诺贝尔文学奖的校友张星河，给出获奖日期。', None),
 ('unknown', '1901年山东大学堂开学典礼当天食堂午餐的完整菜单是什么？', None),
 ('multi_first', '老舍是什么时候在齐鲁大学任教的？', 'multi'),
 ('multi_follow', '后来他又在山东大学任教了吗？具体是哪几年？', 'multi'),
]

async def main():
    output = ROOT / 'tmp' / 'rag-live-evaluation.json'
    output.parent.mkdir(exist_ok=True)
    settings.RAG_SESSION_DB_PATH = str(ROOT / 'tmp' / 'rag-live-evaluation-sessions.sqlite3')
    if not web_rag.configured():
        raise SystemExit('Web RAG is not configured; no requests made.')
    report = {'cases':[], 'note':'Live services; answers require manual evidence review. No TTS calls.'}
    sessions = {}
    original_post = httpx.AsyncClient.post
    original_retrieve = local_rag.retrieve_hybrid
    original_supplement = web_rag.supplement
    for identifier, question, group in CASES:
        counts, evidence = {}, {}
        async def track_post(client, url, *args, **kwargs):
            host = httpx.URL(str(url)).host
            if host and host != 'evaluation.local': counts[host] = counts.get(host, 0) + 1
            return await original_post(client, url, *args, **kwargs)
        async def track_retrieve(*args, **kwargs):
            docs = await original_retrieve(*args, **kwargs)
            evidence['local'] = docs
            return docs
        async def track_supplement(*args, **kwargs):
            docs, notice = await original_supplement(*args, **kwargs)
            evidence['final'] = docs
            evidence['notice'] = notice
            evidence['query'] = args[1]
            return docs, notice
        begin = time.monotonic()
        row = {'id':identifier,'question':question}
        try:
            with patch.object(httpx.AsyncClient,'post',track_post), patch.object(local_rag,'retrieve_hybrid',track_retrieve), patch.object(web_rag,'supplement',track_supplement):
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://evaluation.local',trust_env=False) as client:
                    payload = {'question': question}
                    if group and group in sessions: payload['session_id'] = sessions[group]
                    response = await asyncio.wait_for(client.post('/api/chat',json=payload),timeout=120)
                    row['http_status'] = response.status_code
                    if response.status_code == 200:
                        data = response.json()
                        row.update(answer=data['answer'],sources=data['sources'])
                        if group: sessions[group] = data['session_id']
                    else: row['error'] = 'Unexpected HTTP response'
        except Exception as exc:
            row['error'] = type(exc).__name__
        row.update(seconds=round(time.monotonic()-begin,2),requests=counts,evidence=evidence)
        report['cases'].append(row)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in row.items() if k not in ('evidence','sources')},ensure_ascii=False),flush=True)
    print('REPORT: ' + str(output),flush=True)

if __name__ == '__main__':
    asyncio.run(main())
