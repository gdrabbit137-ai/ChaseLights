(function(){
  "use strict";

  const CATALOG_URL = "./runtime_catalog_v004_r4_2.json";
  const DRAFT_SCHEMA = "field-observation-draft-r4.2-1";
  const EXIF_PARSER = "exifr@7.1.3";
  const AUTO_MATCH_REVIEW_KM = 5;
  const state = { places: [], rows: [], catalogLoaded: false };

  const photoInput = document.getElementById("photo-input");
  const results = document.getElementById("results");
  const parserStatus = document.getElementById("parser-status");
  const downloadAllButton = document.getElementById("download-all");
  const consentModel = document.getElementById("consent-model");
  const consentGps = document.getElementById("consent-gps");

  function finiteNumber(value){
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function haversineKm(lat1, lon1, lat2, lon2){
    const toRad = function(deg){ return deg * Math.PI / 180; };
    const earthKm = 6371.0088;
    const p1 = toRad(lat1);
    const p2 = toRad(lat2);
    const dp = toRad(lat2 - lat1);
    const dl = toRad(lon2 - lon1);
    const a = Math.sin(dp / 2) * Math.sin(dp / 2) +
      Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) * Math.sin(dl / 2);
    return earthKm * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function buildPlaceIndex(catalog){
    const rawSpots = Array.isArray(catalog && catalog.spots)
      ? catalog.spots
      : Object.values((catalog && catalog.spots) || {});

    return rawSpots.map(function(spot){
      const seen = new Set();
      const viewpoints = [];
      (spot.opportunities || []).forEach(function(opportunity){
        (opportunity.viewpoints || []).forEach(function(viewpoint){
          const lat = finiteNumber(viewpoint.lat);
          const lon = finiteNumber(viewpoint.lon);
          if(lat === null || lon === null) return;
          const key = lat.toFixed(7) + "," + lon.toFixed(7);
          if(seen.has(key)) return;
          seen.add(key);
          viewpoints.push({
            viewpoint_id: viewpoint.viewpoint_id || null,
            name: viewpoint.name || null,
            lat: lat,
            lon: lon
          });
        });
      });
      return {
        spot_id: spot.spot_id,
        canonical_name: spot.canonical_name || spot.spot_id,
        viewpoints: viewpoints
      };
    }).filter(function(place){
      return place.spot_id && place.viewpoints.length;
    }).sort(function(a,b){
      return a.spot_id.localeCompare(b.spot_id);
    });
  }

  function nearestPlace(lat, lon, places){
    let best = null;
    (places || []).forEach(function(place){
      place.viewpoints.forEach(function(viewpoint){
        const distanceKm = haversineKm(lat, lon, viewpoint.lat, viewpoint.lon);
        if(!best || distanceKm < best.distance_km){
          best = {
            spot_id: place.spot_id,
            canonical_name: place.canonical_name,
            viewpoint_id: viewpoint.viewpoint_id,
            viewpoint_name: viewpoint.name,
            viewpoint_lat: viewpoint.lat,
            viewpoint_lon: viewpoint.lon,
            distance_km: distanceKm
          };
        }
      });
    });
    return best;
  }

  function pad2(value){
    return String(value).padStart(2, "0");
  }

  function normalizeExifDate(value){
    if(!value) return null;
    if(value instanceof Date && !Number.isNaN(value.getTime())){
      return value.getFullYear() + "-" + pad2(value.getMonth() + 1) + "-" +
        pad2(value.getDate()) + "T" + pad2(value.getHours()) + ":" +
        pad2(value.getMinutes()) + ":" + pad2(value.getSeconds());
    }
    const raw = String(value).trim();
    const match = raw.match(/^(\d{4}):(\d{2}):(\d{2})[ T](\d{2}):(\d{2}):(\d{2})/);
    if(match){
      return match[1] + "-" + match[2] + "-" + match[3] + "T" +
        match[4] + ":" + match[5] + ":" + match[6];
    }
    return raw || null;
  }

  function captureTime(meta){
    const candidates = [
      ["DateTimeOriginal", meta.DateTimeOriginal],
      ["CreateDate", meta.CreateDate],
      ["ModifyDate", meta.ModifyDate]
    ];
    let selected = null;
    for(let i=0;i<candidates.length;i+=1){
      if(candidates[i][1]){
        selected = candidates[i];
        break;
      }
    }
    const localValue = selected ? normalizeExifDate(selected[1]) : null;
    const offset = meta.OffsetTimeOriginal || meta.OffsetTimeDigitized || meta.OffsetTime || null;
    return {
      captured_at: localValue && offset ? localValue + String(offset) : null,
      local_clock: localValue,
      utc_offset: offset ? String(offset) : null,
      source_tag: selected ? selected[0] : null,
      timezone_status: offset ? "offset_from_exif" : (localValue ? "local_clock_without_offset" : "missing")
    };
  }

  function extractLocation(meta){
    const lat = finiteNumber(meta.latitude);
    const lon = finiteNumber(meta.longitude);
    if(lat === null || lon === null) return null;
    return {
      latitude: lat,
      longitude: lon,
      altitude_m: finiteNumber(meta.GPSAltitude),
      direction_deg: finiteNumber(meta.GPSImgDirection),
      direction_ref: meta.GPSImgDirectionRef || null,
      source: "embedded_exif"
    };
  }

  function cameraMetadata(meta){
    return {
      make: meta.Make || null,
      model: meta.Model || null,
      lens_model: meta.LensModel || null,
      focal_length_mm: finiteNumber(meta.FocalLength),
      f_number: finiteNumber(meta.FNumber),
      exposure_time_s: finiteNumber(meta.ExposureTime),
      iso: finiteNumber(meta.ISO || meta.ISOSpeedRatings)
    };
  }

  function humanBytes(bytes){
    if(bytes < 1024) return bytes + " B";
    if(bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function formatDistance(distance){
    if(distance === null || distance === undefined) return "—";
    if(distance < 1) return Math.round(distance * 1000) + " m";
    return distance.toFixed(distance < 10 ? 2 : 1) + " km";
  }

  function getSelectedPlace(row){
    return state.places.find(function(place){ return place.spot_id === row.selected_spot_id; }) || null;
  }

  function buildObservationDraft(row, options){
    const includeGps = Boolean(options && options.includeGps);
    const modelValidation = Boolean(options && options.modelValidation);
    const selectedPlace = getSelectedPlace(row);
    const auto = row.auto_match;
    const manualOverride = Boolean(
      selectedPlace && auto && selectedPlace.spot_id !== auto.spot_id
    );
    let location = {
      available_in_source: Boolean(row.location),
      source: row.location ? "embedded_exif" : null,
      retention: row.location
        ? (includeGps ? "included_by_explicit_user_choice" : "withheld_from_export")
        : "not_available"
    };
    if(row.location && includeGps){
      location.latitude = row.location.latitude;
      location.longitude = row.location.longitude;
      location.altitude_m = row.location.altitude_m;
      location.direction_deg = row.location.direction_deg;
      location.direction_ref = row.location.direction_ref;
    }

    return {
      schema_version: DRAFT_SCHEMA,
      status: "unreviewed",
      created_at: new Date().toISOString(),
      source: {
        type: "user_field_observation",
        medium: "photograph",
        image_bytes_uploaded: false,
        publication: "metadata_only_image_not_uploaded",
        parser: EXIF_PARSER,
        processing: "browser_local"
      },
      file: {
        name: row.file.name,
        type: row.file.type || null,
        size_bytes: row.file.size,
        last_modified_ms: row.file.lastModified
      },
      capture: {
        time: row.capture_time,
        camera: row.camera
      },
      location: location,
      place_match: selectedPlace ? {
        spot_id: selectedPlace.spot_id,
        canonical_name: selectedPlace.canonical_name,
        method: manualOverride ? "user_override" : (auto ? "nearest_catalog_viewpoint" : "manual_selection"),
        auto_match_distance_km: auto ? Number(auto.distance_km.toFixed(4)) : null,
        auto_match_viewpoint_id: auto ? auto.viewpoint_id : null,
        review_required: manualOverride || !auto || (auto.distance_km > AUTO_MATCH_REVIEW_KM)
      } : {
        spot_id: null,
        canonical_name: null,
        method: "unmatched",
        auto_match_distance_km: auto ? Number(auto.distance_km.toFixed(4)) : null,
        auto_match_viewpoint_id: auto ? auto.viewpoint_id : null,
        review_required: true
      },
      consent: {
        model_validation: modelValidation,
        precise_location_storage: includeGps,
        public_photo: false
      },
      ground_truth_boundary: "This is an unreviewed observation draft. It is not an admitted FV field-validation case and must not change scoring thresholds without review."
    };
  }

  function downloadJson(filename, payload){
    const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"], {type:"application/json"});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
  }

  function addMetaItem(grid, label, value){
    const item = document.createElement("div");
    item.className = "meta-item";
    const labelNode = document.createElement("span");
    labelNode.className = "meta-label";
    labelNode.textContent = label;
    const valueNode = document.createElement("span");
    valueNode.className = "meta-value";
    valueNode.textContent = value || "—";
    item.appendChild(labelNode);
    item.appendChild(valueNode);
    grid.appendChild(item);
  }

  function placeOptions(select, selectedId){
    const empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "請選擇景點";
    select.appendChild(empty);
    state.places.forEach(function(place){
      const option = document.createElement("option");
      option.value = place.spot_id;
      option.textContent = place.spot_id + " · " + place.canonical_name;
      option.selected = place.spot_id === selectedId;
      select.appendChild(option);
    });
  }

  function renderRows(){
    results.innerHTML = "";
    if(!state.rows.length){
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "尚未選擇照片。";
      results.appendChild(empty);
      downloadAllButton.disabled = true;
      return;
    }
    downloadAllButton.disabled = false;

    state.rows.forEach(function(row){
      const card = document.createElement("article");
      card.className = "observation-card";

      const head = document.createElement("div");
      head.className = "observation-head";
      const fileWrap = document.createElement("div");
      const name = document.createElement("div");
      name.className = "file-name";
      name.textContent = row.file.name;
      const size = document.createElement("div");
      size.className = "small";
      size.textContent = humanBytes(row.file.size) + (row.file.type ? " · " + row.file.type : "");
      fileWrap.appendChild(name);
      fileWrap.appendChild(size);
      head.appendChild(fileWrap);

      const download = document.createElement("button");
      download.className = "download-btn";
      download.type = "button";
      download.textContent = "下載 JSON";
      download.addEventListener("click", function(){
        const draft = buildObservationDraft(row, {
          includeGps: consentGps.checked,
          modelValidation: consentModel.checked
        });
        downloadJson("observation-" + row.id + ".json", draft);
      });
      head.appendChild(download);
      card.appendChild(head);

      const grid = document.createElement("div");
      grid.className = "meta-grid";
      const captureDisplay = row.capture_time.captured_at ||
        (row.capture_time.local_clock
          ? row.capture_time.local_clock + "（EXIF 無時區）"
          : "未找到");
      const gpsDisplay = row.location
        ? row.location.latitude.toFixed(6) + ", " + row.location.longitude.toFixed(6)
        : "未找到";
      const cameraDisplay = [row.camera.make, row.camera.model].filter(Boolean).join(" ") || "未找到";
      const lensDisplay = row.camera.lens_model ||
        (row.camera.focal_length_mm ? row.camera.focal_length_mm + " mm" : "未找到");

      addMetaItem(grid, "拍攝時間", captureDisplay);
      addMetaItem(grid, "GPS（只在本機顯示）", gpsDisplay);
      addMetaItem(grid, "相機", cameraDisplay);
      addMetaItem(grid, "鏡頭 / 焦距", lensDisplay);
      card.appendChild(grid);

      const placeRow = document.createElement("div");
      placeRow.className = "place-row";
      const label = document.createElement("label");
      label.textContent = "配對景點";
      const select = document.createElement("select");
      select.className = "place-select";
      placeOptions(select, row.selected_spot_id);
      select.addEventListener("change", function(){
        row.selected_spot_id = select.value || null;
        renderRows();
      });
      label.appendChild(select);
      placeRow.appendChild(label);
      card.appendChild(placeRow);

      const note = document.createElement("div");
      note.className = "match-note";
      if(row.auto_match){
        const tooFar = row.auto_match.distance_km > AUTO_MATCH_REVIEW_KM;
        note.classList.toggle("warn", tooFar);
        note.textContent = "GPS 最近景點：" + row.auto_match.canonical_name +
          "（" + formatDistance(row.auto_match.distance_km) + "）" +
          (tooFar ? "；距離較遠，請手動確認。" : "。");
      }else if(row.location){
        note.classList.add("warn");
        note.textContent = "有 GPS，但目前 catalog 找不到可比對的 viewpoint；請手動選景點。";
      }else{
        note.classList.add("warn");
        note.textContent = "照片沒有可讀 GPS；請手動選擇景點。";
      }
      card.appendChild(note);
      results.appendChild(card);
    });
  }

  async function parsePhoto(file, index){
    const id = Date.now().toString(36) + "-" + index.toString(36);
    let meta = {};
    let error = null;
    if(!window.exifr || typeof window.exifr.parse !== "function"){
      error = "EXIF parser unavailable";
    }else{
      try{
        meta = await window.exifr.parse(file, true) || {};
      }catch(err){
        error = String(err && err.message ? err.message : err);
      }
    }
    const location = extractLocation(meta);
    const autoMatch = location
      ? nearestPlace(location.latitude, location.longitude, state.places)
      : null;

    return {
      id: id,
      file: {
        name: file.name,
        type: file.type || "",
        size: file.size,
        lastModified: file.lastModified
      },
      capture_time: captureTime(meta),
      camera: cameraMetadata(meta),
      location: location,
      auto_match: autoMatch,
      selected_spot_id: (autoMatch && autoMatch.distance_km <= AUTO_MATCH_REVIEW_KM) ? autoMatch.spot_id : null,
      parse_error: error
    };
  }

  async function handleFiles(files){
    const list = Array.from(files || []);
    if(!list.length) return;
    parserStatus.className = "status";
    parserStatus.textContent = "正在本機解析 " + list.length + " 張照片…";
    const rows = [];
    for(let i=0;i<list.length;i+=1){
      rows.push(await parsePhoto(list[i], i));
    }
    state.rows = rows;
    const failures = rows.filter(function(row){ return row.parse_error; }).length;
    parserStatus.className = failures ? "status warn" : "status ready";
    parserStatus.textContent = failures
      ? "完成，但有 " + failures + " 張照片無法讀取 EXIF。照片仍未上傳。"
      : "完成。本機 EXIF 已解析；照片仍未上傳。";
    renderRows();
  }

  async function loadCatalog(){
    try{
      const response = await fetch(CATALOG_URL, {cache:"no-cache"});
      if(!response.ok) throw new Error("HTTP " + response.status);
      const catalog = await response.json();
      state.places = buildPlaceIndex(catalog);
      state.catalogLoaded = true;
      if(!window.exifr){
        parserStatus.className = "status warn";
        parserStatus.textContent = "景點資料已載入，但 EXIF 解析器無法載入；不會改用任何上傳式解析。";
      }else{
        parserStatus.className = "status ready";
        parserStatus.textContent = "已就緒：" + state.places.length + " 個景點可供 GPS 配對。照片只在本機解析。";
      }
    }catch(err){
      parserStatus.className = "status warn";
      parserStatus.textContent = "景點資料載入失敗：" + String(err && err.message ? err.message : err);
    }
  }

  photoInput.addEventListener("change", function(){
    handleFiles(photoInput.files);
  });

  downloadAllButton.addEventListener("click", function(){
    const options = {
      includeGps: consentGps.checked,
      modelValidation: consentModel.checked
    };
    const payload = {
      schema_version: DRAFT_SCHEMA,
      exported_at: new Date().toISOString(),
      observations: state.rows.map(function(row){ return buildObservationDraft(row, options); })
    };
    downloadJson("chaselights-observations.json", payload);
  });

  window.ChaseLightsFieldIntake = {
    haversineKm: haversineKm,
    buildPlaceIndex: buildPlaceIndex,
    nearestPlace: nearestPlace,
    buildObservationDraft: buildObservationDraft
  };

  loadCatalog();
})();
