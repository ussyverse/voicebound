"""Opt-in real Luna + OmniVoice smoke; writes private evidence under .runtime."""
import json,time,wave,io
from pathlib import Path
import httpx
base='http://127.0.0.1:8901';report={'mocked':False}
with httpx.Client(base_url=base,timeout=360,headers={'X-Voicebound':'1'}) as c:
 r=c.post('/api/new',json={});r.raise_for_status();s=r.json()
 r=c.post('/api/action',json={'kind':'inspect','target':'console','revision':s['revision']});r.raise_for_status();s=r.json()
 start=time.monotonic();r=c.post('/api/action',json={'kind':'ask','target':'eli','text':'The log says you and Mara were on air together. What do you remember?','revision':s['revision']});r.raise_for_status();s=r.json();m=s['messages'][-1]
 report['luna']={'seconds':round(time.monotonic()-start,2),'text':m['text'],'audit':m['audit']}
 start=time.monotonic();r=c.post('/api/audio/'+m['id']);r.raise_for_status()
 with wave.open(io.BytesIO(r.content)) as w:report['omnivoice']={'bytes':len(r.content),'sample_rate':w.getframerate(),'duration_seconds':w.getnframes()/w.getframerate(),'elapsed_seconds':round(time.monotonic()-start,2)}
 for place in ['workshop','archive']:
  r=c.post('/api/action',json={'kind':'inspect','target':place,'revision':s['revision']});r.raise_for_status();s=r.json()
 r=c.post('/api/action',json={'kind':'accuse','target':'inez','revision':s['revision']});r.raise_for_status();s=r.json();assert s['ending']=='solved';assert c.get('/api/state').json()['ending']=='solved';report['ending']=s['ending']
 report['assemblyai']='NOT LIVE TESTED: no API key configured'
 Path('.runtime/live-smoke.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
