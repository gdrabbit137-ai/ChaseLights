    async function loadDetails(region,spotId){
      const key=`${region}:${spotId}`,versionMatches=x=>!currentData?.updated_at||x?.updated_at===currentData.updated_at;
      if(memoryDetails.has(key)){const m=memoryDetails.get(key);if(versionMatches(m))return m;memoryDetails.delete(key);}
      const url=`./weather_details/${region}/${encodeURIComponent(spotId)}.json`;
      const cached=await cacheMatch(url);
      if(cached&&versionMatches(cached)){memoryDetails.set(key,cached);fetchAndCache(url,null).then(x=>{if(versionMatches(x))memoryDetails.set(key,x);}).catch(()=>{});return cached;}
      const fresh=await fetchAndCache(url,null);if(!versionMatches(fresh))throw new Error('Weather detail version mismatch');memoryDetails.set(key,fresh);return fresh;
    }
    async function openWeatherModal(spot,summaryMetric){
      document.getElementById('modal-overlay').style.display='flex';syncModalScrollLock();const showLocal=!(currentRegion==='tw'&&currentLang==='zh-TW');document.getElementById('modal-spot-name').innerText=`🌦️ ${spotName(spot)} — ${d().weather_link.replace(/^🌦️\s*/, '')}`;document.getElementById('modal-summary').innerText=d().detail_loading;document.getElementById('timeline-head').innerHTML='';document.getElementById('timeline-body').innerHTML='';document.getElementById('timeline-mobile').innerHTML='';
      try{const payload=await loadDetails(currentRegion,spot.spot_id);const detail=payload?.spot;if(!detail||detail.spot_id!==spot.spot_id)throw new Error('missing spot');renderWeatherModal(detail,summaryMetric);}catch(e){document.getElementById('modal-summary').innerText=`⚠️ ${e.message||e}`;}
    }
    function scrollWeatherModalToCurrent(){
      const modalBody=document.querySelector('#modal-overlay .modal-body');if(!modalBody)return;
      const mobileView=window.matchMedia('(max-width:640px)').matches;
      const target=(mobileView?document.getElementById('timeline-mobile'):document.getElementById('timeline-body'))?.querySelector('[data-now-anchor="true"]');
      if(!target){modalBody.scrollTop=0;return;}
      requestAnimationFrame(()=>{
        const bodyTop=modalBody.getBoundingClientRect().top;
        const targetTop=target.getBoundingClientRect().top;
        const stickyOffset=mobileView?8:((document.getElementById('timeline-head')?.getBoundingClientRect().height||0)+8);
        modalBody.scrollTop=Math.max(0,modalBody.scrollTop+(targetTop-bodyTop)-stickyOffset);
      });
    }
    function renderWeatherModal(spot,summaryMetric){
      activeModalSpot=spot;activeModalSummary=summaryMetric;
      const day=currentDayForSpot(spot);const activeTheme=summaryMetric?.theme||'mountain_view';const activeOpportunityId=summaryMetric?.opportunity_id||null;const activeOpportunityName=summaryMetric?.opportunity_name||themeLabel(activeTheme);const selectedDate=selectedDateForSpot(currentSpots.find(x=>x.spot_id===spot.spot_id)||spot);
      const darkSky=darkSkyText(spot,activeTheme);document.getElementById('modal-summary').innerHTML=`<div class="modal-summary-main">${d().best_theme}${esc(activeOpportunityName)}</div><div class="modal-summary-window">${d().best_window}${fmtWindow(summaryMetric)}</div>${darkSky?`<div class="modal-summary-extra">${darkSky}</div>`:''}`;
      const isAurora=activeTheme==='aurora',thead=document.getElementById('timeline-head'),tbody=document.getElementById('timeline-body'),mobile=document.getElementById('timeline-mobile');thead.innerHTML=`<tr><th>${d().th_time}</th><th>${d().th_theme}</th><th>${d().th_score}</th><th>${d().th_status}</th>${isAurora?`<th>${d().th_kp}</th>`:''}<th class="key-metric">${d().th_cloud_base}</th><th>${d().th_temp} (${tempUnitLabel()})</th><th>${d().th_rh}</th><th class="key-metric">${d().th_clow}</th><th>${d().th_cmid}</th><th>${d().th_chigh}</th><th>${d().th_wind}</th><th class="key-metric">${d().th_vis}</th><th>${d().th_astro}</th></tr>`;tbody.innerHTML='';mobile.innerHTML='';
      let nowAnchorAssigned=false;
      (spot.hourly_forecast||[]).forEach(item=>{const metrics=(activeOpportunityId&&item.opportunity_scores?.[activeOpportunityId])||item.theme_scores?.[activeTheme]||item.tag_scores?.[activeTheme];if(!metrics)return;const isNowAnchor=!nowAnchorAssigned&&!item.is_past;if(isNowAnchor)nowAnchorAssigned=true;const isBest=!!(selectedDate&&item.local_date===selectedDate&&summaryMetric?.window_start&&item.time>=summaryMetric.window_start&&item.time<summaryMetric.window_end);const rowClass=isBest?'best-row':(item.is_past?'past-row':'');const tr=document.createElement('tr');tr.className=rowClass;if(isNowAnchor)tr.dataset.nowAnchor='true';const astro=astroText(item,activeTheme);tr.innerHTML=`<td>${item.time}${item.is_past?' <span class="tag-past">HIST</span>':''}${isBest?` <span class="tag-best">${esc(d().tag_best)}</span>`:''}</td><td>${esc(activeOpportunityName)}</td><td><span class="timeline-score-badge ${opportunityScoreClass(Number(metrics.score))}">${metrics.score}</span></td><td>${trMessage(metrics.status_key)}</td>${isAurora?`<td>${item.kp??'—'}</td>`:''}<td class="key-metric">${item.cloud_base_agl??'—'}m</td><td>${formatTemp(item.temp)}</td><td>${item.rh??'—'}%</td><td class="key-metric">${item.c_low??'—'}%</td><td>${item.c_mid??'—'}%</td><td>${item.c_high??'—'}%</td><td>${item.wind??'—'}m/s</td><td class="key-metric">${item.visibility??'—'}km</td><td>${astro||'—'}</td>`;tbody.appendChild(tr);
        const card=document.createElement('div');card.className=`timeline-mobile-card ${rowClass}`;if(isNowAnchor)card.dataset.nowAnchor='true';card.innerHTML=`<div class="timeline-mobile-head"><div><div class="timeline-mobile-time">${esc(item.time)}${item.is_past?' <span class="tag-past">HIST</span>':''}${isBest?` <span class="tag-best">${esc(d().tag_best)}</span>`:''}</div><div class="timeline-mobile-status">${esc(trMessage(metrics.status_key))}</div></div><div class="timeline-mobile-score"><span class="timeline-score-badge ${opportunityScoreClass(Number(metrics.score))}">${metrics.score}</span></div></div><div class="timeline-mobile-metrics"><div class="timeline-mobile-metric"><b>${d().th_temp}</b> ${formatTemp(item.temp)}</div><div class="timeline-mobile-metric primary"><b>${d().th_vis}</b> ${item.visibility??'—'} km</div><div class="timeline-mobile-metric primary"><b>${d().th_clow}</b> ${item.c_low??'—'}%</div><div class="timeline-mobile-metric"><b>${d().th_cmid}</b> ${item.c_mid??'—'}%</div><div class="timeline-mobile-metric"><b>${d().th_chigh}</b> ${item.c_high??'—'}%</div><div class="timeline-mobile-metric"><b>${d().th_wind}</b> ${item.wind??'—'} m/s</div><div class="timeline-mobile-metric primary"><b>${d().th_cloud_base}</b> ${item.cloud_base_agl??'—'} m</div><div class="timeline-mobile-metric"><b>${d().th_rh}</b> ${item.rh??'—'}%</div>${isAurora?`<div class="timeline-mobile-metric"><b>${d().th_kp}</b> ${item.kp??'—'}</div>`:''}</div>${astro?`<div class="timeline-mobile-astro">${esc(astro)}</div>`:''}`;mobile.appendChild(card);
      });
      scrollWeatherModalToCurrent();
    }
    function closeModal(){document.getElementById('modal-overlay').style.display='none';activeModalSpot=null;activeModalSummary=null;syncModalScrollLock();}
    document.addEventListener('keydown',e=>{
      if(e.key!=='Escape')return;
      if(document.getElementById('modal-overlay').style.display==='flex')closeModal();
      else if(document.getElementById('place-modal-overlay').style.display==='flex')closePlaceModal();
    });
