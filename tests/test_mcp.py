import json,subprocess,sys
from medillustrate.mcp_server import dispatch,call_tool,TOOLS
from medillustrate.workspace import Store

def test_mcp_read_propose_no_self_approval(tmp_path):
 s=Store(tmp_path/'s.db');p=s.create()['project']['id'];res=dispatch(s,{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}});assert res['result']['protocolVersion']=='2025-11-25'
 q=call_tool(s,'propose_edits',{'project_id':p,'base_version':1,'summary':'Edit','operations':[{'op':'label_size','value':19}]});assert q['id'];assert s.get(p)['version']==1
 assert not any(t['name'] in {'accept','decide','accept_proposal'} for t in TOOLS)

def test_stdio_protocol_has_no_log_contamination(tmp_path):
 messages=[{'jsonrpc':'2.0','id':1,'method':'tools/list'},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'ping'}]
 r=subprocess.run([sys.executable,'-m','medillustrate.mcp_server','--db',str(tmp_path/'m.db')],input='\n'.join(json.dumps(m) for m in messages)+'\n',text=True,capture_output=True,timeout=10)
 rows=[json.loads(x) for x in r.stdout.splitlines()];assert len(rows)==2 and rows[1]['result']=={} and not r.stderr
