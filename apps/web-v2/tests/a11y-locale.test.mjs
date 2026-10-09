import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';

const app = readFileSync(fileURLToPath(new URL('../app.mjs',import.meta.url)), 'utf8');
const html = readFileSync(fileURLToPath(new URL('../index.html',import.meta.url)), 'utf8');
const hooks = {language:'languageAria','source-strip':'provenanceAria',sidebar:'placesAria',detail:'opportunitiesAria'};
const keys = ['pageTitle','skipToContent',...Object.values(hooks)];

function fakeElement() {
  return {
    textContent:'',value:'',placeholder:'',children:[],attrs:{},events:{},
    append(...children){this.children.push(...children)},
    replaceChildren(...children){this.children=[...children]},
    addEventListener(name,callback){this.events[name]=callback},
    setAttribute(name,value){this.attrs[name]=value},
    getAttribute(name){return this.attrs[name]}
  };
}
function mountApp() {
  const elements = new Map();
  const document = {
    title:'',documentElement:{lang:''},
    getElementById(id){if(!elements.has(id))elements.set(id,fakeElement());return elements.get(id)},
    createElement(){return fakeElement()}
  };
  const store = new Map();
  const localStorage = {getItem:key=>store.get(key)??null,setItem:(key,value)=>store.set(key,value)};
  const code = app.replace(/^import\s+[^\n]+\n/gm,'');
  vm.runInNewContext(code,{
    document,localStorage,LOCALES:['zh-TW','en','ja'],
    fetch:async()=>({status:404}),
    importV21Catalog:()=>{throw Error('unexpected import')},
    placeId:()=>null,opportunityId:()=>null,linkedPlaceId:()=>null,
    localized:()=>null,safeUrl:()=>null,navigationAction:()=>null,
    geometryType:()=>null,relationValue:()=>null,runtimeEvaluation:()=>null,associated:()=>null,
    console,Intl,Date,Set,Map
  },{timeout:2000});
  return {document,store,language:document.getElementById('language')};
}

test('HTML exposes accessible i18n hooks without hard-coded English',()=>{
  assert.match(html,/<a\b(?=[^>]*id="skip-link")(?=[^>]*href="#content")(?=[^>]*data-i18n-text="skipToContent")[^>]*>/);
  for(const [id,key] of Object.entries(hooks)){
    const tag=html.match(new RegExp('<[^>]+\\bid="'+id+'"[^>]*>'))?.[0];
    assert.ok(tag, 'missing landmark '+id);
    assert.ok(tag.includes('data-i18n-aria="'+key+'"'), id+' translation hook');
  }
  assert.doesNotMatch(html,/aria-label="(?:Language|Data provenance|Places|Photography opportunities)"/);
  assert.doesNotMatch(html,/>Skip to content<\/a>/);
});

test('all three locales have distinct accessibility copy',()=>{
  const begin=app.indexOf('const copy = '),end=app.indexOf('const researchCopy=');
  assert.ok(begin>=0&&end>begin,'copy dictionary not found');
  const copy=vm.runInNewContext(app.slice(begin,end)+'\ncopy');
  for(const key of keys){
    const values=['zh-TW','en','ja'].map(locale=>copy[locale]?.[key]);
    assert.ok(values.every(v=>typeof v==='string'&&v.trim()),key+' missing');
    assert.equal(new Set(values).size,3,key+' untranslated');
  }
});

test('real change handler updates skip, title, and four ARIA labels on every switch',()=>{
  const {document,language,store}=mountApp();
  const expected={
    'zh-TW':['ChaseLights V2 — 攝影機會研究','跳至主要內容','語言選擇','資料來源與時效','景點清單','攝影題材與研究資料'],
    en:['ChaseLights V2 — Photography research','Skip to main content','Language selection','Data provenance and freshness','Places list','Photography opportunities and research'],
    ja:['ChaseLights V2 — 撮影機会の調査','メインコンテンツへ移動','言語の選択','資料の出典と更新時刻','撮影地一覧','撮影機会と調査資料']
  };
  assert.equal(document.documentElement.lang,'zh-Hant');
  for(const locale of ['zh-TW','en','ja','zh-TW','en']){
    language.value=locale;
    assert.equal(typeof language.events.change,'function');
    language.events.change({target:language});
    const actual=[document.title,document.getElementById('skip-link').textContent,...Object.keys(hooks).map(id=>document.getElementById(id).getAttribute('aria-label'))];
    assert.deepEqual(actual,expected[locale],locale+' left stale accessibility text');
    assert.equal(document.documentElement.lang,locale==='zh-TW'?'zh-Hant':locale);
    assert.equal(store.get('chaselights-v2-locale'),locale);
  }
});
