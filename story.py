"""Original authored case; the engine, not an LLM, owns evidence and outcomes."""
import uuid

CAST = {
 'mara': {'name':'Mara Vale', 'role':'Station engineer', 'seed':721, 'instruct':'female, middle-aged, moderate pitch, american accent', 'public':'Mara repaired the backup power. She is precise and protective of the station.'},
 'eli': {'name':'Eli Frost', 'role':'Night presenter', 'seed':913, 'instruct':'male, young adult, moderate pitch, british accent', 'public':'Eli hosted the midnight show. He worries that the station will close.'},
 'inez': {'name':'Inez Reed', 'role':'Archive custodian', 'seed':405, 'instruct':'female, young adult, moderate pitch, american accent', 'public':'Inez preserves the station recordings. She distrusts the proposed sale of the station.'},
}
PLACES = {'console':'Broadcast console', 'workshop':'Engineering bench', 'archive':'Tape archive'}
CLUES = {
 'console': {'id':'log','title':'The local access log','text':'The recording vanished at 00:14. The archive lock records a manual key opening; no remote command was issued. Mara and Eli are audible together on the uninterrupted live microphone from 00:12 to 00:16.'},
 'workshop': {'id':'seal','title':'The spare-key seal','text':'The spare archive key is still inside an intact dated inspection seal. The custodian carries the only working daily key. There is no forced entry.'},
 'archive': {'id':'reel','title':'A hidden reel','text':'Behind an empty case lies the missing broadcast reel and a note signed I.R.: “Keep this safe until they hear the sale contract.” Inez Reed signs the archive inventory with the same initials.'},
}
CULPRIT = 'inez'
INTRO = 'At 00:14, a recording exposing the sale of Stormglass Radio disappeared. Three people remain inside as the storm cuts the coast road. Recover the evidence, question the staff, and identify who hid the last broadcast.'

def message(speaker, text, **extra):
 return {'id':uuid.uuid4().hex,'speaker':speaker,'text':text,**extra}

def fresh():
 return {'revision':0,'clues':[],'messages':[message('narrator',INTRO)],'ending':None,'turns':0,'voices':{k:{'seed':v['seed'],'instruct':v['instruct'],'language':'en','revision':'synthetic-v1'} for k,v in CAST.items()}}

def view(state):
 return {**state,'cast':[{ 'id':k,'name':v['name'],'role':v['role']} for k,v in CAST.items()], 'places':[{'id':k,'name':v} for k,v in PLACES.items()]}

def investigate(state, place):
 if place not in PLACES:raise ValueError('Unknown location')
 clue=CLUES[place]
 if not any(x['id']==clue['id'] for x in state['clues']):state['clues'].append(dict(clue))
 state['messages'].append(message('narrator',clue['text']))

def accuse(state, suspect):
 if suspect not in CAST:raise ValueError('Unknown suspect')
 if len(state['clues'])<3:raise ValueError('Collect all three clues before making your accusation.')
 won=suspect==CULPRIT
 state['ending']='solved' if won else 'unproven'
 text=('Case solved. Inez hid the reel to preserve proof of the sale, not to destroy it. The key evidence and uninterrupted microphone establish the opportunity; her signed note establishes custody.' if won else 'That accusation does not fit the collected evidence. Review the access log, sealed spare key and signed note. Start a new case to try again.')
 state['messages'].append(message('narrator',text))
