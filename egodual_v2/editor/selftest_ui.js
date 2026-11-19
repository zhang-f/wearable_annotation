// Syntax + cross-panel save regression, with minimal form stubs; not browser E2E.
const fs=require('fs'),path=require('path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
new Function(html.split('<script>')[1].split('</script>')[0]);
const body=html.split('function unsaved(){')[1].split('\nasync function save(')[0];
const gather=new Function('data','dirty','idx','coarseIdx','$','selected','return (function(){'+body+')()');
const names=['summary','verb','hands','type','confidence','object','tool','target','ambiguous','boundaryNote','stepNotes','instruction','description','goalTitle','goalDescription','goalFinal','videoNotes'];
const form=Object.fromEntries(names.map(n=>[n,{value:n,checked:true}]));
const c=gather({},true,2,1,n=>form[n],n=>[n]);
if(c['goal.title']!=='goalTitle'||c['fine[2].summary']!=='summary'||c['coarse[1].instruction']!=='instruction'||c.notes!=='videoNotes')throw Error('Unsaved form changes lost');
console.log('PASS: JavaScript syntax; unsaved step/subtask/video fields collected together');

for(const signature of ['async function load(v){await flushDirty();','async function navigate(i){await flushDirty();','async function renderQueue(){await flushDirty();','async function setMode(){await flushDirty();'])if(!html.includes(signature))throw Error('Missing save guard: '+signature);
console.log('PASS: navigation/mode/queue render guard unsaved changes before selecting items');
