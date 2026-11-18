'use strict';
const $ = id => document.getElementById(id);
let csrf = document.querySelector('meta[name=csrf-token]').content;
let pools = [], records = {}, view = 'infrastructure', pendingAction = null;
const titles = {infrastructure:'Infrastructure',VM:'Virtual machines',host:'Hosts',SR:'Storage',network:'Networks',task:'Tasks',help:'Help & documentation',about:'About Flagship Web'};
const labels = {start:'Start',clean_shutdown:'Shut down',clean_reboot:'Reboot',hard_shutdown:'Force shut down',hard_reboot:'Force reboot',suspend:'Suspend',resume:'Resume',snapshot:'Take snapshot',clone:'Clone',rename:'Rename',folder:'Set folder'};
function node(tag, text, cls) {const el=document.createElement(tag); if(text !== undefined) el.textContent=String(text); if(cls) el.className=cls; return el;}
function fail(error) {$('error').textContent=error.message || String(error); $('error').hidden=false;}
async function api(path, method='GET', body) {
  const response=await fetch('/api'+path,{method,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:body===undefined?undefined:JSON.stringify(body)});
  const result=await response.json();
  if(!response.ok) {if(response.status===401 && path!=='/login') location.reload(); throw new Error(result.error || 'Request failed');}
  return result;
}
async function task(fn) { $('error').hidden=true; try {await fn();} catch(error) {fail(error);} }
function announce(text) {$('notice').textContent=text; $('notice').hidden=!text;}
function selected() {return $('pool-select').value;}
async function state(prefer) {
  pools=(await api('/state')).pools;
  const current=prefer || selected(); $('pool-select').replaceChildren(node('option','Choose a connection'));
  $('pool-select').firstChild.value='';
  pools.forEach(p=>{const o=node('option',p.name+(p.demo?' · DEMO':''));o.value=p.id;$('pool-select').append(o);});
  $('pool-select').value=pools.some(p=>p.id===current)?current:(pools[0]?.id || '');
  await refresh();
}
async function refresh() {
  records={};
  if(selected()) {
    const result=await api('/pools/'+encodeURIComponent(selected())+'/inventory'); records=result.records;
    const demo=pools.find(p=>p.id===selected())?.demo;
    announce((demo?'OFFLINE DEMO — simulated data and actions; no host connection. ':'')+Object.entries(result.errors).map(([k,v])=>k+': '+v).join(' · '));
  } else announce('Connect a host or pool, or explore the offline demo.');
  render();
}
function render() {
  $('view-title').textContent=titles[view];
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  $('overview').hidden=view!=='infrastructure'; $('inventory').hidden=!['VM','host','SR','network','task'].includes(view); $('help').hidden=view!=='help'; $('about').hidden=view!=='about';
  $('pool-bar').hidden=['help','about'].includes(view); $('add-pool').hidden=['help','about'].includes(view);
  $('stats').replaceChildren();
  [['HOSTS',records.host?.length||0],['VIRTUAL MACHINES',records.VM?.filter(v=>!v.is_control_domain&&!v.is_a_template).length||0],['STORAGE REPOSITORIES',records.SR?.length||0],['RUNNING VMS',records.VM?.filter(v=>v.power_state==='Running'&&!v.is_control_domain).length||0]].forEach(([title,count])=>{const c=node('div',undefined,'stat');c.append(node('strong',count),node('span',title));$('stats').append(c);});
  $('connection-list').replaceChildren();
  pools.forEach(p=>{const c=node('div',undefined,'connection'), description=node('div');description.append(node('strong',p.name),node('small',p.endpoint));c.append(node('span','◈'),description,node('span',p.demo?'DEMO':'TLS XAPI','tag'));$('connection-list').append(c);});
  if(!$('inventory').hidden) table();
}
function table() {
  const columns={VM:['Name / UUID','Power','Folder / tags','Operation'],host:['Name / UUID','Address','Enabled'],SR:['Name / UUID','Type','Used / capacity'],network:['Name / UUID','Bridge'],task:['Name / UUID','Status','Progress']}[view];
  const heading=node('tr');columns.forEach(c=>heading.append(node('th',c)));$('table-head').replaceChildren(heading);$('table-body').replaceChildren();
  const query=$('search').value.toLowerCase();
  const rows=(records[view]||[]).filter(r=>JSON.stringify(r).toLowerCase().includes(query));
  rows.forEach(r=>{const row=node('tr'), name=node('td',r.name_label||'(unnamed)');name.append(node('small',r.uuid));row.append(name);
    if(view==='VM') {
      row.append(node('td',r.power_state),node('td',(r.folder||'Unfiled')+(r.tags?.length?' · '+r.tags.join(', '):'')));
      const cell=node('td');
      if(!r.is_a_template&&!r.is_control_domain) {
        const options=node('select');options.setAttribute('aria-label','Operation for '+r.name_label);const empty=node('option','Choose operation…');empty.value='';options.append(empty);
        Object.entries(labels).forEach(([value,text])=>{const o=node('option',text);o.value=value;options.append(o);});
        options.addEventListener('change',()=>{if(!options.value)return; pendingAction={pool:selected(),ref:r.ref,action:options.value,confirm:r.name_label};$('action-title').textContent=labels[options.value];$('action-target').textContent='Target: '+r.name_label+ (pools.find(p=>p.id===selected())?.demo?' (offline demo)':'');$('value-label').hidden=!['snapshot','clone','rename','folder'].includes(options.value);$('action-value').required=['snapshot','clone','rename'].includes(options.value);$('action-value').value='';$('action-confirm').value='';$('action-dialog').showModal();options.value='';});cell.append(options);
      } else cell.textContent=r.is_control_domain?'Control domain':'Template'; row.append(cell);
    } else if(view==='host') row.append(node('td',r.address),node('td',r.enabled?'Yes':'No'));
    else if(view==='SR') row.append(node('td',r.type),node('td',gib(r.physical_utilisation)+' / '+gib(r.physical_size)));
    else if(view==='network') row.append(node('td',r.bridge));
    else row.append(node('td',r.status),node('td',Math.round(Number(r.progress||0)*100)+'%'));
    $('table-body').append(row);
  });
  if(!rows.length){const cell=node('td',selected()?'No matching objects.':'Choose a host or pool first.');cell.colSpan=columns.length;const row=node('tr');row.append(cell);$('table-body').append(row);}
}
function gib(value) {return (Number(value||0)/1073741824).toFixed(1)+' GiB';}
let articles=[];
function help() {const q=$('help-search').value.toLowerCase();$('articles').replaceChildren();articles.filter(a=>(a.title+a.content).toLowerCase().includes(q)).forEach(a=>{const article=node('article',undefined,'card article');article.append(node('h2',a.title),node('pre',a.content));$('articles').append(article);});}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>task(async()=>{view=b.dataset.view;render();if(view==='help'){articles=(await api('/help')).articles;help();}})));
$('login').addEventListener('submit',e=>{e.preventDefault();task(async()=>{const result=await api('/login','POST',{username:$('username').value,password:$('password').value});$('password').value='';csrf=result.csrf;$('login-panel').hidden=true;$('workspace').hidden=false;$('account').hidden=false;await state();});});
$('logout').addEventListener('click',()=>task(async()=>{await api('/logout','POST',{});location.reload();}));
$('refresh').addEventListener('click',()=>task(refresh));$('pool-select').addEventListener('change',()=>task(refresh));
$('demo').addEventListener('click',()=>task(async()=>{const result=await api('/pools','POST',{demo:true});await state(result.id);}));
$('disconnect').addEventListener('click',()=>task(async()=>{if(!selected())return;await api('/pools/'+encodeURIComponent(selected()),'DELETE',{});await state();}));
$('add-pool').addEventListener('click',()=>{$('connect').reset();$('connect-dialog').showModal();});
document.querySelectorAll('.cancel').forEach(b=>b.addEventListener('click',()=>{const d=b.closest('dialog');d.querySelectorAll('input[type=password]').forEach(i=>i.value='');d.close();}));
$('connect-dialog').addEventListener('cancel',()=>{$('connect').elements.password.value='';});
$('connect').addEventListener('submit',e=>{e.preventDefault();task(async()=>{const form=$('connect'),body=Object.fromEntries(new FormData(form));form.elements.password.value='';const button=form.querySelector('[type=submit]');button.disabled=true;try{const result=await api('/pools','POST',body);$('connect-dialog').close();await state(result.id);}finally{button.disabled=false;}});});
$('action-form').addEventListener('submit',e=>{e.preventDefault();task(async()=>{if($('action-confirm').value!==pendingAction.confirm)throw new Error('The VM name must match exactly.');const button=$('action-form').querySelector('[type=submit]');button.disabled=true;try{const result=await api('/pools/'+encodeURIComponent(pendingAction.pool)+'/actions','POST',{...pendingAction,value:$('action-value').value});$('action-dialog').close();await refresh();announce(result.message);}finally{button.disabled=false;}});});
$('search').addEventListener('input',table);$('help-search').addEventListener('input',help);
// Resume only an existing authenticated local browser session.
fetch('/api/state').then(r=>{if(r.ok){$('login-panel').hidden=true;$('workspace').hidden=false;$('account').hidden=false;return task(()=>state());}}).catch(()=>{});
