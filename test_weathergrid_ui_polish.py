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

    def test_direction_uses_speed_weighted_uv_circular_interpolation(self):
        self.assertIn("function windUv(speed,directionDeg)", self.js)
        self.assertIn("function bilinearWindDirection(", self.js)
        self.assertIn("drawCircularDirectionSubcells", self.js)
        self.assertIn("'bilinear_uv_circular'", self.js)
        self.assertIn("風向以 u/v 向量循環插值", self.js)

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
        self.assertIn("min-width:132px;max-width:46%", self.css)
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

    def test_ci_runs_ui_polish_contract(self):
        self.assertIn('"test_weathergrid_ui_polish.py"', self.workflow)
        self.assertIn("test_weathergrid_ui_polish.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
