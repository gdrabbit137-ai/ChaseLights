import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridUiPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "weather-map.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_controls_cannot_overflow_map_panel(self):
        self.assertIn("grid-template-columns:repeat(3,minmax(0,1fr))", self.css)
        self.assertIn(".control-bar>*{min-width:0}", self.css)
        self.assertIn("#spot-select,#opportunity-select", self.css)

    def test_time_ui_is_one_navigator_instead_of_two_competing_controls(self):
        self.assertIn('class="time-navigator"', self.html)
        self.assertIn('id="time-prev"', self.html)
        self.assertIn('id="time-slider"', self.html)
        self.assertIn('id="time-next"', self.html)
        self.assertIn('id="time-play"', self.html)
        self.assertIn("function updateTimeline()", self.js)
        self.assertNotIn('class="time-control"', self.html)

    def test_wind_direction_is_encoded_by_vectors_in_combined_layer(self):
        self.assertIn("wind_speed_10m_m_s:{label:'10 m 風場'", self.js)
        self.assertIn("key=>key!=='wind_direction_10m_deg'", self.js)
        self.assertIn("const toward=((direction+180)%360)", self.js)
        self.assertIn("if(!state.windVectors && !isWindLayer()) return", self.js)

    def test_direction_source_field_remains_available_for_vector_rendering(self):
        self.assertIn("wind_direction_10m_deg", self.js)
        self.assertIn("decodedArray('wind_direction_10m_deg')", self.js)
        self.assertIn("function windUv(speed,directionDeg)", self.js)

    def test_direction_palette_is_explicitly_cyclic(self):
        self.assertIn("if(cfg.palette==='direction')", self.js)
        self.assertIn("北 0°", self.js)
        self.assertIn("北 360°", self.js)

    def test_rain_rate_uses_non_linear_threshold_scale(self):
        self.assertIn("scale:'precip_rate'", self.js)
        self.assertIn("ticks:[0,.1,.5,1,2,5,10,20]", self.js)
        self.assertIn("function normalizedPiecewise(value,breaks)", self.js)

    def test_spots_cluster_at_low_zoom_and_keep_selected_spot_distinct(self):
        self.assertIn("function spotClusterRadius()", self.js)
        self.assertIn("function buildSpotHitTargets()", self.js)
        self.assertIn("function zoomToSpotCluster(spots)", self.js)
        self.assertIn("spots.length>1", self.js)

    def test_inspector_prioritizes_layer_identity_over_raw_min_max(self):
        self.assertIn('id="layer-range"', self.html)
        self.assertIn("$('layer-summary').textContent=cfg.label", self.js)
        self.assertIn("畫面資料範圍", self.js)

    def test_qc_flags_are_explained_in_user_language(self):
        self.assertIn("function qcMessage(flag)", self.js)
        self.assertIn("能見度大量達模型上限", self.js)
        self.assertIn("內部 QC 代碼", self.js)

    def test_cycle_and_valid_time_are_user_facing(self):
        self.assertIn("模型起報", self.js)
        self.assertIn("TST", self.js)
        self.assertIn("預報時間", self.js)
        self.assertIn("自動模式：依圖層選優先模型", self.js)

    def test_model_boundary_is_drawn(self):
        self.assertIn("function drawProviderBoundary(data)", self.js)
        self.assertIn("虛線＝目前資料來源範圍", self.js)

    def test_mobile_layout_respects_safe_area_and_keeps_two_column_controls(self):
        self.assertIn("viewport-fit=cover", self.html)
        self.assertIn("env(safe-area-inset-top)", self.css)
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", self.css)
        self.assertNotIn("@media(max-width:460px){\n  .control-bar{grid-template-columns:1fr}", self.css)

    def test_mobile_hides_disabled_topic_control_and_expands_place_control(self):
        self.assertIn('id="opportunity-control" class="opportunity-control"', self.html)
        self.assertIn("mobile-inactive", self.js)
        self.assertIn("mobile-full", self.js)
        self.assertIn(".opportunity-control.mobile-inactive{display:none}", self.css)
        self.assertIn(".spot-control.mobile-full{grid-column:1/-1}", self.css)

    def test_reset_view_is_map_overlay_instead_of_full_width_control_row(self):
        control_start = self.html.index('class="control-bar"')
        map_start = self.html.index('class="map-wrap"')
        reset_start = self.html.index('id="reset-view"')
        self.assertGreater(reset_start, map_start)
        self.assertNotIn('id="reset-view"', self.html[control_start:map_start])
        self.assertIn(".map-reset-button{position:absolute", self.css)

    def test_mobile_time_controls_stay_on_one_compact_row(self):
        self.assertIn("grid-template-columns:38px minmax(0,1fr) 38px 38px", self.css)
        self.assertIn("#time-play{grid-column:auto;font-size:0}", self.css)
        self.assertIn(".timeline span:nth-child(2),.timeline span:nth-child(4){display:none}", self.css)

    def test_mobile_map_gets_more_vertical_space_and_compact_legend(self):
        self.assertIn(".map-wrap{aspect-ratio:1.12/1", self.css)
        self.assertIn("min-width:132px;max-width:44%", self.css)
        self.assertIn(".coverage-outline-key{display:none}", self.css)

    def test_cloud_percent_palette_has_explicit_50_percent_hinge(self):
        self.assertIn("CLOUD_PERCENT_BREAKS=[0,20,40,50,70,85,100]", self.js)
        self.assertIn("scale:'cloud_percent'", self.js)
        self.assertIn("function cloudColorFor(value)", self.js)
        self.assertIn("50% 雲量分界", self.js)
        self.assertIn("cloud-midline", self.css)

    def test_cloud_overlay_never_fully_hides_basemap(self):
        self.assertIn("CLOUD_MAX_OVERLAY_ALPHA=.78", self.js)
        self.assertIn("function layerOpacityCap(cfg)", self.js)
        self.assertIn("state.weatherOpacity*layerOpacityCap(cfg)*cellOpacityFor", self.js)
        self.assertIn('id="opacity-title"', self.html)
        self.assertIn("雲層顯示強度", self.js)

    def test_forecast_cloud_map_draws_50_percent_contour_and_selected_value(self):
        self.assertIn("function drawCloudThresholdContour(", self.js)
        self.assertIn("drawCloudThresholdContour(data,vals,50,visibleView)", self.js)
        self.assertIn("!isObservationMode() && cfg.palette==='cloud'", self.js)
        self.assertIn("selectedLabel=", self.js)
        self.assertIn("formatValue(value,state.layer)", self.js)

    def test_cloud_legend_exposes_all_breakpoints(self):
        self.assertIn("function cloudLegendLabels()", self.js)
        self.assertIn("cloud-legend-labels", self.css)

    def test_mobile_map_clusters_spots_more_aggressively(self):
        self.assertIn("const compactMap=canvas.clientWidth<=600", self.js)
        self.assertIn("if(zoom<6.2) return 44", self.js)
        self.assertIn("if(zoom<7.5) return 32", self.js)
        self.assertIn("if(zoom<8.4) return 20", self.js)

    def test_mobile_cluster_and_selected_labels_are_compact(self):
        self.assertIn("700 9px -apple-system, sans-serif", self.js)
        self.assertIn("bold 16px -apple-system, sans-serif", self.js)
        self.assertIn("ctx.measureText(selectedLabel)", self.js)
        self.assertIn("canvas.clientWidth-8", self.js)

    def test_mobile_maplibre_controls_are_compact(self):
        self.assertIn(".maplibregl-ctrl-group button{width:34px;height:34px}", self.css)
        self.assertIn("max-width:112px", self.css)

    def test_b166_cams_aod_source_and_layer_are_exposed(self):
        self.assertIn('<option value="cams">CAMS Global · 霧霾</option>', self.html)
        self.assertIn("LIVE_CAMS_DATA", self.js)
        self.assertIn("aerosol_optical_depth_550nm", self.js)
        self.assertIn("palette:'haze'", self.js)
        self.assertIn("if(mode==='cams') return 'CAMS Global · 霧霾'", self.js)
        self.assertIn("CAMS 預報時間", self.js)
        self.assertIn("資料更新 ", self.js)
        self.assertIn("? `更新 ", self.js)

    def test_b166_cams_provenance_is_visible_in_ui(self):
        self.assertIn("CAMS Global 原生約", self.js)
        self.assertIn("Copernicus CAMS Global", self.js)
        self.assertIn("Open-Meteo", self.js)
        self.assertIn("AOD 是整層大氣的氣膠光學厚度", self.html)

    def test_b167_cams_pm25_layer_is_exposed_with_distinct_semantics(self):
        self.assertIn("pm2_5_ug_m3", self.js)
        self.assertIn("label:'PM2.5'", self.js)
        self.assertIn("unit:'µg/m³'", self.js)
        self.assertIn("palette:'pm25'", self.js)
        self.assertIn("CAMS Global · PM2.5", self.js)
        self.assertIn("PM2.5 是近地面細懸浮微粒質量濃度", self.html)

    def test_b168r_environment_diagnostic_is_visible_but_non_scoring(self):
        self.assertIn('id="spot-environment"', self.html)
        self.assertIn("function classifyFogHazeEnvironment(point)", self.js)
        self.assertIn("mixed_fog_haze", self.js)
        self.assertIn("low_visibility_unresolved", self.js)
        self.assertIn("GFS 能見度／低雲 + CWA RH + CAMS AOD／PM2.5", self.js)
        self.assertIn("目前不影響攝影評分", self.js)
        self.assertIn(".environment-diagnostic", self.css)

    def test_b169f_viirs_is_fail_closed_until_real_qc_artifact_exists(self):
        self.assertIn("LIVE_VIIRS_DATA", self.js)
        self.assertIn("LIVE_VIIRS_QC", self.js)
        self.assertIn("qcFlags.length===0", self.js)
        self.assertIn("viirsData?.source==='nasa_black_marble_vnp46a4'", self.js)
        self.assertIn("if(state.viirsData && !viirsOption)", self.js)
        self.assertIn("else if(!state.viirsData && viirsOption)", self.js)
        self.assertNotIn('<option value="viirs">', self.html)

    def test_b169f_viirs_keeps_static_environment_semantics(self):
        self.assertIn("nighttime_lights_radiance_nw_cm2_sr", self.js)
        self.assertIn("label:'夜間燈光'", self.js)
        self.assertIn("palette:'nightlights'", self.js)
        self.assertIn("function isStaticEnvironmentMode()", self.js)
        self.assertIn("靜態年度背景，不隨氣象預報時間軸變化", self.js)
        self.assertIn("不等同 Bortle 或天空亮度", self.js)

    def test_b169h_renderer_culls_to_visible_grid_slice(self):
        self.assertIn("function visibleAxisRange(values,minValue,maxValue,pad=1)", self.js)
        self.assertIn("function visibleGridRange(data,visibleView,pad=1)", self.js)
        self.assertIn("for(let r=row0;r<=row1;r++)", self.js)
        self.assertIn("for(let c=col0;c<=col1;c++)", self.js)
        self.assertIn("const maxRow=Math.min(rows-2,row1)", self.js)
        self.assertIn("const maxCol=Math.min(cols-2,col1)", self.js)

    def test_b169i_viirs_inspector_exposes_quality_semantics(self):
        self.assertIn("nighttime_lights_quality_flag", self.js)
        self.assertIn("VNP46A4 QA：", self.js)
        self.assertIn("good（原始年度合成）", self.js)
        self.assertIn("poor（品質較低）", self.js)
        self.assertIn("gap-filled（缺口填補）", self.js)
        self.assertIn("品質旗標以最近原始顯示格判讀", self.js)

    def test_b169i_nightlights_legend_uses_piecewise_radiance_ticks(self):
        self.assertIn("else if(cfg.scale==='nightlights')", self.js)
        self.assertIn("labels=['0','1','5','10','50+']", self.js)

    def test_assets_use_cache_busting_after_mobile_ui_updates(self):
        self.assertIn('weather-map.css?v=b172g', self.html)
        self.assertIn('weather-map.js?v=b172g', self.html)

    def test_mobile_opacity_control_is_single_row(self):
        self.assertIn('class="opacity-caption"', self.html)
        self.assertIn("grid-template-columns:max-content minmax(0,1fr)", self.css)
        self.assertIn("display:grid!important", self.css)
        self.assertIn("const compactUi=window.matchMedia('(max-width:720px)').matches", self.js)
        self.assertIn("? (cfg.palette==='cloud'?'雲層透明度':'圖層透明度')", self.js)

    def test_map_attribution_is_compact_on_mobile(self):
        self.assertIn("attributionControl:false", self.js)
        self.assertIn("new maplibregl.AttributionControl({compact:true})", self.js)
        self.assertIn(".maplibregl-ctrl-attrib.maplibregl-compact", self.css)

    def test_mobile_header_uses_one_line_source_summary(self):
        self.assertIn('id="source-mobile-summary"', self.html)
        self.assertIn("grid-template-columns:auto minmax(0,1fr) auto", self.css)
        self.assertIn(".source-detail,.source-attribution{display:none}", self.css)
        self.assertIn("compactSummary.textContent=", self.js)
        self.assertIn("起報 ", self.js)
        self.assertIn("觀測 ", self.js)

    def test_mobile_header_keeps_data_info_accessible(self):
        self.assertIn('class="info-label-long"', self.html)
        self.assertIn('class="info-label-short"', self.html)
        self.assertIn(".info-label-long{display:none}", self.css)
        self.assertIn(".info-label-short{display:inline}", self.css)
        self.assertIn('id="data-info-open"', self.html)

    def test_mobile_title_line_is_compact_but_desktop_structure_survives(self):
        self.assertIn('class="header-title-line"', self.html)
        self.assertIn(".header-title-line{display:flex;flex-direction:column", self.css)
        self.assertIn(".header-title-line{\n    flex-direction:row", self.css)

    def test_mobile_layer_inspector_defaults_to_summary(self):
        self.assertIn('id="layer-details-toggle"', self.html)
        self.assertIn('aria-expanded="false"', self.html)
        self.assertIn('id="qc-summary" class="qc-summary pending"', self.html)
        self.assertIn('class="layer-details mobile-collapsed"', self.html)
        self.assertIn(".layer-details.mobile-collapsed{display:none}", self.css)

    def test_mobile_layer_details_can_expand_without_hiding_desktop_content(self):
        self.assertIn(".layer-details{display:block}", self.css)
        self.assertIn(".layer-details.mobile-collapsed.is-expanded{display:block", self.css)
        self.assertIn("layerDetails.classList.toggle('is-expanded',next)", self.js)
        self.assertIn("layerDetailsToggle.textContent=next?'收合':'詳細'", self.js)

    def test_layer_qc_summary_tracks_status(self):
        self.assertIn("function setQcSummary(tone,text)", self.js)
        self.assertIn("setQcSummary('ok','資料正常')", self.js)
        self.assertIn("setQcSummary('warn','需注意')", self.js)
        self.assertIn("setQcSummary('ok','觀測正常')", self.js)

    def test_ci_runs_ui_polish_contract(self):
        self.assertIn('"test_weathergrid_ui_polish.py"', self.workflow)
        self.assertIn("test_weathergrid_ui_polish.py", self.workflow)


    def test_photographer_first_controls_and_auto_provider_contract(self):
        self.assertIn('class="layer-control primary-control"', self.html)
        self.assertIn('攝影圖層', self.html)
        self.assertIn('class="model-control advanced-control"', self.html)
        self.assertIn('進階 · 資料來源', self.html)
        self.assertIn("function autoDataset(key=state.layer)", self.js)
        self.assertIn("function photographyLayerLabel(key)", self.js)
        self.assertIn("🌫️ 低雲／山霧", self.js)
        self.assertIn(".layer-control.primary-control{grid-column:span 2}", self.css)

    def test_auto_provider_prefers_available_regional_data_by_layer_and_time(self):
        self.assertIn("datasetHasFrameForLayer(data,key,validTime)", self.js)
        self.assertIn("[state.cwaData,state.jmaData,state.iconData,state.data]", self.js)
        self.assertIn("[state.cwaData,state.jmaData,state.data,state.iconData]", self.js)
        self.assertIn("if(data===state.cwaData) return state.cwaQc", self.js)
        self.assertIn("if(data===state.jmaData) return state.jmaQc", self.js)

    def test_b172_does_not_publish_unproven_composite_scores(self):
        self.assertNotIn("photography_overview:{", self.js)
        self.assertNotIn("function photographyCompositeArray(", self.js)
        self.assertNotIn("function photographyOverviewArray(", self.js)
        self.assertNotIn("0–100 題材環境指標", self.js)


if __name__ == "__main__":
    unittest.main()
