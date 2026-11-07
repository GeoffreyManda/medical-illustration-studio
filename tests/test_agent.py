import json
import pytest,httpx
from medillustrate import agent,core
from medillustrate.workspace import Store,new_project,get_frame

@pytest.mark.parametrize('command',['show contours','show values','show colour','hide labels','show labels','less texture','restore texture','labels 19','title: New title','rename cortex: Cortical tissue','move cortex left 330','add atlas-kidney-surface'])
def test_local_command_is_bounded(command):assert agent.local_commands(command,new_project())['operations']

def test_unknown_freeform_does_not_fake_model():
 with pytest.raises(core.IllustrationError):agent.local_commands('Make it absolutely Netter quality',new_project())

@pytest.mark.parametrize('op',[{'op':'geometry_lock','value':False},{'op':'label','landmark':'cortex','values':{'target':[.4,.3],'target_note':'model guessed'}}])
def test_models_cannot_unlock_or_guess_landmarks(op):
 with pytest.raises(core.IllustrationError):agent.check_agent_operations([op])

def test_ollama_real_adapter_with_mock_response(tmp_path,monkeypatch):
 monkeypatch.setenv('MEDILLUSTRATE_OLLAMA_MODEL','test-model');s=Store(tmp_path/'a.db');p=s.create()['project']['id'];calls=[]
 def handler(req):
  calls.append(req);payload=json.loads(req.content);assert payload['stream'] is False and payload['format']['type']=='object'
  return httpx.Response(200,json={'message':{'content':json.dumps({'summary':'Larger labels','operations':[{'op':'label_size','value':19}],'warnings':[]})}})
 with httpx.Client(transport=httpx.MockTransport(handler)) as client:
  q=agent.propose(s,p,1,'Increase label size','ollama',consent=True,client=client)
 assert len(calls)==1;assert s.get(p)['version']==1;assert q['provider']=='Ollama: test-model'

def test_no_model_call_without_consent(tmp_path,monkeypatch):
 monkeypatch.setenv('MEDILLUSTRATE_OLLAMA_MODEL','test-model');s=Store(tmp_path/'a.db');p=s.create()['project']['id']
 with pytest.raises(core.IllustrationError):agent.propose(s,p,1,'edit','ollama')


class ScriptedEngine:
 def __init__(self,responses):self.responses=iter(responses);self.calls=[]
 def invoke(self,data):
  self.calls.append(data)
  return {'choices':[{'message':next(self.responses)}]}

def tool(name,args):
 return {'id':'call-1','type':'function','function':{'name':name,'arguments':json.dumps(args)}}

def test_subscription_agent_validates_repairs_and_requires_acceptance(tmp_path):
 s=Store(tmp_path/'composer.db');pid=s.create()['project']['id']
 engine=ScriptedEngine([
  {'role':'assistant','content':'Inspecting','tool_calls':[tool('inspect_artboard',{})]},
  {'role':'assistant','content':'Editing','tool_calls':[tool('propose_changes',{'summary':'Invalid size','operations':[{'op':'label_size','value':99}],'warnings':[]})]},
  {'role':'assistant','content':'Correcting','tool_calls':[tool('propose_changes',{'summary':'Readable labels','operations':[{'op':'label_size','value':19}],'warnings':[]})]}
 ])
 q=agent.compose(s,pid,1,'Make labels easier to read',consent=True,engine=engine)
 assert len(engine.calls)==3
 assert q['trace'][0]=='Inspected current artboard' and q['trace'][1].startswith('Validation requested a correction:') and q['trace'][-1]=='Validated editing proposal'
 assert s.get(pid)['version']==1
 assert len(agent.composer_history(s,pid))==1
 assert any(m.get('role')=='tool' and 'error' in m.get('content','') for m in engine.calls[-1]['messages'])
 accepted=s.decide(pid,q['id'],True)
 assert accepted['version']==2 and get_frame(accepted['project'])['document']['label_size']==19

def test_subscription_does_not_fallback_or_call_without_consent(tmp_path):
 s=Store(tmp_path/'composer.db');pid=s.create()['project']['id'];engine=ScriptedEngine([])
 with pytest.raises(core.IllustrationError,match='Authorize'):agent.compose(s,pid,1,'Make an edit',engine=engine)
 assert not engine.calls

def test_subscription_question_and_stale_context(tmp_path):
 s=Store(tmp_path/'composer.db');pid=s.create()['project']['id']
 e=ScriptedEngine([{'role':'assistant','content':'This is a kidney section.','tool_calls':[]}])
 r=agent.compose(s,pid,1,'What is shown?',consent=True,engine=e)
 assert r['no_edit'] and s.get(pid)['version']==1
 s.edit(pid,1,[{'op':'title','value':'Manual title'}])
 with pytest.raises(core.IllustrationError,match='changed'):agent.compose(s,pid,1,'Edit',consent=True,engine=e)

def test_subscription_cancel_prevents_proposal(tmp_path):
 s=Store(tmp_path/'composer.db');pid=s.create()['project']['id'];run='cancel-test-id'
 class CancelledEngine:
  def invoke(self,data):
   with agent.RUN_LOCK:agent.RUNS[run]['cancel'].set()
   return {'choices':[{'message':{'content':'stopped','tool_calls':[]}}]}
 with pytest.raises(core.IllustrationError,match='stopped'):agent.compose(s,pid,1,'Edit',consent=True,run_id=run,engine=CancelledEngine())
 assert s.get(pid)['version']==1 and not agent.composer_history(s,pid)
