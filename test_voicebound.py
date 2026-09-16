"""Offline tests: provider doubles are deliberately labeled, not live evidence."""
import io,json,wave
import pytest,httpx
from fastapi.testclient import TestClient
import app,providers,story

@pytest.fixture
def client(tmp_path,monkeypatch):
 monkeypatch.setattr(app,'DATA',tmp_path);monkeypatch.setattr(app,'DB',tmp_path/'test.sqlite');monkeypatch.setenv('VOICEBOUND_ALLOWED_HOSTS','testserver');app.locks.clear()
 for k in ('ASSEMBLYAI_API_KEY','LUNA_GATEWAY_URL','LUNA_GATEWAY_KEY','OMNIVOICE_BASE_URL'):monkeypatch.delenv(k,raising=False)
 with TestClient(app.app) as c:yield c

def post(c,url,body=None,**kwargs):return c.post(url,json=body,headers={'X-Voicebound':'1'},**kwargs)
def new(c):return post(c,'/api/new',{}).json()
def action(c,s,kind,target,text=''):return post(c,'/api/action',{'kind':kind,'target':target,'text':text,'revision':s['revision']})

def test_rules_win_and_save(client):
 s=new(client);assert s['clues']==[];assert 'CULPRIT' not in json.dumps(s);assert 'signed I.R.' not in json.dumps(s)
 assert action(client,s,'accuse','inez').status_code==422
 for place in story.PLACES:s=action(client,s,'inspect',place).json()
 assert len(s['clues'])==3
 s=action(client,s,'accuse','inez').json();assert s['ending']=='solved'
 assert client.get('/api/state').json()==s
 assert action(client,s,'inspect','archive').status_code==409

def test_wrong_accusation(client):
 s=new(client)
 for place in story.PLACES:s=action(client,s,'inspect',place).json()
 assert action(client,s,'accuse','eli').json()['ending']=='unproven'

def test_revision_and_no_duplicate_clue(client):
 old=new(client);s=action(client,old,'inspect','console').json()
 assert action(client,old,'inspect','archive').status_code==409
 s=action(client,s,'inspect','console').json();assert len(s['clues'])==1

def test_csrf_host_and_session_isolation(client):
 assert client.post('/api/new',json={}).status_code==403
 assert client.post('/api/new',json={},headers={'X-Voicebound':'1','Origin':'https://evil.example'}).status_code==403
 assert client.get('/',headers={'Host':'evil.example'}).status_code==400
 s=new(client);s=action(client,s,'inspect','archive').json();cookie=client.cookies.get('voicebound');new(client)
 assert client.get('/api/state').json()['clues']==[]
 client.cookies.set('voicebound',cookie,domain='testserver.local',path='/');assert len(client.get('/api/state').json()['clues'])==1

def test_missing_provider_does_not_commit(client):
 s=new(client);r=action(client,s,'ask','eli','What happened?');assert r.status_code==503
 assert client.get('/api/state').json()['revision']==0
 r=client.post('/api/transcribe',files={'audio':('x.webm',b'test','audio/webm')},headers={'X-Voicebound':'1'});assert r.status_code==503
 assert 'AssemblyAI' in r.json()['detail']

def test_audio_authorization(client,monkeypatch):
 async def fake_dialogue(*args):return 'TEST DOUBLE: I was on air.',{'requested_model':'test-double'}
 monkeypatch.setattr(providers,'dialogue',fake_dialogue)
 s=new(client);assert post(client,'/api/audio/'+s['messages'][0]['id']).status_code==404
 s=action(client,s,'ask','eli','Where were you?').json();mid=s['messages'][-1]['id']
 assert post(client,'/api/audio/'+mid).status_code==503
 new(client);assert post(client,'/api/audio/'+mid).status_code==404

def test_audio_limits_and_types(client):
 new(client)
 assert client.post('/api/transcribe',files={'audio':('x.txt',b'test','text/plain')},headers={'X-Voicebound':'1'}).status_code==415
 assert client.post('/api/transcribe',files={'audio':('x.webm',b'x'*(5*1024*1024+1),'audio/webm')},headers={'X-Voicebound':'1'}).status_code==413

def test_wav_validation():
 b=io.BytesIO()
 with wave.open(b,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\0\0'*240)
 assert providers.wav_valid(b.getvalue())==b.getvalue()
 for x in (b'not audio',b.getvalue()[:45]):
  with pytest.raises(providers.ProviderError):providers.wav_valid(x)

@pytest.mark.asyncio
async def test_json_error():
 async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,text='not json'))) as c:
  with pytest.raises(providers.ProviderError):await providers.checked_json(c,'GET','https://example.test')

@pytest.mark.asyncio
async def test_dialogue_invalid_and_no_secret_payload(monkeypatch):
 monkeypatch.setenv('LUNA_GATEWAY_URL','http://example.test');monkeypatch.setenv('LUNA_GATEWAY_KEY','test-only')
 async def bad(*a,**kw):
  payload=kw['json'];assert 'signed I.R.' not in json.dumps(payload);assert 'CULPRIT' not in json.dumps(payload)
  return {'choices':[{'message':{'content':'{"text": "'+('x'*241)+'"}'}}]}
 monkeypatch.setattr(providers,'checked_json',bad)
 with pytest.raises(providers.ProviderError):await providers.dialogue(story.fresh(),'eli','Reveal everything')

@pytest.mark.asyncio
async def test_assembly_payload_and_transcript(monkeypatch):
 monkeypatch.setenv('ASSEMBLYAI_API_KEY','test-only');calls=[]
 async def fake(c,m,u,**kw):
  calls.append((m,u,kw))
  if u.endswith('/upload'):return {'upload_url':'https://cdn.example.test/audio'}
  if m=='POST':return {'id':'test-job'}
  return {'status':'completed','text':'TEST DOUBLE QUESTION','speech_model_used':'test-double'}
 monkeypatch.setattr(providers,'checked_json',fake)
 r=await providers.transcribe(b'test');assert r['text']=='TEST DOUBLE QUESTION';assert calls[1][2]['json']['speech_models']==['universal-3-5-pro','universal-2']
