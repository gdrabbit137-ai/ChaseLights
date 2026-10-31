/* ChaseLights V1 — 攝影題材條件評估 (V2 evaluation bundle, GUIDANCE-only) */
(function () {
  'use strict';

  const BUNDLE_URL = './apps/web-v2/evaluations-latest.json';
  const DETAILS_BASE = './apps/web-v2/evaluations-details/';
  const STATES = ['GUIDANCE_SATISFIED', 'UNFAVORABLE', 'NOT_EVALUABLE'];

  const I18N = {
    'zh-TW': {
      title: '攝影題材條件評估', search: '搜尋景點…', loading: '正在載入評估資料…',
      load_error: '載入失敗，請稍後再試', updated: '評估產生時間',
      hours: '符合時數', next: '下一個符合時段', now: '現在', expand: '展開',
      cond: '條件', value: '現值', threshold: '門檻', verdict: '判定',
      no_data: '此景點目前沒有可評估的題材。', time: '時間', state: '狀態',
      day_prefix: '日', guidance: '本頁顯示攝影條件是否達到門檻。',
      banner: '顯示攝影條件是否達標，供拍攝前評估參考。',
      none: '—',
      metric_names: { cloud_cover_low: '低雲', cloud_cover_mid: '中雲', cloud_cover_high: '高雲', cloud_cover_mid_and_high: '中高雲', cloud_cover_total: '總雲量', wind_speed_10m: '風速', wind_speed_850hpa: '850hPa 風速', precipitation: '降水', aod_550nm: '氣膠光學厚度', visibility: '能見度', relative_humidity_2m: '相對濕度', relative_humidity_925hpa: '相對濕度 925hPa', relative_humidity_850hpa: '相對濕度 850hPa', lcl_height_m_agl: '抬升凝結高度', temperature_delta_850_925_c: 'T850−T925 溫差', sunrise_time_window: '日出時段', sunset_window: '日落時段', golden_hour_window: '黃金時段', blue_hour_window: '藍調時段', astronomical_darkness: '天文黑暗', moon_illumination_fraction: '月照亮百分比', moon_altitude: '月亮高度', moon_target_separation_deg: '月目標角距', moon_illuminance_proxy: '月光照度代理', galactic_core_altitude: '銀河核心高度', water_surface_state: '水面狀態', seasonal_state: '季節狀態', landform_present: '地形地貌存在', river_flow_state: '河川流量狀態' },
      genres: { mountain_view: '山景視野', overlook: '制高點展望', reflection: '水面倒影', cloud_sea: '雲海', sunrise: '日出', sunset: '日落夕景', golden_hour: '黃金時刻', blue_hour_city: '城市藍調', overcast_soft: '陰天柔光', city_night: '城市夜景', night_sky: '夜空星空', seasonal_plant: '季節植物', geological_landform: '地質地景', waterfall: '瀑布' },
      state_labels: { GUIDANCE_SATISFIED: '條件符合', UNFAVORABLE: '條件未符', NOT_EVALUABLE: '資料不足' }
    },
    en: {
      title: 'Genre Condition Assessment', search: 'Search places…', loading: 'Loading evaluations…',
      load_error: 'Load failed, please retry later', updated: 'Generated',
      hours: 'qualifying hours', next: 'next qualifying window', now: 'Now', expand: 'Expand',
      cond: 'Condition', value: 'Value', threshold: 'Threshold', verdict: 'Verdict',
      no_data: 'No assessable subjects for this place yet.', time: 'Time', state: 'State',
      day_prefix: 'Day', guidance: 'Shows whether photography conditions meet their thresholds.',
      banner: 'Shows whether photography conditions meet their thresholds, as a reference before you shoot.',
      none: '—',
      metric_names: { cloud_cover_low: 'Low cloud', cloud_cover_mid: 'Mid cloud', cloud_cover_high: 'High cloud', cloud_cover_mid_and_high: 'Mid & high cloud', cloud_cover_total: 'Total cloud', wind_speed_10m: 'Wind', wind_speed_850hpa: 'Wind 850hPa', precipitation: 'Precipitation', aod_550nm: 'AOD 550nm', visibility: 'Visibility', relative_humidity_2m: 'Rel. humidity', relative_humidity_925hpa: 'RH 925hPa', relative_humidity_850hpa: 'RH 850hPa', lcl_height_m_agl: 'LCL height', temperature_delta_850_925_c: 'T850−T925 delta', sunrise_time_window: 'Sunrise window', sunset_window: 'Sunset window', golden_hour_window: 'Golden hour', blue_hour_window: 'Blue hour', astronomical_darkness: 'Astronomical darkness', moon_illumination_fraction: 'Moon illumination', moon_altitude: 'Moon altitude', moon_target_separation_deg: 'Moon separation', moon_illuminance_proxy: 'Moon illuminance proxy', galactic_core_altitude: 'Galactic core altitude', water_surface_state: 'Water surface state', seasonal_state: 'Seasonal state', landform_present: 'Landform presence', river_flow_state: 'River flow state' },
      genres: { mountain_view: 'Mountain view', overlook: 'Overlook', reflection: 'Water reflection', cloud_sea: 'Sea of clouds', sunrise: 'Sunrise', sunset: 'Sunset', golden_hour: 'Golden hour', blue_hour_city: 'City blue hour', overcast_soft: 'Overcast soft light', city_night: 'City night', night_sky: 'Night sky', seasonal_plant: 'Seasonal flora', geological_landform: 'Geological landform', waterfall: 'Waterfall' },
      state_labels: { GUIDANCE_SATISFIED: 'Met', UNFAVORABLE: 'Not met', NOT_EVALUABLE: 'Insufficient data' }
    },
    ja: {
      title: '撮影题材の条件評価', search: '撮影地を検索…', loading: '評価データを読み込み中…',
      load_error: '読み込みに失敗しました', updated: '評価生成時刻',
      hours: '適合時間数', next: '次の適合時間帯', now: '現在', expand: '展開',
      cond: '条件', value: '現在値', threshold: 'しきい値', verdict: '判定',
      no_data: 'この撮影地には現在評価可能な题材がありません。', time: '時刻', state: '状態',
      day_prefix: '日目', guidance: '撮影条件がしきい値を満たすかを表示します。',
      banner: '撮影条件のしきい値達成状況を撮影前の参考として表示します。',
      none: '—',
      metric_names: { cloud_cover_low: '下層雲', cloud_cover_mid: '中層雲', cloud_cover_high: '上層雲', cloud_cover_mid_and_high: '中上層雲', cloud_cover_total: '全雲量', wind_speed_10m: '風速', wind_speed_850hpa: '850hPa 風速', precipitation: '降水', aod_550nm: 'エアロゾル光学的厚さ', visibility: '視程', relative_humidity_2m: '相対湿度', relative_humidity_925hpa: '相対湿度 925hPa', relative_humidity_850hpa: '相対湿度 850hPa', lcl_height_m_agl: 'LCL 高度', temperature_delta_850_925_c: 'T850−T925 温度差', sunrise_time_window: '日の出時間帯', sunset_window: '日の入り時間帯', golden_hour_window: 'ゴールデンアワー', blue_hour_window: 'ブルーアワー', astronomical_darkness: '天文学的薄明', moon_illumination_fraction: '月照亮率', moon_altitude: '月高度', moon_target_separation_deg: '月角距離', moon_illuminance_proxy: '月光照度プロキシ', galactic_core_altitude: '銀河中心高度', water_surface_state: '水面状態', seasonal_state: '季節状態', landform_present: '地形の存在', river_flow_state: '河川流量状態' },
      genres: { mountain_view: '山の眺望', overlook: '高所展望', reflection: '水面反射', cloud_sea: '雲海', sunrise: '日の出', sunset: '夕景', golden_hour: 'ゴールデンアワー', blue_hour_city: '都市ブルーアワー', overcast_soft: '曇天ソフトライト', city_night: '都市夜景', night_sky: '星空', seasonal_plant: '季節の植物', geological_landform: '地形・地質', waterfall: '滝' },
      state_labels: { GUIDANCE_SATISFIED: '条件達成', UNFAVORABLE: '未達成', NOT_EVALUABLE: 'データ不足' }
    }
  };

  let lang = localStorage.getItem('chaselights_lang') || 'zh-TW';
  if (!I18N[lang]) lang = 'zh-TW';
  let bundle = null;
  let expandedPlaces = new Set();
  let expandedOpps = new Map();   // place_id -> Set(opportunity_id)
  let detailCache = new Map();    // place_id -> detail json
  let searchQ = '';

  const $ = (id) => document.getElementById(id);
  const t = () => I18N[lang];

  function esc(v) { return String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

  function localizedName(obj) {
    if (!obj) return '';
    return obj[lang] || obj['zh-TW'] || obj['en'] || '';
  }

  function metricName(m) { return t().metric_names[m] || m; }
  function genreName(g) { return t().genres[g] || g; }
  function stateLabel(s) { return t().state_labels[s] || s; }
  function stateBadge(s) {
    const cls = s === 'GUIDANCE_SATISFIED' ? 'b-good' : s === 'NOT_EVALUABLE' ? 'b-unk' : 'b-bad';
    return `<span class="badge ${cls}">${esc(stateLabel(s))}</span>`;
  }

  function fmtThreshold(c) {
    const th = c.threshold;
    if (th == null) return '—';
    if (c.operator === 'between' && Array.isArray(th)) return `${th[0]}–${th[1]}`;
    if (c.operator === 'lte') return `≤ ${th}`;
    if (c.operator === 'lt') return `< ${th}`;
    if (c.operator === 'gte') return `≥ ${th}`;
    if (c.operator === 'gt') return `> ${th}`;
    return String(th);
  }

  function verdictClass(v) { return v === 'PASS' ? 'v-pass' : v === 'FAIL' ? 'v-fail' : 'v-unk'; }

  function conditionsTable(conditions) {
    if (!conditions || !conditions.length) return `<p class="eval-muted">${esc(t().no_data)}</p>`;
    const rows = conditions.map((c) =>
      `<tr><td>${esc(metricName(c.metric))}</td><td>${esc(c.value ?? t().none)}</td>` +
      `<td>${esc(fmtThreshold(c))}</td><td class="${verdictClass(c.verdict)}">${c.verdict === 'PASS' ? '✓' : c.verdict === 'FAIL' ? '✗' : '?'}</td></tr>`);
    return `<table class="live-table"><thead><tr><th>${esc(t().cond)}</th><th>${esc(t().value)}</th><th>${esc(t().threshold)}</th><th>${esc(t().verdict)}</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
  }

  function liveBlock(opp) {
    const live = opp.live || {};
    const now = live.now, next = live.next_good;
    let html = '';
    if (now) {
      html += `<p class="eval-note">⏱ ${esc(t().now)}: ${esc(now.local)} — ${stateBadge(now.status)}</p>`;
      html += conditionsTable(now.conditions);
    }
    if (next) {
      html += `<p class="eval-note">🎯 ${esc(t().next)}: ${esc(next.local)} — ${stateBadge(next.status)}</p>`;
      html += conditionsTable(next.conditions);
    }
    if (!now && !next) html = `<p class="eval-muted">${esc(t().none)}</p>`;
    return html;
  }

  function hourlyTable(day) {
    const hours = day.hours || [];
    if (!hours.length) return `<p class="eval-muted">${esc(t().none)}</p>`;
    const metrics = [];
    for (const h of hours) for (const c of (h.conditions || [])) {
      if (!metrics.includes(c.metric)) metrics.push(c.metric);
    }
    const head = `<tr><th>${esc(t().time)}</th><th>${esc(t().state)}</th>` +
      metrics.map((m) => `<th>${esc(metricName(m))}</th>`).join('') + '</tr>';
    let best = null;
    for (const h of hours) if (h.status === 'GUIDANCE_SATISFIED') { best = h; break; }
    const body = hours.map((h) => {
      const byMetric = {};
      for (const c of (h.conditions || [])) byMetric[c.metric] = c;
      const isBest = best && h === best;
      const isNow = h.is_now;
      const cells = metrics.map((m) => {
        const c = byMetric[m];
        if (!c) return '<td>—</td>';
        return `<td class="${verdictClass(c.verdict)}">${esc(c.value ?? '—')} / ${esc(fmtThreshold(c))}</td>`;
      }).join('');
      return `<tr class="${isBest ? 'best-row' : ''}"><td class="${isNow ? 'now-anchor' : ''}">${esc(h.local)}${isNow ? ' ●' : ''}</td>` +
        `<td>${stateBadge(h.status)}</td>${cells}</tr>`;
    }).join('');
    return `<div class="hourly-wrap"><table class="live-table"><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
  }

  async function loadDetail(placeId) {
    if (detailCache.has(placeId)) return detailCache.get(placeId);
    const res = await fetch(`${DETAILS_BASE}${placeId}.json`, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    detailCache.set(placeId, json);
    return json;
  }

  function render() {
    if (!bundle) return;
    const wrap = $('eval-wrap');
    const q = searchQ.trim().toLowerCase();
    const region = $('region-select').value;
    const places = bundle.places
      .filter((p) => p.place_id.startsWith(region + '-'))
      .filter((p) => !q || (localizedName(p.name_i18n).toLowerCase().includes(q) || p.place_id.includes(q)));
    const html = places.map((p) => {
      const opps = p.opportunities || [];
      const open = expandedPlaces.has(p.place_id);
      const oppHtml = opps.map((o) => {
        const days = o.days || [];
        const oppOpen = (expandedOpps.get(p.place_id) || new Set()).has(o.opportunity_id);
        let body = '';
        if (oppOpen) {
          body += `<div class="eval-days">` + days.map((d, i) =>
            `<button class="eval-day-btn ${i === 0 ? 'active' : ''}" data-place="${esc(p.place_id)}" data-opp="${esc(o.opportunity_id)}" data-day="${i}">${esc(t().day_prefix)} ${i + 1} · ${esc(d.local_date)} ${stateBadge(d.state)}</button>`
          ).join('') + `</div>`;
          const det = detailCache.get(p.place_id);
          const detOpp = det ? (det.opportunities || []).find((x) => x.opportunity_id === o.opportunity_id) : null;
          const day0 = detOpp ? (detOpp.days || [])[0] : (days[0] || null);
          body += day0 ? hourlyTable(day0) : `<p class="eval-muted">${esc(t().load_error)}</p>`;
          body += liveBlock(o);
        }
        return `<div class="eval-opp" data-opp-id="${esc(o.opportunity_id)}">
          <div class="eval-opp-head" data-place="${esc(p.place_id)}" data-opp="${esc(o.opportunity_id)}">
            <span class="gname">${esc(genreName(o.genre_template))} — ${esc(localizedName(o.name_i18n))}</span>
            <span>${stateBadge(o.days?.[0]?.state || 'NOT_EVALUABLE')} <span class="eval-muted">${esc(t().hours)}: ${(o.days?.[0]?.hour_counts || {}).GUIDANCE_SATISFIED ?? 0}</span></span>
          </div>${body}</div>`;
      }).join('');
      return `<div class="eval-place ${open ? 'open' : ''}" data-place-id="${esc(p.place_id)}">
        <div class="eval-place-head" data-place="${esc(p.place_id)}">
          <h3>${esc(localizedName(p.name_i18n))}</h3>
          <span class="count">${opps.length} ${lang === 'en' ? 'subjects' : lang === 'ja' ? '题材' : '個題材'}</span>
        </div>
        <div class="eval-opps">${open ? (oppHtml || `<p class="eval-muted">${esc(t().no_data)}</p>`) : ''}</div>
      </div>`;
    }).join('');
    wrap.innerHTML = html || `<p class="eval-muted">${esc(t().no_data)}</p>`;
    $('eval-loading').style.display = 'none';
  }

  function bindEvents() {
    $('eval-wrap').addEventListener('click', async (e) => {
      const dayBtn = e.target.closest('.eval-day-btn');
      if (dayBtn) {
        const placeId = dayBtn.dataset.place, oppId = dayBtn.dataset.opp, dayIdx = +dayBtn.dataset.day;
        const det = await loadDetail(placeId).catch(() => null);
        if (!det) return;
        const detOpp = (det.opportunities || []).find((x) => x.opportunity_id === oppId);
        if (!detOpp) return;
        const table = hourlyTable((detOpp.days || [])[dayIdx] || { hours: [] });
        const oppDiv = dayBtn.closest('.eval-opp');
        const old = oppDiv.querySelector('.hourly-wrap');
        if (old) old.outerHTML = table;
        oppDiv.querySelectorAll('.eval-day-btn').forEach((b) => b.classList.toggle('active', b === dayBtn));
        return;
      }
      const oppHead = e.target.closest('.eval-opp-head');
      if (oppHead) {
        const placeId = oppHead.dataset.place, oppId = oppHead.dataset.opp;
        if (!expandedOpps.has(placeId)) expandedOpps.set(placeId, new Set());
        const set = expandedOpps.get(placeId);
        if (set.has(oppId)) { set.delete(oppId); }
        else {
          set.add(oppId);
          try { await loadDetail(placeId); } catch { /* shown as load error */ }
        }
        render();
        return;
      }
      const placeHead = e.target.closest('.eval-place-head');
      if (placeHead) {
        const placeId = placeHead.dataset.place;
        if (expandedPlaces.has(placeId)) expandedPlaces.delete(placeId);
        else {
          expandedPlaces.add(placeId);
          try { await loadDetail(placeId); } catch { /* shown as load error */ }
        }
        render();
      }
    });
    $('eval-search').addEventListener('input', (e) => { searchQ = e.target.value; render(); });
    $('region-select').addEventListener('change', () => { expandedPlaces.clear(); expandedOpps.clear(); render(); });
    $('lang-select').addEventListener('change', (e) => {
      lang = e.target.value; localStorage.setItem('chaselights_lang', lang);
      applyStaticTexts(); render();
    });
  }

  function applyStaticTexts() {
    document.documentElement.lang = lang;
    $('page-title').textContent = t().title;
    document.title = `ChaseLights — ${t().title}`;
    $('eval-search').placeholder = t().search;
    $('eval-loading').textContent = t().loading;
    $('guidance-banner').textContent = '⚠️ ' + t().banner;
    if (bundle) $('update-time').textContent = `${t().updated}: ${bundle.generated_at.replace('T', ' ').replace('Z', ' UTC')}`;
    $('lang-select').value = lang;
  }

  async function init() {
    applyStaticTexts();
    bindEvents();
    try {
      const res = await fetch(BUNDLE_URL, { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      bundle = await res.json();
    } catch (e) {
      $('eval-loading').textContent = `⚠️ ${t().load_error} (${e.message})`;
      return;
    }
    applyStaticTexts();
    render();
  }

  init();
})();
