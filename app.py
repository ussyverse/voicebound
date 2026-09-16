import asyncio, hashlib, json, os, secrets, sqlite3, time
from pathlib import Path
from urllib.parse import urlparse
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import providers
from story import CAST, fresh, view, investigate, accuse, message

load_dotenv()
ROOT=Path(__file__).resolve().parent
DATA=Path(os.getenv('VOICEBOUND_DATA',str(ROOT/'.runtime')))
DATA.mkdir(parents=True,exist_ok=True);os.chmod(DATA,0o700)
DB=DATA/'cases.sqlite3'

def connect():
 db=sqlite3.connect(DB);db.execute('CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, body TEXT NOT NULL)');db.execute('CREATE TABLE IF NOT EXISTS budget (sid TEXT, kind TEXT, bucket INTEGER, n INTEGER, PRIMARY KEY(sid,kind,bucket))');db.commit();return db

def read(sid):
 with connect() as db:r=db.execute('SELECT body FROM cases WHERE id=?',(sid,)).fetchone()
 if not r:raise HTTPException(404,'Case not found. Start a new case.')
 return json.loads(r[0])

def save(sid,state):
 with connect() as db:db.execute('INSERT OR REPLACE INTO cases VALUES (?,?)',(sid,json.dumps(state)));db.commit()

def charge(sid,kind,limit):
 bucket=int(time.time()//3600)
 with connect() as db:
  db.execute('BEGIN IMMEDIATE')
  db.execute('DELETE FROM budget WHERE bucket<?',(bucket-24,))
  for who,cap in [(sid,limit),('*',limit*5)]:
   row=db.execute('SELECT n FROM budget WHERE sid=? AND kind=? AND bucket=?',(who,kind,bucket)).fetchone()
   if row and row[0]>=cap:raise HTTPException(429,'Hourly prototype quota reached. Please wait.')
   db.execute('INSERT INTO budget VALUES (?,?,?,1) ON CONFLICT(sid,kind,bucket) DO UPDATE SET n=n+1',(who,kind,bucket))
  db.commit()

locks={};voice_lock=asyncio.Lock();inference_slots=asyncio.Semaphore(2)
app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)

@app.middleware('http')
async def guard(request,call_next):
 host=request.headers.get('host','')
 allowed=os.getenv('VOICEBOUND_ALLOWED_HOSTS','127.0.0.1,localhost').split(',')
 if host.split(':')[0] not in allowed:return JSONResponse({'detail':'Host not allowed'},400)
 if request.method not in ('GET','HEAD','OPTIONS'):
  origin=request.headers.get('origin')
  if request.headers.get('x-voicebound')!='1' or (origin and urlparse(origin).netloc!=host) or request.headers.get('sec-fetch-site')=='cross-site':return JSONResponse({'detail':'Same-origin request required'},403)
  if int(request.headers.get('content-length','0') or 0)>5*1024*1024+65536:return JSONResponse({'detail':'Request too large'},413)
 response=await call_next(request)
 response.headers['X-Content-Type-Options']='nosniff'
 response.headers['Referrer-Policy']='no-referrer'
 response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
 if request.url.path.startswith('/api'):response.headers['Cache-Control']='no-store'
 return response

@app.exception_handler(providers.ProviderError)
async def provider_error(request,exc):return JSONResponse({'detail':str(exc)},503)

def sid(request):
 value=request.cookies.get('voicebound')
 if not value or len(value)!=64:raise HTTPException(401,'Start a case first.')
 read(value);return value

@app.get('/')
def index():return FileResponse(ROOT/'static/index.html')

@app.get('/api/status')
def status():return {'text_only':os.getenv('VOICEBOUND_TEXT_ONLY')=='1','providers':providers.config(),'voice_complete':False,'note':'AssemblyAI voice path requires live verification; typed play alone is not the sponsor demo.'}

@app.post('/api/new')
def new(request:Request):
 charge('new','cases',10)
 s=secrets.token_hex(32);state=fresh();save(s,state)
 r=JSONResponse(view(state));r.set_cookie('voicebound',s,httponly=True,samesite='strict',secure=request.url.scheme=='https',max_age=86400*7);return r

@app.get('/api/state')
def state(request:Request):return view(read(sid(request)))

class Action(BaseModel):
 kind:str=Field(max_length=20)
 target:str=Field(default='',max_length=30)
 text:str=Field(default='',max_length=1000)
 revision:int=Field(ge=0)

@app.post('/api/action')
async def action(a:Action,request:Request):
 s=sid(request)
 lock=locks.setdefault(s,asyncio.Lock())
 if lock.locked():raise HTTPException(409,'A turn is already running.')
 async with lock:
  state=read(s)
  if a.revision!=state['revision']:raise HTTPException(409,'Case changed; reload before trying again.')
  if state['ending']:raise HTTPException(409,'Case ended; start a new case.')
  if state['turns']>=60:raise HTTPException(429,'This case has reached its 60-turn limit.')
  try:
   if a.kind=='inspect':investigate(state,a.target)
   elif a.kind=='accuse':accuse(state,a.target)
   elif a.kind=='ask':
    if a.target not in CAST or not a.text.strip():raise ValueError('Select a suspect and enter a question.')
    charge(s,'inference',30)
    async with inference_slots:text,audit=await providers.dialogue(state,a.target,a.text.strip())
    state['messages'].extend([message('you',a.text.strip()),message(a.target,text,audit=audit)])
   else:raise ValueError('Unknown action')
  except ValueError as e:raise HTTPException(422,str(e))
  state['revision']+=1;state['turns']+=1;save(s,state);return view(state)

@app.post('/api/transcribe')
async def transcribe(request:Request,audio:UploadFile=File(...)):
 s=sid(request)
 if audio.content_type not in ('audio/webm','audio/ogg','audio/mp4','audio/wav','audio/x-wav'):raise HTTPException(415,'Unsupported recording type')
 data=await audio.read(5*1024*1024+1);await audio.close()
 if not data or len(data)>5*1024*1024:raise HTTPException(413,'Audio must be between 1 byte and 5 MiB')
 charge(s,'transcription',15)
 # Never accepts a user-supplied remote URL. Transcript does not mutate game state.
 async with inference_slots:return await providers.transcribe(data)

@app.post('/api/audio/{mid}')
async def audio(mid:str,request:Request):
 s=sid(request);state=read(s)
 m=next((x for x in state['messages'] if x['id']==mid),None)
 if not m or m['speaker'] not in CAST:raise HTTPException(404,'No speakable character line in this case.')
 recipe=state['voices'][m['speaker']]
 key=hashlib.sha256(json.dumps([m['text'],recipe],sort_keys=True).encode()).hexdigest()
 cache=DATA/'audio';cache.mkdir(exist_ok=True)
 target=cache/(key+'.wav')
 async with voice_lock:
  if not target.exists():
   charge(s,'speech',20)
   data=await providers.synthesize(m['text'],recipe)
   # Bound completed local cache by evicting oldest files before adding a new one.
   files=sorted(cache.glob('*.wav'),key=lambda p:p.stat().st_mtime)
   total=sum(p.stat().st_size for p in files)
   while files and total+len(data)>64*1024*1024:
    old=files.pop(0);total-=old.stat().st_size;old.unlink()
   temp=target.with_suffix('.tmp');temp.write_bytes(data);temp.replace(target)
  data=target.read_bytes()
 return Response(data,media_type='audio/wav')

app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
