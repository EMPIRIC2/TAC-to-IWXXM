const API_BASE = (typeof window !== 'undefined' && window.METAR_API_BASE) ? window.METAR_API_BASE : '';
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const manualInput = document.getElementById('manualInput');
const convertBtn = document.getElementById('convertBtn');
const clearBtn = document.getElementById('clearBtn');
const zipBtn = document.getElementById('zipBtn');
const resultsDiv = document.getElementById('results');
const spinner = document.getElementById('spinner');

let pendingFiles = [];

function refreshFileList() {
  fileList.innerHTML = '';
  pendingFiles.forEach((f, idx) => {
    const li = document.createElement('li');
    li.textContent = f.name;
    const rm = document.createElement('button');
    rm.textContent = '×';
    rm.title = 'Remove file';
    rm.className = 'secondary';
    rm.onclick = () => { pendingFiles.splice(idx,1); refreshFileList(); };
    li.appendChild(rm);
    fileList.appendChild(li);
  });
  convertBtn.disabled = pendingFiles.length === 0 && manualInput.value.trim() === '';
}

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('keydown', (e) => { if(e.key==='Enter') fileInput.click(); });
fileInput.addEventListener('change', (e) => {
  for (const f of e.target.files) pendingFiles.push(f);
  refreshFileList();
});

['dragenter','dragover'].forEach(ev => dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.add('dragover'); }));
['dragleave','drop'].forEach(ev => dropzone.addEventListener(ev, e => { e.preventDefault(); if(ev==='drop') handleDrop(e); dropzone.classList.remove('dragover'); }));

function handleDrop(e){
  const files = e.dataTransfer.files;
  for (const f of files) pendingFiles.push(f);
  refreshFileList();
}

manualInput.addEventListener('input', refreshFileList);

clearBtn.addEventListener('click', () => {
  pendingFiles = [];
  fileInput.value = '';
  manualInput.value='';
  resultsDiv.innerHTML = '';
  refreshFileList();
});

convertBtn.addEventListener('click', async () => {
  if (pendingFiles.length === 0 && manualInput.value.trim() === '') return;
  spinner.classList.remove('hidden');
  resultsDiv.innerHTML = '';
  convertBtn.disabled = true;
  try {
    const fd = new FormData();
    pendingFiles.forEach(f => fd.append('files', f));
    fd.append('manual_text', manualInput.value);
    const token = sessionStorage.getItem('authToken');
    const resp = await fetch(API_BASE + '/api/convert', { method: 'POST', body: fd, headers: token ? { 'Authorization': 'Bearer ' + token } : {} });
    if (!resp.ok) {
      let detail = await resp.text();
      throw new Error(detail);
    }
    const data = await resp.json();
    if (data.errors && data.errors.length) {
      const warn = document.createElement('div');
      warn.style.color='tomato';
      warn.textContent = 'Some errors: ' + data.errors.join('; ');
      resultsDiv.appendChild(warn);
    }
    (data.results || []).forEach(r => renderResult(r));
  } catch (err) {
    const div = document.createElement('div');
    div.style.color='red';
    div.textContent = 'Conversion failed: ' + err;
    resultsDiv.appendChild(div);
  } finally {
    spinner.classList.add('hidden');
    convertBtn.disabled = false;
  }
});

function renderResult(r){
  const wrapper = document.createElement('div');
  wrapper.className='result-item';
  const header = document.createElement('div');
  header.className='result-header';
  const name = document.createElement('strong');
  name.textContent = r.name;
  header.appendChild(name);
  const btnGroup = document.createElement('div');
  btnGroup.className='btn-group';
  const dlBtn = document.createElement('button');
  dlBtn.textContent='Download';
  dlBtn.onclick = () => downloadText(r.content, r.name);
  const copyBtn = document.createElement('button');
  copyBtn.textContent='Copy';
  copyBtn.onclick = async () => { await navigator.clipboard.writeText(r.content); copyBtn.textContent='Copied'; setTimeout(()=>copyBtn.textContent='Copy',1500); };
  btnGroup.appendChild(dlBtn); btnGroup.appendChild(copyBtn); header.appendChild(btnGroup);
  const code = document.createElement('div');
  code.className='code-block';
  code.textContent = r.content;
  wrapper.appendChild(header); wrapper.appendChild(code);
  resultsDiv.appendChild(wrapper);
}

function downloadText(text, filename){
  const blob = new Blob([text], {type:'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; document.body.appendChild(a); a.click();
  setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 500);
}

zipBtn.addEventListener('click', async ()=>{
  if (pendingFiles.length === 0 && manualInput.value.trim() === '') return;
  spinner.classList.remove('hidden');
  try {
    const fd = new FormData();
    pendingFiles.forEach(f => fd.append('files', f));
    fd.append('manual_text', manualInput.value);
    const token = sessionStorage.getItem('authToken');
    const resp = await fetch(API_BASE + '/api/convert-zip', { method: 'POST', body: fd, headers: token ? { 'Authorization': 'Bearer ' + token } : {} });
    if(!resp.ok){
      throw new Error(await resp.text());
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'iwxxm_batch.zip'; document.body.appendChild(a); a.click();
    setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 500);
  } catch(err){
    const div = document.createElement('div');
    div.style.color='red';
    div.textContent='ZIP conversion failed: ' + err;
    resultsDiv.appendChild(div);
  } finally {
    spinner.classList.add('hidden');
  }
});

refreshFileList();