    function opportunityScoreClass(score){return score>=80?'high':score>=65?'mid':'low';}
    function openPlaceModal(spot,summaryMetric){
      const overlay=document.getElementById('place-modal-overlay');
      const body=document.getElementById('place-modal-body');
      const showLocal=!(currentRegion==='tw'&&currentLang==='zh-TW');
      document.getElementById('place-modal-spot-name').textContent=`📍 ${spotName(spot)}${showLocal&&spot.name_local&&spot.name_local!==spotName(spot)?` (${spot.name_local})`:''}`;
      const opportunities=spot.opportunities||[];
      const day=currentDayForSpot(spot);
      const dayScores=day?.opportunities||{};
      if(!opportunities.length){
        body.innerHTML=`<div class="unresearched-note">${esc(d().guide_unresearched)}</div>`;
        overlay.style.display='flex';syncModalScrollLock();return;
      }
      const rankedOpportunities=opportunities.map((op,index)=>{const raw=dayScores[op.opportunity_id]?.score;const score=raw===null||raw===undefined?null:Number(raw);return {op,index,score:Number.isFinite(score)?score:null};}).sort((a,b)=>{if(a.score===null&&b.score===null)return a.index-b.index;if(a.score===null)return 1;if(b.score===null)return -1;return (b.score-a.score)||(a.index-b.index);}).map(x=>x.op);
      const cards=rankedOpportunities.map(op=>{
        const m=dayScores[op.opportunity_id]||null;
        const score=m?.score;
        const viewpoints=(op.viewpoints||[]).map(v=>v.name).filter(Boolean);
        const variants=(op.condition_variants||[]).map(v=>{
          const rows=[];
          if(v.required_conditions)rows.push(`<div><span class="research-label">${esc(d().guide_required)}：</span>${esc(v.required_conditions)}</div>`);
          if(v.boosters)rows.push(`<div><span class="research-label">${esc(d().guide_boosters)}：</span>${esc(v.boosters)}</div>`);
          if(v.penalties)rows.push(`<div><span class="research-label">${esc(d().guide_penalties)}：</span>${esc(v.penalties)}</div>`);
          return `<div class="variant-name">${esc(v.variant_name||'')}</div>${rows.join('')}`;
        }).join('');
        const scoreHtml=score===undefined||score===null?'':`<div class="opportunity-score ${opportunityScoreClass(score)}">${score}</div>`;
        const current=m?`<div class="opportunity-current"><span class="research-label">${esc(d().guide_current)}：</span>${score} · ${esc(trMessage(m.status_key))}</div>`:'';
        const scoreFactors=(m?.factors||[]).map(f=>`<span class="factor-pill ${f.type==='minus'?'factor-minus':'factor-plus'}">${f.type==='minus'?'−':'＋'} ${trFactor(f)}</span>`).join('');
        const scoreStatus=m?trMessage(m.status_key):'';
        const scoreIndicator=m?trMessage(m.indicator_key):'';
        const scoreExplain=m?`<details class="score-explain"><summary>${esc(d().guide_score_why)}</summary><div class="score-explain-body"><div class="score-explain-status"><span class="research-label">${esc(d().guide_score_status)}：</span>${esc(scoreStatus)}${scoreIndicator&&scoreIndicator!==scoreStatus?`<br>${esc(scoreIndicator)}`:''}</div>${scoreFactors?`<div class="factor-row">${scoreFactors}</div>`:''}</div></details>`:'';
        const metaRows=[];
        if(op.best_time)metaRows.push(`<div><span class="research-label">${esc(d().guide_time)}：</span>${esc(op.best_time)}</div>`);
        if(op.best_season)metaRows.push(`<div><span class="research-label">${esc(d().guide_season)}：</span>${esc(op.best_season)}</div>`);
        if(viewpoints.length)metaRows.push(`<div><span class="research-label">${esc(d().guide_viewpoint)}：</span>${esc(viewpoints.join('／'))}</div>`);
        return `<div class="opportunity-card">
          <div class="opportunity-head"><div class="opportunity-title">${esc(op.name_zh||themeLabel(op.legacy_theme))}</div>${scoreHtml}</div>
          ${current}
          ${metaRows.length?`<div class="opportunity-meta">${metaRows.join('')}</div>`:''}
          ${scoreExplain}
          ${variants?`<details class="research-details"><summary>${esc(d().guide_details)}</summary><div class="research-block">${variants}</div></details>`:''}
        </div>`;
      }).join('');
      body.innerHTML=`<div class="place-guide-intro"><b>${esc(d().place_suitable)}</b><br>${esc(d().researched_only)}<br>🕒 ${esc(d().place_time_note)}</div><div class="opportunity-list">${cards}</div>`;
      overlay.style.display='flex';
      syncModalScrollLock();
    }
    function syncModalScrollLock(){
      const open=[document.getElementById('place-modal-overlay'),document.getElementById('modal-overlay')].some(el=>el?.style.display==='flex');
      document.body.style.overflow=open?'hidden':'';
    }
    function closePlaceModal(){document.getElementById('place-modal-overlay').style.display='none';syncModalScrollLock();}
