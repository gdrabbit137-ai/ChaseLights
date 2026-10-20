import {ARCHIVE_SHA256, HOURLY_FIELDS, displayHourlyCell, inspectHourlyArtifact, taipeiTime} from './hourly-weather.mjs';

const words = {
  'zh-TW': {
    title:'七星潭 · 72 小時逐時天氣歷史樣本', scope:'離線封存展示 · 非目前或未來天氣預報',
    loading:'正在載入離線歷史樣本…', available:'資料可供檢視', stale:'歷史／已過期',
    unavailable:'離線樣本未提供', partial:'資料不完整', error:'樣本無法驗證',
    notEvaluable:'不可評估攝影條件', retry:'重新載入樣本',
    explanation:'這是 2026 年 10 月 19 日擷取的一次性網格預報，逐時時間只表示當時預報的有效時間。不可當作今日天氣、拍攝建議或導航資訊。',
    retrieved:'擷取完成（台灣時間）', issued:'模型發行／更新時間', unknown:'來源未提供',
    valid:'原預報有效時間（台灣時間）', previous:'降雨量與降雨機率代表此前一小時（起點不含、終點包含）',
    missing:'缺值', sample:'景點代表取樣點；非攝影機位或海岸實測站。海岸風場與海平線未校正。',
    source:'來源', licence:'授權', transformation:'處理說明', limitations:'資料限制',
    fields:{temperature_2m:'2 公尺氣溫',dew_point_2m:'2 公尺露點',relative_humidity_2m:'2 公尺相對濕度',cloud_cover_low:'低雲量',cloud_cover_mid:'中雲量',cloud_cover_high:'高雲量',wind_speed_10m:'10 公尺風速',visibility:'能見度',precipitation:'前一小時降雨量',precipitation_probability:'前一小時降雨機率'}
  },
  en: {
    title:'Qixingtan · 72-hour historical hourly weather sample',scope:'Offline archive display · Not current or future weather',
    loading:'Loading the offline historical sample…',available:'Data available to inspect',stale:'Historical / expired',
    unavailable:'Offline sample unavailable',partial:'Incomplete data',error:'Sample could not be verified',
    notEvaluable:'Photography conditions not evaluable',retry:'Reload sample',
    explanation:'This is a one-time grid forecast retrieved on 19 October 2026. Hourly times show when that old forecast was valid. Do not treat it as today’s weather, shooting advice or navigation.',
    retrieved:'Retrieved (Taipei time)',issued:'Model issue / update time',unknown:'Not supplied by source',
    valid:'Original forecast valid time (Taipei time)',previous:'Rain and rain probability cover the preceding hour (open start, closed end)',
    missing:'Unavailable',sample:'Representative place sample; not a camera position or coastal station. Coastal wind and horizon conditions are uncalibrated.',
    source:'Source',licence:'Licence',transformation:'Transformations',limitations:'Limitations',
    fields:{temperature_2m:'2 m temperature',dew_point_2m:'2 m dew point',relative_humidity_2m:'2 m relative humidity',cloud_cover_low:'Low cloud cover',cloud_cover_mid:'Mid cloud cover',cloud_cover_high:'High cloud cover',wind_speed_10m:'10 m wind speed',visibility:'Visibility',precipitation:'Preceding-hour precipitation',precipitation_probability:'Preceding-hour precipitation probability'}
  },
  ja: {
    title:'七星潭 · 過去の72時間分の毎時気象サンプル',scope:'オフライン保存データ · 現在または将来の天気ではありません',
    loading:'過去のオフラインデータを読み込んでいます…',available:'データを閲覧できます',stale:'過去のデータ／期限切れ',
    unavailable:'オフラインデータは未提供です',partial:'データが不完全です',error:'データを検証できません',
    notEvaluable:'撮影条件は評価できません',retry:'データを再読込',
    explanation:'2026年10月19日に一度だけ取得した格子予報です。毎時の時刻は当時の予報対象時刻を示します。今日の天気、撮影の助言、ナビとして利用しないでください。',
    retrieved:'取得完了（台湾時間）',issued:'モデルの発行／更新時刻',unknown:'提供元から未提供',
    valid:'当時の予報対象時刻（台湾時間）',previous:'降水量と降水確率は直前1時間（開始時刻を含まず、終了時刻を含む）',
    missing:'欠損',sample:'撮影地の代表地点であり、撮影位置や海岸の観測所ではありません。海岸の風と水平線の状態は未校正です。',
    source:'出典',licence:'ライセンス',transformation:'変換内容',limitations:'制約',
    fields:{temperature_2m:'2 mの気温',dew_point_2m:'2 mの露点',relative_humidity_2m:'2 mの相対湿度',cloud_cover_low:'下層雲量',cloud_cover_mid:'中層雲量',cloud_cover_high:'上層雲量',wind_speed_10m:'10 mの風速',visibility:'視程',precipitation:'直前1時間の降水量',precipitation_probability:'直前1時間の降水確率'}
  }
};
const el = (tag, className, value) => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (value !== undefined) element.textContent = value;
  return element;
};
function addLine(parent, label, value) {
  const line=el('p','hourly-meta');line.append(el('strong','',label+': '),el('span','',value));parent.append(line);
}
function addLink(parent,label,url,text) {
  const line=el('p','hourly-meta');line.append(el('strong','',label+': '));
  const link=el('a','',text);link.href=url;link.target='_blank';link.rel='noopener noreferrer';line.append(link);parent.append(line);
}
export function initHourlyWeather(root, initialLocale) {
  let locale=initialLocale, result=null, status='LOADING';
  async function load() {
    status='LOADING';render();
    try {
      const response=await fetch('./fixtures/hourly/qixingtan-one-shot-20261019.json',{cache:'no-store'});
      if (!response.ok) {status='UNAVAILABLE';result=null;render();return;}
      const raw=await response.text();
      const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)))].map(x=>x.toString(16).padStart(2,'0')).join('');
      if (digest!==ARCHIVE_SHA256) throw new Error('Archive hash mismatch');
      result=inspectHourlyArtifact(JSON.parse(raw));status=result.state;
    } catch {result=null;status='ERROR';}
    render();
  }
  function render() {
    const w=words[locale],heading=root.querySelector('#hourly-heading'),content=root.querySelector('#hourly-content');
    heading.textContent=w.title;
    content.replaceChildren();
    content.append(el('p','hourly-scope',w.scope));
    const state=el('p','hourly-state',w[status.toLowerCase()]||w.error);
    state.dataset.state=status;state.setAttribute('role','status');content.append(state);
    content.append(el('p','hourly-evaluation',w.notEvaluable));
    content.append(el('p','hourly-explanation',w.explanation));
    if (!result) {
      if(status!=='LOADING') {const retry=el('button','hourly-retry',w.retry);retry.type='button';retry.addEventListener('click',load);content.append(retry);}
      return;
    }
    if(result.partial)content.append(el('p','hourly-partial',w.partial));
    addLine(content,w.retrieved,taipeiTime(result.retrievedAt,locale,{dateStyle:'medium',timeStyle:'short'}));
    addLine(content,w.issued,w.unknown);
    content.append(el('p','hourly-sample',w.sample));
    addLink(content,w.source,result.attribution.provider_url,'Open-Meteo');
    addLink(content,w.licence,result.attribution.licence_url,'CC BY 4.0');
    addLine(content,w.transformation,result.attribution.modifications_i18n[locale]);
    addLine(content,w.limitations,result.limitations[locale]);
    content.append(el('h3','',w.valid),el('p','hourly-interval',w.previous));
    const groups=new Map();
    for(const hour of result.hours) {
      const day=taipeiTime(hour.valid_at_utc,'en-CA',{year:'numeric',month:'2-digit',day:'2-digit'});
      if(!groups.has(day))groups.set(day,[]);
      groups.get(day).push(hour);
    }
    for(const [day,hours] of groups) {
      const group=el('details','hourly-day');
      if(day===groups.keys().next().value)group.open=true;
      group.append(el('summary','',`${day} · ${hours.length} h`));
      const list=el('div','hourly-hours');
      for(const hour of hours) {
        const card=el('details','hourly-hour');
        const time=taipeiTime(hour.valid_at_utc,locale,{hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
        card.append(el('summary','',time));
        const grid=el('dl','hourly-values');
        for(const [key] of HOURLY_FIELDS) {
          const cell=hour.values[key];grid.append(el('dt','',w.fields[key]),el('dd',cell.state==='AVAILABLE'?'':'hourly-missing',displayHourlyCell(cell,locale)||w.missing));
        }
        card.append(grid);list.append(card);
      }
      group.append(list);content.append(group);
    }
  }
  render();void load();
  return {setLocale(next) {if(words[next]){locale=next;render();}}};
}
