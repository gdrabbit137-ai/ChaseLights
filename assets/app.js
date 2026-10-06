    const i18nDict = {
      'zh-TW': {
        page_title:'ChaseLights — 攝影氣象預報', country_aria:'國家／區域', temp_unit_aria:'溫度單位', weathergrid_title:'開啟 WeatherGrid 天氣圖', weathergrid_v2_title:'開啟 WeatherGrid V2 實驗頁', field_intake_title:'開啟實拍驗證', place_modal_title:'景點攝影資訊', weather_modal_title:'景點氣象分析', close_place:'關閉景點攝影資訊', close_weather:'關閉景點氣象分析', load_error:'暫時無法載入攝影氣象資料。',
        country_label:'📍 選擇國家/區域：', opt_tw:'🇹🇼 台灣', opt_jp:'🇯🇵 日本', opt_us:'🇺🇸 美國',
        btn_today:'📅 今天', btn_tomorrow:'📅 明天', btn_after_tomorrow:'📅 後天', loading:'正在獲取攝影氣象數據...', updating:'背景更新中…',
        last_updated:'最後更新：', click_detail:'查看詳細資訊', weather_link:'🌦️ 天氣預報', nav_link:'🗺️ 導航', map_link:'📍 地圖', nav_pending:'🗺️ 導航待確認', radar_link:'📡 雷達', field_intake_link:'📷 實拍驗證', place_suitable:'📸 這裡適合拍什麼', researched_only:'只顯示已逐點查證的攝影題材；未查證內容不自動生成。', place_time_note:'拍攝時間皆以景點當地時區顯示。', guide_selected_date:'📅 所選日期拍攝機會', guide_no_selected_date:'所選日期目前沒有明確的拍攝建議。', guide_more_subjects:'其他已查證拍攝題材（{n}）', guide_all_subjects:'查看這裡可以拍什麼（{n}）', guide_subjects_note:'以下是這個景點已查證的拍攝題材，不代表所選日期條件適合。', guide_time:'適合時間（景點當地時間）', guide_season:'季節', guide_viewpoint:'拍攝位置', guide_required:'成立條件', guide_boosters:'加分條件', guide_penalties:'不利條件', guide_current:'所選日期最佳評分', guide_day_best:'最佳拍攝時段', guide_confidence:'信心', confidence_high:'高', confidence_medium:'中', confidence_low:'低', guide_details:'拍攝指南', guide_score_why:'為什麼適合？', guide_score_status:'判定', guide_unresearched:'此景點尚未完成逐點攝影研究，因此暫不顯示推測性的拍攝建議。', research_pending_card:'攝影研究待補，暫不評分', no_viable_card:'所選日期沒有合適的已研究拍攝機會', no_viable_group:'暫無合適拍攝機會（{n}）', scene_label:'🖼️ 景觀類型：', theme_label:'📸 題材：', advanced_filters:'🔎 更多篩選', result_count:'依所選日期最佳拍攝機會排序 · {n} 個景點', search_result:'找到 {n} 個景點', search_placeholder:'搜尋景點名稱…', where_today:'📍 今天去哪裡拍？', where_tomorrow:'📍 明天去哪裡拍？', where_after:'📍 後天去哪裡拍？', recommendation_reasons:'推薦理由', narrow_result:'目前僅 {n} 個景點，範圍較窄', clear_scene:'清除景觀類型', admin_area_filter:'地區', admin_area_all:'全部地區', admin_area_selected:'已選 {n} 個地區', admin_area_clear:'清除地區', admin_area_search:'搜尋地區…', admin_area_no_match:'找不到符合的地區', admin_area_done:'完成', admin_area_close:'關閉地區選單', admin_area_show_empty:'顯示尚未收錄的地區', admin_area_hide_empty:'隱藏尚未收錄的地區', sort_label:'排序', sort_region:'地區順序', sort_score_desc:'評分：高到低', sort_score_asc:'評分：低到高', sort_distance_near:'距離：近到遠', sort_distance_far:'距離：遠到近', sort_location_requesting:'正在取得目前位置…', sort_location_using_current:'以目前位置排序', sort_location_unavailable:'無法取得位置，已改回地區順序', result_count_region:'依地區順序 · {n} 個景點', result_count_score_desc:'依評分高到低 · {n} 個景點', result_count_score_asc:'依評分低到高 · {n} 個景點', result_count_distance_near:'依距離近到遠 · {n} 個景點', result_count_distance_far:'依距離遠到近 · {n} 個景點', region_group_count:'{n} 個景點',
        best_window:'⏱️ 最佳拍攝時段：', forecast_status:'📍 預報狀態：', cloud_base_label:'估算凝結高度', best_theme:'📸 所選日期較適合：', local_time:'當地時間', dark_sky:'暗空',
        modal_subtitle:'⏱️ 逐時拍攝條件：過去 24 小時 + 未來 72 小時（藍底＝所選日期中相對較佳的時段；仍需看整體評分與條件）', tag_best:'最佳',
        th_time:'時間', th_theme:'題材', th_score:'評分', th_status:'狀態', th_kp:'Kp指數', th_cloud_base:'凝結高度', th_temp:'氣溫', th_rh:'濕度', th_clow:'低雲', th_cmid:'中雲', th_chigh:'高雲', th_wind:'風速', th_vis:'能見度', th_astro:'天文', no_spots:'此條件下沒有景點', detail_loading:'正在載入天氣預報…', detail_sync_wait:'天氣資料正在同步更新，請幾秒後再試一次。', detail_error:'暫時無法載入天氣預報。', status_unavailable:'目前無法顯示狀態說明', favorite_label:'我的最愛', tag_past:'歷史', guide_translation_limited:'部分拍攝指南尚未提供繁體中文版本。', score_excellent:'極佳', score_good:'良好', score_fair:'普通', score_low_label:'較弱', verdict_suitable:'✅ 適合拍攝{subject}', verdict_chance:'🟡 有機會拍到{subject}', verdict_unfavorable:'⚠️ 目前不利於拍攝{subject}', verdict_outside:'🕒 目前不是拍攝{subject}的建議時段'
      },
      'en': {
        page_title:'ChaseLights — Photography Weather Forecast', country_aria:'Country / region', temp_unit_aria:'Temperature unit', weathergrid_title:'Open WeatherGrid weather map', weathergrid_v2_title:'Open WeatherGrid V2 experiment', field_intake_title:'Open field validation', place_modal_title:'Place photography guide', weather_modal_title:'Place weather analysis', close_place:'Close place photography guide', close_weather:'Close place weather analysis', load_error:'Photography weather data is temporarily unavailable.',
        country_label:'📍 Select Region:', opt_tw:'🇹🇼 Taiwan', opt_jp:'🇯🇵 Japan', opt_us:'🇺🇸 United States',
        btn_today:'📅 Today', btn_tomorrow:'📅 Tomorrow', btn_after_tomorrow:'📅 Day After', loading:'Fetching photography weather data...', updating:'Updating in background…',
        last_updated:'Last Updated: ', click_detail:'View details', weather_link:'🌦️ Weather', nav_link:'🗺️ Nav', map_link:'📍 Map', nav_pending:'🗺️ Nav pending', radar_link:'📡 Radar', field_intake_link:'📷 Field Check', place_suitable:'📸 What can you photograph here?', researched_only:'Only individually researched photography opportunities are shown; unverified ideas are not generated.', place_time_note:'Shooting times are shown in the place’s local time zone.', guide_selected_date:'📅 Selected-date shooting opportunities', guide_no_selected_date:'There is no clear shooting recommendation for the selected date.', guide_more_subjects:'Other verified subjects ({n})', guide_all_subjects:'What can you photograph here? ({n})', guide_subjects_note:'These are verified subjects for this place; they do not imply suitable conditions on the selected date.', guide_time:'Best time (place local time)', guide_season:'Season', guide_viewpoint:'Shooting area', guide_required:'Required conditions', guide_boosters:'Boosters', guide_penalties:'Penalties', guide_current:'Best score for selected date', guide_day_best:'Best shooting time', guide_confidence:'Confidence', confidence_high:'High', confidence_medium:'Medium', confidence_low:'Low', guide_details:'Shooting guide', guide_score_why:'Why is this suitable?', guide_score_status:'Assessment', guide_unresearched:'This place has not yet completed place-specific photography research, so no speculative shooting guide is shown.', research_pending_card:'Photography research pending · not scored yet', no_viable_card:'No researched shooting opportunity is suitable for the selected date', no_viable_group:'No viable shooting opportunity ({n})', scene_label:'🖼️ Landscape type:', theme_label:'📸 Subject:', advanced_filters:'🔎 More filters', result_count:'Ranked by best opportunity for selected date · {n} spots', search_result:'Found {n} spots', search_placeholder:'Search places…', where_today:'📍 Where should I shoot today?', where_tomorrow:'📍 Where should I shoot tomorrow?', where_after:'📍 Where should I shoot the day after tomorrow?', recommendation_reasons:'Why it stands out', narrow_result:'Only {n} spots — narrow filter', clear_scene:'Clear landscape type', admin_area_filter:'Area', admin_area_all:'All areas', admin_area_selected:'{n} selected', admin_area_clear:'Clear areas', admin_area_search:'Search areas…', admin_area_no_match:'No matching area', admin_area_done:'Done', admin_area_close:'Close area picker', admin_area_show_empty:'Show areas not yet covered', admin_area_hide_empty:'Hide areas not yet covered', sort_label:'Sort', sort_region:'Geographic order', sort_score_desc:'Score: high to low', sort_score_asc:'Score: low to high', sort_distance_near:'Distance: near to far', sort_distance_far:'Distance: far to near', sort_location_requesting:'Getting your current location…', sort_location_using_current:'Sorted from current location', sort_location_unavailable:'Location unavailable; switched to geographic order', result_count_region:'Geographic order · {n} spots', result_count_score_desc:'Score high to low · {n} spots', result_count_score_asc:'Score low to high · {n} spots', result_count_distance_near:'Nearest first · {n} spots', result_count_distance_far:'Farthest first · {n} spots', region_group_count:'{n} spots',
        best_window:'⏱️ Best shooting time: ', forecast_status:'📍 Status: ', cloud_base_label:'Est. LCL', best_theme:'📸 Best for selected date: ', local_time:'Local time', dark_sky:'Dark sky',
        modal_subtitle:'⏱️ Hourly shooting conditions: past 24 hours + next 72 hours (blue = a relatively better time on the selected date; check the overall score and conditions)', tag_best:'BEST',
        th_time:'Time', th_theme:'Theme', th_score:'Score', th_status:'Status', th_kp:'Kp', th_cloud_base:'LCL', th_temp:'Temp', th_rh:'RH', th_clow:'Low', th_cmid:'Mid', th_chigh:'High', th_wind:'Wind', th_vis:'Visibility', th_astro:'Astronomy', no_spots:'No spots match these filters', detail_loading:'Loading weather forecast…', detail_sync_wait:'Weather data is synchronizing. Please try again in a few seconds.', detail_error:'Weather forecast is temporarily unavailable.', status_unavailable:'Status details are temporarily unavailable', favorite_label:'Favorite', tag_past:'Past', guide_translation_limited:'Some shooting-guide details are not yet available in English.', score_excellent:'Excellent', score_good:'Good', score_fair:'Fair', score_low_label:'Low', verdict_suitable:'✅ Suitable for photographing {subject}', verdict_chance:'🟡 A chance to capture {subject}', verdict_unfavorable:'⚠️ Currently unfavorable for photographing {subject}', verdict_outside:'🕒 This is not the recommended time for photographing {subject}'
      },
      'ja': {
        page_title:'ChaseLights — 撮影向け気象予報', country_aria:'国・地域', temp_unit_aria:'温度単位', weathergrid_title:'WeatherGrid 天気マップを開く', weathergrid_v2_title:'WeatherGrid V2 実験ページを開く', field_intake_title:'実写検証を開く', place_modal_title:'撮影スポットガイド', weather_modal_title:'撮影スポット気象分析', close_place:'撮影スポットガイドを閉じる', close_weather:'撮影スポット気象分析を閉じる', load_error:'撮影向け気象データを一時的に読み込めません。',
        country_label:'📍 地域を選択：', opt_tw:'🇹🇼 台湾', opt_jp:'🇯🇵 日本', opt_us:'🇺🇸 アメリカ',
        btn_today:'📅 今日', btn_tomorrow:'📅 明日', btn_after_tomorrow:'📅 明後日', loading:'撮影気象データを取得中...', updating:'バックグラウンド更新中…',
        last_updated:'最終更新：', click_detail:'詳細を見る', weather_link:'🌦️ 天気予報', nav_link:'🗺️ ナビ', map_link:'📍 地図', nav_pending:'🗺️ ナビ確認待ち', radar_link:'📡 レーダー', field_intake_link:'📷 実写検証', place_suitable:'📸 ここで何が撮れる？', researched_only:'個別調査済みの撮影機会のみ表示し、未確認の内容は自動生成しません。', place_time_note:'撮影時間はすべて現地のタイムゾーンで表示します。', guide_selected_date:'📅 選択日の撮影機会', guide_no_selected_date:'選択日には明確におすすめできる撮影時間がありません。', guide_more_subjects:'その他の確認済み撮影テーマ（{n}）', guide_all_subjects:'ここで撮影できるものを見る（{n}）', guide_subjects_note:'以下はこの場所で確認済みの撮影テーマです。選択日の条件が適していることを意味しません。', guide_time:'適した時間（現地時間）', guide_season:'季節', guide_viewpoint:'撮影位置', guide_required:'成立条件', guide_boosters:'加点条件', guide_penalties:'不利条件', guide_current:'選択日の最良スコア', guide_day_best:'最適な撮影時間', guide_confidence:'信頼度', confidence_high:'高', confidence_medium:'中', confidence_low:'低', guide_details:'撮影ガイド', guide_score_why:'なぜ撮影に適している？', guide_score_status:'判定', guide_unresearched:'この場所は個別撮影調査が未完了のため、推測的な撮影案内は表示しません。', research_pending_card:'撮影調査待ち・現在は採点しません', no_viable_card:'選択日に適した調査済みの撮影機会はありません', no_viable_group:'適した撮影機会なし（{n}）', scene_label:'🖼️ 景観タイプ：', theme_label:'📸 テーマ：', advanced_filters:'🔎 その他の絞り込み', result_count:'選択日の最良撮影機会順 · {n} スポット', search_result:'{n} スポット見つかりました', search_placeholder:'スポット名を検索…', where_today:'📍 今日はどこへ撮りに行く？', where_tomorrow:'📍 明日はどこへ撮りに行く？', where_after:'📍 明後日はどこへ撮りに行く？', recommendation_reasons:'おすすめ理由', narrow_result:'{n} スポットのみ・絞り込みが狭いです', clear_scene:'景観タイプを解除', admin_area_filter:'地域', admin_area_all:'すべての地域', admin_area_selected:'{n} 件選択', admin_area_clear:'地域を解除', admin_area_search:'地域を検索…', admin_area_no_match:'該当する地域がありません', admin_area_done:'完了', admin_area_close:'地域選択を閉じる', admin_area_show_empty:'未収録の地域を表示', admin_area_hide_empty:'未収録の地域を隠す', sort_label:'並び順', sort_region:'地域順', sort_score_desc:'評価：高い順', sort_score_asc:'評価：低い順', sort_distance_near:'距離：近い順', sort_distance_far:'距離：遠い順', sort_location_requesting:'現在地を取得中…', sort_location_using_current:'現在地からの距離順', sort_location_unavailable:'現在地を取得できないため地域順に戻しました', result_count_region:'地域順 · {n} スポット', result_count_score_desc:'評価の高い順 · {n} スポット', result_count_score_asc:'評価の低い順 · {n} スポット', result_count_distance_near:'近い順 · {n} スポット', result_count_distance_far:'遠い順 · {n} スポット', region_group_count:'{n} スポット',
        best_window:'⏱️ 最適時間：', forecast_status:'📍 予報状況：', cloud_base_label:'推定LCL', best_theme:'📸 選択日に向く：', local_time:'現地時間', dark_sky:'暗空',
        modal_subtitle:'⏱️ 時間別の撮影条件：過去24時間＋未来72時間（青色＝選択日の中で相対的に条件が良い時間帯。総合評価と条件も確認してください）', tag_best:'最適',
        th_time:'時間', th_theme:'テーマ', th_score:'評価', th_status:'状態', th_kp:'Kp', th_cloud_base:'LCL', th_temp:'気温', th_rh:'湿度', th_clow:'下層雲', th_cmid:'中層雲', th_chigh:'上層雲', th_wind:'風速', th_vis:'視程', th_astro:'天文', no_spots:'該当する撮影スポットはありません', detail_loading:'天気予報を読み込み中…', detail_sync_wait:'天気データを同期更新中です。数秒後にもう一度お試しください。', detail_error:'天気予報を一時的に読み込めません。', status_unavailable:'状態の説明を一時的に表示できません', favorite_label:'お気に入り', tag_past:'過去', guide_translation_limited:'撮影ガイドの一部はまだ日本語に対応していません。', score_excellent:'非常に良い', score_good:'良好', score_fair:'普通', score_low_label:'弱め', verdict_suitable:'✅ {subject}の撮影に適しています', verdict_chance:'🟡 {subject}を撮影できる可能性があります', verdict_unfavorable:'⚠️ 現在は{subject}の撮影に不利です', verdict_outside:'🕒 現在は{subject}の推奨撮影時間帯ではありません'
      }
    };

    const categoryKeys = {
      // Geography is handled by the country-aware first-level administrative
      // area picker. Favorites stays a separate on/off filter in every region.
      tw:['__fav__'],
      jp:['__fav__'],
      us:['__fav__']
    };
    const categoryLabels = {
      'zh-TW':{__all__:'全部',__fav__:'⭐ 我的最愛','本島':'本島','澎湖':'澎湖','金門':'金門','馬祖':'馬祖','綠島/蘭嶼/小琉球':'綠島/蘭嶼/小琉球','北海道/東北':'北海道/東北','關東/中部':'關東/中部','關西/中四國':'關西/中四國','九州/沖繩':'九州/沖繩','美西':'美西','美中':'美中','美東':'美東','阿拉斯加':'阿拉斯加'},
      en:{__all__:'All',__fav__:'⭐ Favorites','本島':'Main Island','澎湖':'Penghu','金門':'Kinmen','馬祖':'Matsu','綠島/蘭嶼/小琉球':'Islands','北海道/東北':'Hokkaido/Tohoku','關東/中部':'Kanto/Chubu','關西/中四國':'Kansai/Chugoku','九州/沖繩':'Kyushu/Okinawa','美西':'US West','美中':'US Central','美東':'US East','阿拉斯加':'Alaska'},
      ja:{__all__:'すべて',__fav__:'⭐ お気に入り','本島':'本島','澎湖':'澎湖','金門':'金門','馬祖':'馬祖','綠島/蘭嶼/小琉球':'離島','北海道/東北':'北海道/東北','關東/中部':'関東/中部','關西/中四國':'関西/中国・四国','九州/沖繩':'九州/沖縄','美西':'全米西部','美中':'全米中部','美東':'全米東部','阿拉斯加':'アラスカ'}
    };
    const sceneLabels = {
      'zh-TW':{all:'🌐 全部場景',mountain:'🏔️ 山岳',coast:'🌊 海岸',lake:'🏞️ 湖泊',river:'🏞️ 河川溪流',waterfall:'💦 瀑布',forest:'🌲 森林',wetland:'🦆 濕地',geology:'🪨 地質奇景',desert:'🏜️ 沙漠荒原',grassland:'🌾 草原',rural:'🌾 田園',snow_ice:'❄️ 冰雪冰川',city:'🏙️ 城市',architecture:'🏛️ 建築地標'},
      en:{all:'🌐 All Scenes',mountain:'🏔️ Mountain',coast:'🌊 Coast',lake:'🏞️ Lake',river:'🏞️ River',waterfall:'💦 Waterfall',forest:'🌲 Forest',wetland:'🦆 Wetland',geology:'🪨 Geology',desert:'🏜️ Desert',grassland:'🌾 Grassland',rural:'🌾 Rural',snow_ice:'❄️ Snow/Ice',city:'🏙️ City',architecture:'🏛️ Architecture'},
      ja:{all:'🌐 全シーン',mountain:'🏔️ 山岳',coast:'🌊 海岸',lake:'🏞️ 湖',river:'🏞️ 河川',waterfall:'💦 滝',forest:'🌲 森林',wetland:'🦆 湿地',geology:'🪨 地質景観',desert:'🏜️ 砂漠',grassland:'🌾 草原',rural:'🌾 田園',snow_ice:'❄️ 雪・氷河',city:'🏙️ 都市',architecture:'🏛️ 建築'}
    };
    const themeLabels = {
      'zh-TW':{all:'🌐 全部題材',mountain_view:'🏔️ 山景展望',alpine_lake:'🏔️ 高山湖',sunrise:'🌅 日出',sunset:'🌇 日落',blue_hour:'🔵 藍調時刻',sky_glow:'🌈 彩霞',cloud_sea:'☁️ 雲海',fog_mist:'🌫️ 霧景',reflection:'🪞 倒影',sunbeam:'🌤️ 光束',milky_way:'🌌 銀河星空',long_exposure:'💧 長曝水景',city_night:'🌃 夜景',city_view:'🏙️ 城市景觀',coast:'🌊 海岸景觀',forest:'🌲 森林',geology:'🪨 地質景觀',lake:'🏞️ 湖景',landscape:'📷 風景',waterfall:'💦 瀑布',snow_scene:'❄️ 冰雪景觀',aurora:'🌌 極光'},
      en:{all:'🌐 All subjects',mountain_view:'🏔️ Mountain View',alpine_lake:'🏔️ Alpine Lake',sunrise:'🌅 Sunrise',sunset:'🌇 Sunset',blue_hour:'🔵 Blue Hour',sky_glow:'🌈 Sky Glow',cloud_sea:'☁️ Sea of Clouds',fog_mist:'🌫️ Mist/Fog',reflection:'🪞 Reflection',sunbeam:'🌤️ Sunbeams',milky_way:'🌌 Milky Way',long_exposure:'💧 Long Exposure',city_night:'🌃 Night Scene',city_view:'🏙️ City View',coast:'🌊 Coast',forest:'🌲 Forest',geology:'🪨 Geology',lake:'🏞️ Lake',landscape:'📷 Landscape',waterfall:'💦 Waterfall',snow_scene:'❄️ Snow/Ice',aurora:'🌌 Aurora'},
      ja:{all:'🌐 全テーマ',mountain_view:'🏔️ 山岳展望',alpine_lake:'🏔️ 高山湖',sunrise:'🌅 日の出',sunset:'🌇 日没',blue_hour:'🔵 ブルーアワー',sky_glow:'🌈 朝夕焼け',cloud_sea:'☁️ 雲海',fog_mist:'🌫️ 霧景',reflection:'🪞 水面反射',sunbeam:'🌤️ 光芒',milky_way:'🌌 天の川',long_exposure:'💧 長秒露光',city_night:'🌃 夜景',city_view:'🏙️ 都市景観',coast:'🌊 海岸景観',forest:'🌲 森林',geology:'🪨 地質景観',lake:'🏞️ 湖景',landscape:'📷 風景',waterfall:'💦 滝',snow_scene:'❄️ 雪氷景観',aurora:'🌌 オーロラ'}
    };

    const TW_ADMIN_AREA_ORDER=[
      '台北市','新北市','基隆市','桃園市','新竹市','新竹縣','苗栗縣','台中市',
      '彰化縣','南投縣','雲林縣','嘉義市','嘉義縣','台南市','高雄市','屏東縣',
      '宜蘭縣','花蓮縣','台東縣','澎湖縣','金門縣','連江縣'
    ];

    const TW_BROWSE_AREA_GROUPS=[
      {key:'tw_north',areas:['台北市','新北市','基隆市','桃園市','新竹市','新竹縣']},
      {key:'tw_central',areas:['苗栗縣','台中市','彰化縣','南投縣','雲林縣']},
      {key:'tw_south',areas:['嘉義市','嘉義縣','台南市','高雄市','屏東縣']},
      {key:'tw_east',areas:['宜蘭縣','花蓮縣','台東縣']},
      {key:'tw_islands',areas:['澎湖縣','金門縣','連江縣']}
    ];

    const JP_ADMIN_AREA_GROUPS=[
      {key:'jp_hokkaido',areas:['北海道']},
      {key:'jp_tohoku',areas:['青森県','岩手県','宮城県','秋田県','山形県','福島県']},
      {key:'jp_kanto',areas:['茨城県','栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県']},
      {key:'jp_chubu',areas:['新潟県','富山県','石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県']},
      {key:'jp_kinki',areas:['三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県']},
      {key:'jp_chugoku',areas:['鳥取県','島根県','岡山県','広島県','山口県']},
      {key:'jp_shikoku',areas:['徳島県','香川県','愛媛県','高知県']},
      {key:'jp_kyushu_okinawa',areas:['福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県']}
    ];

    const US_ADMIN_AREA_GROUPS=[
      {key:'us_northeast',areas:['Connecticut','Maine','Massachusetts','New Hampshire','Rhode Island','Vermont','New Jersey','New York','Pennsylvania']},
      {key:'us_midwest',areas:['Indiana','Illinois','Michigan','Ohio','Wisconsin','Iowa','Kansas','Minnesota','Missouri','Nebraska','North Dakota','South Dakota']},
      {key:'us_south',areas:['Delaware','Florida','Georgia','Maryland','North Carolina','South Carolina','Virginia','District of Columbia','West Virginia','Alabama','Kentucky','Mississippi','Tennessee','Arkansas','Louisiana','Oklahoma','Texas']},
      {key:'us_west',areas:['Montana','Idaho','Wyoming','Colorado','New Mexico','Arizona','Utah','Nevada','Alaska','California','Hawaii','Oregon','Washington']}
    ];

    const ADMIN_AREA_GROUPS={
      tw:[{key:'tw_counties',areas:TW_ADMIN_AREA_ORDER}],
      jp:JP_ADMIN_AREA_GROUPS,
      us:US_ADMIN_AREA_GROUPS
    };
    const BROWSE_AREA_GROUPS={
      tw:TW_BROWSE_AREA_GROUPS,
      jp:JP_ADMIN_AREA_GROUPS,
      us:US_ADMIN_AREA_GROUPS
    };

    // Compatibility bridge for cached / pre-B137 weather snapshots that do not
    // yet carry admin_areas. Fresh snapshots get this metadata from regions.py.
    const ADMIN_AREA_FALLBACK={
      jp:{
        'jp-001':['北海道'],'jp-002':['北海道'],'jp-003':['北海道'],'jp-004':['北海道'],'jp-005':['北海道'],'jp-006':['北海道'],
        'jp-007':['青森県','秋田県'],'jp-008':['宮城県'],'jp-009':['福島県'],'jp-010':['山梨県'],'jp-011':['東京都'],'jp-012':['神奈川県'],
        'jp-013':['長野県'],'jp-014':['東京都'],'jp-015':['東京都'],'jp-016':['神奈川県'],'jp-017':['石川県'],'jp-018':['愛知県'],
        'jp-019':['静岡県'],'jp-020':['神奈川県'],'jp-021':['岐阜県'],'jp-022':['新潟県'],'jp-023':['京都府'],'jp-024':['大阪府'],
        'jp-025':['山口県'],'jp-026':['島根県'],'jp-027':['兵庫県'],'jp-028':['和歌山県'],'jp-029':['三重県'],'jp-030':['徳島県'],
        'jp-031':['岡山県'],'jp-032':['福岡県'],'jp-033':['佐賀県'],'jp-034':['長崎県'],'jp-035':['福岡県']
      },
      us:{
        'us-001':['Arizona'],'us-002':['Arizona'],'us-003':['Arizona'],'us-004':['Arizona'],'us-005':['Utah'],'us-006':['Utah'],'us-007':['Utah'],
        'us-008':['California'],'us-009':['California'],'us-010':['Wyoming'],'us-011':['Wyoming'],'us-012':['Washington'],'us-013':['Oregon'],
        'us-014':['California','Nevada'],'us-015':['California'],'us-016':['Nevada'],'us-017':['Washington'],'us-018':['Montana'],'us-019':['Washington'],
        'us-020':['California'],'us-021':['Utah'],'us-022':['California'],'us-023':['Arizona'],'us-024':['Washington'],'us-025':['California'],
        'us-026':['Washington'],'us-027':['Idaho'],'us-028':['California'],'us-029':['New Mexico'],'us-030':['Illinois'],'us-031':['Colorado'],
        'us-032':['Louisiana'],'us-033':['Colorado'],'us-034':['Missouri'],'us-035':['Texas'],'us-036':['New York'],'us-037':['New York'],
        'us-038':['Tennessee','North Carolina'],'us-039':['Florida'],'us-040':['Massachusetts'],
        'us-041':['Alaska'],'us-042':['Alaska'],'us-043':['Alaska'],'us-044':['Alaska'],'us-045':['Alaska'],'us-046':['Alaska'],'us-047':['Alaska'],
        'us-048':['Alaska'],'us-049':['Alaska'],'us-050':['Alaska'],'us-051':['Alaska'],'us-052':['Alaska'],'us-053':['Alaska'],'us-054':['Alaska'],
        'us-055':['Alaska'],'us-056':['Alaska'],'us-057':['Alaska'],'us-058':['Alaska'],'us-059':['Alaska'],'us-060':['Alaska'],'us-061':['Alaska'],
        'us-062':['Alaska'],'us-063':['Alaska'],'us-064':['Alaska'],'us-065':['Alaska'],'us-066':['Alaska'],'us-067':['Alaska'],'us-068':['Alaska'],
        'us-069':['Alaska'],'us-070':['Alaska']
      }
    };
    const spotAdminAreas=s=>{
      const areas=Array.isArray(s?.admin_areas)?s.admin_areas.filter(Boolean):[];
      return areas.length?areas:(ADMIN_AREA_FALLBACK[currentRegion]?.[s?.spot_id]||[]);
    };

    const JP_AREA_EN={
      '北海道':'Hokkaido','青森県':'Aomori','岩手県':'Iwate','宮城県':'Miyagi','秋田県':'Akita','山形県':'Yamagata','福島県':'Fukushima',
      '茨城県':'Ibaraki','栃木県':'Tochigi','群馬県':'Gunma','埼玉県':'Saitama','千葉県':'Chiba','東京都':'Tokyo','神奈川県':'Kanagawa',
      '新潟県':'Niigata','富山県':'Toyama','石川県':'Ishikawa','福井県':'Fukui','山梨県':'Yamanashi','長野県':'Nagano','岐阜県':'Gifu','静岡県':'Shizuoka','愛知県':'Aichi',
      '三重県':'Mie','滋賀県':'Shiga','京都府':'Kyoto','大阪府':'Osaka','兵庫県':'Hyogo','奈良県':'Nara','和歌山県':'Wakayama',
      '鳥取県':'Tottori','島根県':'Shimane','岡山県':'Okayama','広島県':'Hiroshima','山口県':'Yamaguchi',
      '徳島県':'Tokushima','香川県':'Kagawa','愛媛県':'Ehime','高知県':'Kochi',
      '福岡県':'Fukuoka','佐賀県':'Saga','長崎県':'Nagasaki','熊本県':'Kumamoto','大分県':'Oita','宮崎県':'Miyazaki','鹿児島県':'Kagoshima','沖縄県':'Okinawa'
    };
    const JP_AREA_ZH={
      '北海道':'北海道','青森県':'青森縣','岩手県':'岩手縣','宮城県':'宮城縣','秋田県':'秋田縣','山形県':'山形縣','福島県':'福島縣',
      '茨城県':'茨城縣','栃木県':'栃木縣','群馬県':'群馬縣','埼玉県':'埼玉縣','千葉県':'千葉縣','東京都':'東京都','神奈川県':'神奈川縣',
      '新潟県':'新潟縣','富山県':'富山縣','石川県':'石川縣','福井県':'福井縣','山梨県':'山梨縣','長野県':'長野縣','岐阜県':'岐阜縣','静岡県':'靜岡縣','愛知県':'愛知縣',
      '三重県':'三重縣','滋賀県':'滋賀縣','京都府':'京都府','大阪府':'大阪府','兵庫県':'兵庫縣','奈良県':'奈良縣','和歌山県':'和歌山縣',
      '鳥取県':'鳥取縣','島根県':'島根縣','岡山県':'岡山縣','広島県':'廣島縣','山口県':'山口縣',
      '徳島県':'德島縣','香川県':'香川縣','愛媛県':'愛媛縣','高知県':'高知縣',
      '福岡県':'福岡縣','佐賀県':'佐賀縣','長崎県':'長崎縣','熊本県':'熊本縣','大分県':'大分縣','宮崎県':'宮崎縣','鹿児島県':'鹿兒島縣','沖縄県':'沖繩縣'
    };

    const US_AREA_ZH={
      'Alabama':'阿拉巴馬州','Alaska':'阿拉斯加州','Arizona':'亞利桑那州','Arkansas':'阿肯色州','California':'加利福尼亞州',
      'Colorado':'科羅拉多州','Connecticut':'康乃狄克州','Delaware':'德拉瓦州','Florida':'佛羅里達州','Georgia':'喬治亞州',
      'Hawaii':'夏威夷州','Idaho':'愛達荷州','Illinois':'伊利諾州','Indiana':'印第安納州','Iowa':'愛荷華州','Kansas':'堪薩斯州',
      'Kentucky':'肯塔基州','Louisiana':'路易斯安那州','Maine':'緬因州','Maryland':'馬里蘭州','Massachusetts':'麻薩諸塞州',
      'Michigan':'密西根州','Minnesota':'明尼蘇達州','Mississippi':'密西西比州','Missouri':'密蘇里州','Montana':'蒙大拿州',
      'Nebraska':'內布拉斯加州','Nevada':'內華達州','New Hampshire':'新罕布夏州','New Jersey':'紐澤西州','New Mexico':'新墨西哥州',
      'New York':'紐約州','North Carolina':'北卡羅來納州','North Dakota':'北達科他州','Ohio':'俄亥俄州','Oklahoma':'奧克拉荷馬州',
      'Oregon':'奧勒岡州','Pennsylvania':'賓夕法尼亞州','Rhode Island':'羅德島州','South Carolina':'南卡羅來納州',
      'South Dakota':'南達科他州','Tennessee':'田納西州','Texas':'德克薩斯州','Utah':'猶他州','Vermont':'佛蒙特州',
      'Virginia':'維吉尼亞州','Washington':'華盛頓州','West Virginia':'西維吉尼亞州','Wisconsin':'威斯康辛州','Wyoming':'懷俄明州',
      'District of Columbia':'華盛頓特區'
    };
    const US_AREA_JA={
      'Alabama':'アラバマ州','Alaska':'アラスカ州','Arizona':'アリゾナ州','Arkansas':'アーカンソー州','California':'カリフォルニア州',
      'Colorado':'コロラド州','Connecticut':'コネチカット州','Delaware':'デラウェア州','Florida':'フロリダ州','Georgia':'ジョージア州',
      'Hawaii':'ハワイ州','Idaho':'アイダホ州','Illinois':'イリノイ州','Indiana':'インディアナ州','Iowa':'アイオワ州','Kansas':'カンザス州',
      'Kentucky':'ケンタッキー州','Louisiana':'ルイジアナ州','Maine':'メイン州','Maryland':'メリーランド州','Massachusetts':'マサチューセッツ州',
      'Michigan':'ミシガン州','Minnesota':'ミネソタ州','Mississippi':'ミシシッピ州','Missouri':'ミズーリ州','Montana':'モンタナ州',
      'Nebraska':'ネブラスカ州','Nevada':'ネバダ州','New Hampshire':'ニューハンプシャー州','New Jersey':'ニュージャージー州','New Mexico':'ニューメキシコ州',
      'New York':'ニューヨーク州','North Carolina':'ノースカロライナ州','North Dakota':'ノースダコタ州','Ohio':'オハイオ州','Oklahoma':'オクラホマ州',
      'Oregon':'オレゴン州','Pennsylvania':'ペンシルベニア州','Rhode Island':'ロードアイランド州','South Carolina':'サウスカロライナ州',
      'South Dakota':'サウスダコタ州','Tennessee':'テネシー州','Texas':'テキサス州','Utah':'ユタ州','Vermont':'バーモント州',
      'Virginia':'バージニア州','Washington':'ワシントン州','West Virginia':'ウェストバージニア州','Wisconsin':'ウィスコンシン州','Wyoming':'ワイオミング州',
      'District of Columbia':'ワシントンD.C.'
    };

    const adminAreaLabels={
      'zh-TW':{
        '台北市':'台北市','新北市':'新北市','基隆市':'基隆市','桃園市':'桃園市','新竹市':'新竹市','新竹縣':'新竹縣','苗栗縣':'苗栗縣','台中市':'台中市','彰化縣':'彰化縣','南投縣':'南投縣','雲林縣':'雲林縣','嘉義市':'嘉義市','嘉義縣':'嘉義縣','台南市':'台南市','高雄市':'高雄市','屏東縣':'屏東縣','宜蘭縣':'宜蘭縣','花蓮縣':'花蓮縣','台東縣':'台東縣','澎湖縣':'澎湖縣','金門縣':'金門縣','連江縣':'連江縣',
        ...JP_AREA_ZH,...US_AREA_ZH
      },
      en:{
        '台北市':'Taipei','新北市':'New Taipei','基隆市':'Keelung','桃園市':'Taoyuan','新竹市':'Hsinchu City','新竹縣':'Hsinchu County','苗栗縣':'Miaoli','台中市':'Taichung','彰化縣':'Changhua','南投縣':'Nantou','雲林縣':'Yunlin','嘉義市':'Chiayi City','嘉義縣':'Chiayi County','台南市':'Tainan','高雄市':'Kaohsiung','屏東縣':'Pingtung','宜蘭縣':'Yilan','花蓮縣':'Hualien','台東縣':'Taitung','澎湖縣':'Penghu','金門縣':'Kinmen','連江縣':'Lienchiang',
        ...JP_AREA_EN
      },
      ja:{
        '台北市':'台北市','新北市':'新北市','基隆市':'基隆市','桃園市':'桃園市','新竹市':'新竹市','新竹縣':'新竹県','苗栗縣':'苗栗県','台中市':'台中市','彰化縣':'彰化県','南投縣':'南投県','雲林縣':'雲林県','嘉義市':'嘉義市','嘉義縣':'嘉義県','台南市':'台南市','高雄市':'高雄市','屏東縣':'屏東県','宜蘭縣':'宜蘭県','花蓮縣':'花蓮県','台東縣':'台東県','澎湖縣':'澎湖県','金門縣':'金門県','連江縣':'連江県',
        ...US_AREA_JA
      }
    };

    const adminAreaGroupLabels={
      'zh-TW':{
        tw_counties:'縣市',tw_north:'北部',tw_central:'中部',tw_south:'南部',tw_east:'東部',tw_islands:'離島',jp_hokkaido:'北海道',jp_tohoku:'東北',jp_kanto:'關東',jp_chubu:'中部',jp_kinki:'近畿',jp_chugoku:'中國',jp_shikoku:'四國',jp_kyushu_okinawa:'九州・沖繩',
        us_northeast:'東北部',us_midwest:'中西部',us_south:'南部',us_west:'西部'
      },
      en:{
        tw_counties:'Counties / cities',tw_north:'North',tw_central:'Central',tw_south:'South',tw_east:'East',tw_islands:'Offshore islands',jp_hokkaido:'Hokkaido',jp_tohoku:'Tohoku',jp_kanto:'Kanto',jp_chubu:'Chubu',jp_kinki:'Kinki',jp_chugoku:'Chugoku',jp_shikoku:'Shikoku',jp_kyushu_okinawa:'Kyushu / Okinawa',
        us_northeast:'Northeast',us_midwest:'Midwest',us_south:'South',us_west:'West'
      },
      ja:{
        tw_counties:'県・市',tw_north:'北部',tw_central:'中部',tw_south:'南部',tw_east:'東部',tw_islands:'離島',jp_hokkaido:'北海道',jp_tohoku:'東北',jp_kanto:'関東',jp_chubu:'中部',jp_kinki:'近畿',jp_chugoku:'中国',jp_shikoku:'四国',jp_kyushu_okinawa:'九州・沖縄',
        us_northeast:'北東部',us_midwest:'中西部',us_south:'南部',us_west:'西部'
      }
    };
    const adminAreaKindLabels={
      'zh-TW':{tw:'縣市',jp:'都道府縣',us:'州'},
      en:{tw:'County / City',jp:'Prefecture',us:'State'},
      ja:{tw:'県・市',jp:'都道府県',us:'州'}
    };
    const adminAreaLabel=a=>(adminAreaLabels[currentLang]||{})[a]||a;
    const adminAreaGroupLabel=k=>(adminAreaGroupLabels[currentLang]||{})[k]||k;
    const adminAreaKindLabel=()=>((adminAreaKindLabels[currentLang]||{})[currentRegion]||d().admin_area_filter);
    const adminAreaSearchPlaceholders={
      'zh-TW':{tw:'搜尋縣市…',jp:'搜尋都道府縣…',us:'搜尋州…'},
      en:{tw:'Search counties / cities…',jp:'Search prefectures…',us:'Search states…'},
      ja:{tw:'県・市を検索…',jp:'都道府県を検索…',us:'州を検索…'}
    };
    const adminAreaSearchPlaceholder=()=>((adminAreaSearchPlaceholders[currentLang]||{})[currentRegion]||d().admin_area_search);


    const VALID_REGIONS=['tw','jp','us'], VALID_LANGS=['zh-TW','en','ja'], VALID_DAYS=['today','tomorrow','after_tomorrow'];
    const VALID_SORT_MODES=['region','score_desc','score_asc','distance_near','distance_far'];
    let currentRegion=VALID_REGIONS.includes(localStorage.getItem('chaselights_region'))?localStorage.getItem('chaselights_region'):'tw';
    let currentLang=VALID_LANGS.includes(localStorage.getItem('chaselights_lang'))?localStorage.getItem('chaselights_lang'):'zh-TW';
    let currentDayFilter=VALID_DAYS.includes(localStorage.getItem('chaselights_day'))?localStorage.getItem('chaselights_day'):'today';
    const storedSortMode=localStorage.getItem('chaselights_sort_mode');
    let currentSortMode=VALID_SORT_MODES.includes(storedSortMode)&&!storedSortMode.startsWith('distance_')?storedSortMode:'region';
    let userLocation=null;
    let sortLocationStatus='';
    let locationRequestSequence=0;
    let showEmptyAdminAreas=false;
    const FILTER_UI_VERSION='3';
    let currentScene='all';
    let currentTheme='all';
    let currentSearch='';
    if(localStorage.getItem('chaselights_filter_ui_version')!==FILTER_UI_VERSION){
      localStorage.setItem('chaselights_scene','all');
      localStorage.setItem('chaselights_theme','all');
      localStorage.setItem('chaselights_filter_ui_version',FILTER_UI_VERSION);
    }
    let currentCategoryKey=localStorage.getItem(`chaselights_category_${currentRegion}`)||'__all__';
    function loadAdminAreas(region){
      try{
        const value=JSON.parse(localStorage.getItem(`chaselights_admin_areas_${region}`)||'[]');
        return new Set(Array.isArray(value)?value:[]);
      }catch{return new Set();}
    }
    let currentAdminAreas=loadAdminAreas(currentRegion);
    let adminPickerHistoryArmed=false;
    let adminPickerScrollY=0;
    let adminPickerPendingRestoreY=null;
    let adminPickerPreviousScrollRestoration=null;
    let currentTempUnit=['C','F'].includes(localStorage.getItem('chaselights_temp_unit'))?localStorage.getItem('chaselights_temp_unit'):'C';
    const FAVORITE_MIGRATION_KEY='chaselights_favs_migration_v2_regions_v1';
    let favorites=JSON.parse(localStorage.getItem('chaselights_favs_v2')||'[]');
    let legacyFavorites=JSON.parse(localStorage.getItem('chaselights_favs')||'[]');
    let favoriteMigrationRegions=JSON.parse(localStorage.getItem(FAVORITE_MIGRATION_KEY)||'[]');
    if(!Array.isArray(favoriteMigrationRegions))favoriteMigrationRegions=[];
    let currentData=null, currentSpots=[];
    let activeModalSpot=null, activeModalSummary=null;
    let activePlaceSpot=null, activePlaceSummary=null;
    let activeLoadController=null, activeLoadSequence=0;
    const memorySummary=new Map(), memoryDetails=new Map();
    const CACHE_NAME='chaselights-v11-weather';
    const MIN_SCHEMA_VERSION=7, MAX_SCHEMA_VERSION=11;
    const schemaSupported=j=>Number.isInteger(j?.schema_version)&&j.schema_version>=MIN_SCHEMA_VERSION&&j.schema_version<=MAX_SCHEMA_VERSION;
    function clearMemoryDetails(region){for(const key of memoryDetails.keys())if(key.startsWith(`${region}:`))memoryDetails.delete(key);}

    const d=()=>i18nDict[currentLang]||i18nDict['zh-TW'];
    // Place names are the one intentional locale exception: when a translated
    // name is unavailable, showing the local/original place name is useful and
    // explicitly allowed. Other user-facing semantic content must not fall
    // back to a different supported language.
    const spotName=s=>s?.name_i18n?.[currentLang]||s?.name_local||s?.name_i18n?.['zh-TW']||s?.spot_id||'—';
    const categoryLabel=k=>(categoryLabels[currentLang]||categoryLabels['zh-TW'])[k]||k;
    const sceneLabel=k=>(sceneLabels[currentLang]||sceneLabels['zh-TW'])[k]||k;
    const themeLabel=k=>(themeLabels[currentLang]||themeLabels['zh-TW'])[k]||k;
    const localeText=values=>{
      const value=values?.[currentLang];
      return typeof value==='string'?value.trim():'';
    };
    function localizedResearchValue(owner,key){
      const translated=localeText(owner?.[`${key}_i18n`]);
      if(translated)return userFacingResearchValue(translated);
      // Canonical research strings are currently zh-TW. They remain available
      // in zh-TW, but are hidden in other locales until an explicit translation
      // exists rather than leaking mixed-language copy.
      return currentLang==='zh-TW'?userFacingResearchValue(owner?.[key]):'';
    }
    function opportunityDisplayName(spot,opportunityId,theme,legacyName){
      const op=(spot?.opportunities||[]).find(item=>item?.opportunity_id===opportunityId)||null;
      const translated=localeText(op?.name_i18n);
      if(translated)return translated;
      if(currentLang==='zh-TW')return op?.name_zh||legacyName||themeLabel(op?.legacy_theme||theme||'mountain_view');
      return themeLabel(op?.legacy_theme||theme||'mountain_view');
    }
    const tempUnitLabel=()=>currentTempUnit==='F'?'°F':'°C';
    function formatTemp(c){
      if(c===null||c===undefined||c===''||Number.isNaN(Number(c)))return '—';
      const n=Number(c);const v=currentTempUnit==='F'?(n*9/5+32):n;return `${Math.round(v*10)/10}${tempUnitLabel()}`;
    }
    function trMessage(key){ const t=currentData?.translations?.messages?.[key]; return localeText(t)||d().status_unavailable; }
    function trFactor(f){ if(!f)return''; const t=currentData?.translations?.factors?.[f.key]; const text=localeText(t); if(!text)return''; return f.value!==null&&f.value!==undefined?text.replace('{v}',f.value):text; }
    function esc(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}

    const OPPORTUNITY_CANDIDATE_STATUS_KEYS=new Set([
      'OPPORTUNITY_MIST_CANDIDATE',
      'OPPORTUNITY_MIST_SUPPORTED',
      'OPPORTUNITY_DIRECTIONAL_MIST_CANDIDATE',
      'OPPORTUNITY_DIRECTIONAL_CLOUD_MATCH',
      'OPPORTUNITY_OROGRAPHIC_CLOUD_PROXY',
      'OPPORTUNITY_SPATIAL_CLOUD_SEA_CANDIDATE'
    ]);
    function opportunityVerdict(metric,subject){
      if(!metric)return {primary:'',detail:''};
      const statusKey=metric.status_key||'';
      const raw=trMessage(statusKey);
      const label=String(subject||themeLabel(metric.theme||'mountain_view')||'').trim();
      const fill=template=>String(template||'').replace('{subject}',label);
      if(statusKey==='OPPORTUNITY_SIMPLE_MATCH'){
        if(metric.score_confidence==='low')return {primary:fill(d().verdict_chance),detail:raw};
        return {primary:fill(d().verdict_suitable),detail:''};
      }
      if(OPPORTUNITY_CANDIDATE_STATUS_KEYS.has(statusKey)){
        return {primary:fill(d().verdict_chance),detail:raw};
      }
      if(statusKey==='OPPORTUNITY_SIMPLE_MISS'){
        return {primary:fill(d().verdict_unfavorable),detail:raw};
      }
      if(statusKey==='OPPORTUNITY_OUTSIDE_TIME_WINDOW'){
        return {primary:fill(d().verdict_outside),detail:raw};
      }
      return {primary:raw,detail:''};
    }

    function updateDiscoveryText(){
      const title=document.getElementById('discovery-title');
      if(title)title.textContent=currentDayFilter==='tomorrow'?d().where_tomorrow:currentDayFilter==='after_tomorrow'?d().where_after:d().where_today;
      const search=document.getElementById('place-search');
      if(search)search.placeholder=d().search_placeholder;
    }
    function applyStaticI18n(){
      document.documentElement.lang=currentLang;
      document.title=d().page_title;
      document.querySelectorAll('[data-i18n]').forEach(el=>{const k=el.dataset.i18n;if(d()[k])el.innerText=d()[k];});
      document.querySelectorAll('[data-i18n-title]').forEach(el=>{const k=el.dataset.i18nTitle;if(d()[k])el.title=d()[k];});
      document.querySelectorAll('[data-i18n-aria-label]').forEach(el=>{const k=el.dataset.i18nAriaLabel;if(d()[k])el.setAttribute('aria-label',d()[k]);});
      document.getElementById('lang-select').value=currentLang; document.getElementById('country-select').value=currentRegion; document.getElementById('temp-unit-select').value=currentTempUnit;
      const sortSelect=document.getElementById('spot-sort');if(sortSelect)sortSelect.value=currentSortMode;
      updateDiscoveryText();renderSortStatus();
    }
    function formatUpdated(iso){ if(!iso)return '—'; const dt=new Date(iso); if(isNaN(dt))return iso; return new Intl.DateTimeFormat(currentLang==='zh-TW'?'zh-TW':currentLang==='ja'?'ja-JP':'en-US',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',timeZoneName:'short'}).format(dt); }
    function updateHeader(){ document.getElementById('update-time').innerText=currentData?`${d().last_updated}${formatUpdated(currentData.updated_at)}`:d().loading; }

    function renderSubNav(){
      const el=document.getElementById('sub-nav'); el.innerHTML='';
      // Legacy country-specific geographic category values collapse to the
      // default all-Places state. Geography now lives in the admin-area picker.
      if(currentCategoryKey!=='__fav__'){
        currentCategoryKey='__all__';
        localStorage.setItem(`chaselights_category_${currentRegion}`,currentCategoryKey);
      }
      const b=document.createElement('button');
      const on=currentCategoryKey==='__fav__';
      b.className=`sub-btn favorite-filter-toggle ${on?'active':''}`;
      b.dataset.key='__fav__';
      b.setAttribute('aria-pressed',on?'true':'false');
      b.innerText=categoryLabel('__fav__');
      b.onclick=e=>{
        e.preventDefault();
        currentCategoryKey=on?'__all__':'__fav__';
        localStorage.setItem(`chaselights_category_${currentRegion}`,currentCategoryKey);
        renderSubNav();
        filterAndRender();
      };
      el.appendChild(b);
    }

    function categoryBaseSpots(){
      const active=currentSpots.filter(s=>s.active_in_catalog!==false);
      if(currentCategoryKey==='__fav__')return active.filter(s=>favorites.includes(s.spot_id));
      return active;
    }

    function availableAdminAreaGroups(){
      return ADMIN_AREA_GROUPS[currentRegion]||[];
    }
    function availableAdminAreas(){
      return availableAdminAreaGroups().flatMap(group=>group.areas);
    }
    function browseAreaGroups(){
      return BROWSE_AREA_GROUPS[currentRegion]||availableAdminAreaGroups();
    }
    function geographicPosition(spot){
      const areas=new Set(spotAdminAreas(spot));
      const groups=browseAreaGroups();
      for(let groupIndex=0;groupIndex<groups.length;groupIndex++){
        const areaIndex=groups[groupIndex].areas.findIndex(area=>areas.has(area));
        if(areaIndex>=0)return {groupKey:groups[groupIndex].key,groupIndex,areaIndex};
      }
      return {groupKey:null,groupIndex:Number.MAX_SAFE_INTEGER,areaIndex:Number.MAX_SAFE_INTEGER};
    }
    function compareGeographic(a,b){
      const ap=geographicPosition(a.spot),bp=geographicPosition(b.spot);
      if(ap.groupIndex!==bp.groupIndex)return ap.groupIndex-bp.groupIndex;
      if(ap.areaIndex!==bp.areaIndex)return ap.areaIndex-bp.areaIndex;
      return spotName(a.spot).localeCompare(spotName(b.spot),currentLang==='ja'?'ja-JP':currentLang==='en'?'en-US':'zh-Hant');
    }
    function persistAdminAreas(){
      localStorage.setItem(`chaselights_admin_areas_${currentRegion}`,JSON.stringify([...currentAdminAreas]));
    }
    const adminPickerMedia=window.matchMedia('(max-width: 640px)');
    const isMobileAdminPicker=()=>adminPickerMedia.matches;
    function lockAdminPickerScroll(scrollYOverride=null){
      if(document.body.classList.contains('admin-picker-open'))return;
      adminPickerScrollY=Number.isFinite(scrollYOverride)
        ? scrollYOverride
        : (window.scrollY||window.pageYOffset||0);
      document.body.style.top=`-${adminPickerScrollY}px`;
      document.body.classList.add('admin-picker-open');
    }
    function unlockAdminPickerScroll(){
      if(!document.body.classList.contains('admin-picker-open'))return;
      document.body.classList.remove('admin-picker-open');
      document.body.style.top='';
      window.scrollTo(0,adminPickerScrollY);
    }
    function restoreAdminPickerScroll(restoreY){
      const apply=()=>{
        if(!document.body.classList.contains('admin-picker-open')){
          window.scrollTo(0,restoreY);
        }
      };
      requestAnimationFrame(apply);
      // Chromium can finish a history traversal after popstate/rAF under
      // mobile emulation. Re-apply briefly so the picker never moves the
      // underlying page after Done/Back closes it.
      setTimeout(apply,50);
      setTimeout(apply,250);
    }
    function openMobileAdminPicker(details,{scrollY=null}={}){
      if(!details||!isMobileAdminPicker())return;
      const alreadyLocked=document.body.classList.contains('admin-picker-open');
      lockAdminPickerScroll(scrollY);
      if(!adminPickerHistoryArmed){
        if('scrollRestoration' in history){
          adminPickerPreviousScrollRestoration=history.scrollRestoration;
          history.scrollRestoration='manual';
        }
        history.pushState({...history.state,chaselightsAdminPicker:true},document.title);
        adminPickerHistoryArmed=true;
      }
      if(!alreadyLocked){
        requestAnimationFrame(()=>{
          const target=details.querySelector('[data-admin-search]')||details.querySelector('[data-admin-close]');
          target?.focus({preventScroll:true});
        });
      }
    }
    function closeMobileAdminPicker({fromHistory=false,restoreFocus=true}={}){
      const host=document.getElementById('admin-filter');
      const details=host?.querySelector('.admin-filter');
      const restoreY=adminPickerScrollY;
      if(details?.open)details.open=false;
      unlockAdminPickerScroll();
      if(adminPickerHistoryArmed){
        if(fromHistory)adminPickerHistoryArmed=false;
        else{
          // history.back() may apply the previous entry's browser-managed
          // scroll position after unlockAdminPickerScroll(). Remember the
          // picker position and re-apply it from popstate.
          adminPickerHistoryArmed=false;
          adminPickerPendingRestoreY=restoreY;
          history.back();
        }
      }
      if(restoreFocus){
        requestAnimationFrame(()=>host?.querySelector('.admin-filter > summary')?.focus({preventScroll:true}));
      }
    }
    function syncAdminGroupSummaryState(group){
      const summary=group?.querySelector(':scope > .admin-area-group-title');
      if(summary)summary.setAttribute('aria-expanded',group.open?'true':'false');
    }
    function renderAdminFilter(){
      const host=document.getElementById('admin-filter');if(!host)return;
      const previousDetails=host.querySelector('.admin-filter');
      const mobile=isMobileAdminPicker();
      // Preserve an open picker across mobile rerenders only after the mobile
      // sheet has actually acquired its scroll lock. A desktop dropdown that
      // happened to be open must not silently become an already-open sheet
      // when crossing the responsive breakpoint.
      const wasOpen=!!previousDetails?.open&&(!mobile||document.body.classList.contains('admin-picker-open'));
      const previousSearch=host.querySelector('[data-admin-search]')?.value||'';
      const previousOpenGroups=new Set(
        [...host.querySelectorAll('[data-admin-group][open]')]
          .map(group=>group.dataset.adminGroupKey)
          .filter(Boolean)
      );
      const groups=availableAdminAreaGroups();
      const areas=groups.flatMap(group=>group.areas);
      const available=new Set(areas);
      const next=new Set([...currentAdminAreas].filter(a=>available.has(a)));
      if(next.size!==currentAdminAreas.size){currentAdminAreas=next;persistAdminAreas();}
      if(!areas.length){
        host.hidden=true;host.innerHTML='';closeMobileAdminPicker({restoreFocus:false});return;
      }

      // Counts and disabled state always use all active Places in the country,
      // not a transient Favorites filter. This keeps the picker stable.
      const allActive=currentSpots.filter(s=>s.active_in_catalog!==false);
      const counts={};
      areas.forEach(a=>counts[a]=allActive.filter(s=>spotAdminAreas(s).includes(a)).length);

      const summary=currentAdminAreas.size?d().admin_area_selected.replace('{n}',currentAdminAreas.size):d().admin_area_all;
      const showSearch=areas.length>24||mobile;
      const visibleGroups=groups.map(group=>({
        ...group,
        areas:group.areas.filter(a=>showEmptyAdminAreas||counts[a]>0||currentAdminAreas.has(a))
      })).filter(group=>group.areas.length);
      const hiddenEmptyCount=areas.filter(a=>counts[a]===0).length;
      const emptyToggle=hiddenEmptyCount
        ? `<button type="button" class="admin-area-empty-toggle" data-admin-empty-toggle aria-pressed="${showEmptyAdminAreas?'true':'false'}">${esc(showEmptyAdminAreas?d().admin_area_hide_empty:d().admin_area_show_empty)}</button>`
        : '';
      const groupHtml=visibleGroups.map((group,index)=>{
        const buttons=group.areas.map(a=>{
          const disabled=counts[a]===0&&!currentAdminAreas.has(a);
          const searchText=`${a} ${adminAreaLabel(a)}`.toLocaleLowerCase();
          const active=currentAdminAreas.has(a);
          return `<button type="button" class="admin-area-btn ${active?'active':''}" data-admin-area="${esc(a)}" data-admin-search-text="${esc(searchText)}" aria-pressed="${active?'true':'false'}" ${disabled?'disabled aria-disabled="true"':''}><span class="admin-area-count">${counts[a]}</span><span class="admin-area-name"><i class="admin-area-check" aria-hidden="true">✓</i>${esc(adminAreaLabel(a))}</span></button>`;
        }).join('');
        const showGroupTitle=groups.length>1;
        if(!showGroupTitle)return `<section class="admin-area-group admin-area-group-flat" data-admin-group data-admin-group-key="${esc(group.key)}"><div class="admin-filter-grid">${buttons}</div></section>`;
        const containsSelected=group.areas.some(a=>currentAdminAreas.has(a));
        const expanded=!mobile||previousOpenGroups.has(group.key)||containsSelected||(!currentAdminAreas.size&&!previousOpenGroups.size&&index===0);
        return `<details class="admin-area-group" data-admin-group data-admin-group-key="${esc(group.key)}" ${expanded?'open':''}><summary class="admin-area-group-title" aria-expanded="${expanded?'true':'false'}"><span>${esc(adminAreaGroupLabel(group.key))}</span><span class="admin-area-group-chevron" aria-hidden="true">⌄</span></summary><div class="admin-filter-grid">${buttons}</div></details>`;
      }).join('');

      host.hidden=false;
      host.innerHTML=`<details class="admin-filter"${wasOpen?' open':''}><summary aria-haspopup="dialog" aria-expanded="${wasOpen?'true':'false'}">📍 ${esc(summary)}</summary><div class="admin-picker-backdrop" data-admin-backdrop></div><div class="admin-filter-menu" role="${mobile?'dialog':'group'}" ${mobile?'aria-modal="true"':''} aria-labelledby="admin-filter-title"><div class="admin-mobile-handle" aria-hidden="true"></div><div class="admin-filter-head"><span id="admin-filter-title">${esc(adminAreaKindLabel())}</span><div class="admin-filter-head-actions"><button type="button" class="admin-clear-btn" data-admin-clear>${esc(d().admin_area_clear)}</button><button type="button" class="admin-close-btn" data-admin-close aria-label="${esc(d().admin_area_close)}">×</button></div></div>${showSearch?`<input class="admin-area-search" type="search" autocomplete="off" data-admin-search placeholder="${esc(adminAreaSearchPlaceholder())}" aria-label="${esc(adminAreaSearchPlaceholder())}">`:''}${emptyToggle}<div class="admin-area-groups">${groupHtml}</div><div class="admin-area-empty" data-admin-empty hidden>${esc(d().admin_area_no_match)}</div><div class="admin-filter-footer"><button type="button" class="admin-footer-clear" data-admin-clear>${esc(d().admin_area_clear)}</button><button type="button" class="admin-done-btn" data-admin-done>${esc(d().admin_area_done)}</button></div></div></details>`;

      const details=host.querySelector('.admin-filter');
      const summaryButton=details.querySelector(':scope > summary');
      const close=()=>closeMobileAdminPicker();
      summaryButton.addEventListener('click',e=>{
        if(!isMobileAdminPicker())return;
        e.preventDefault();
        if(details.open){
          close();
          return;
        }
        // Capture before opening <details>. Chromium can reflow the page as
        // soon as details.open flips, changing window.scrollY before the body
        // lock is applied. Preserve the user's actual pre-open position.
        const preOpenScrollY=window.scrollY||window.pageYOffset||0;
        // Lock before toggling <details>; opening the element itself can
        // synchronously change layout/scroll position in Chromium.
        openMobileAdminPicker(details,{scrollY:preOpenScrollY});
        details.open=true;
        summaryButton.setAttribute('aria-expanded','true');
      });
      details.addEventListener('toggle',()=>{
        summaryButton.setAttribute('aria-expanded',details.open?'true':'false');
        if(!isMobileAdminPicker())return;
        if(details.open)openMobileAdminPicker(details);
        else if(document.body.classList.contains('admin-picker-open'))closeMobileAdminPicker();
      });
      host.querySelector('[data-admin-backdrop]')?.addEventListener('click',e=>{e.preventDefault();close();});
      host.querySelector('[data-admin-close]')?.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();close();});
      host.querySelector('[data-admin-done]')?.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();close();});
      host.querySelector('[data-admin-empty-toggle]')?.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();showEmptyAdminAreas=!showEmptyAdminAreas;renderAdminFilter();});
      host.querySelectorAll('[data-admin-clear]').forEach(button=>button.onclick=e=>{
        e.preventDefault();e.stopPropagation();currentAdminAreas.clear();persistAdminAreas();filterAndRender();
      });
      host.querySelectorAll('[data-admin-area]:not([disabled])').forEach(button=>button.onclick=e=>{
        e.preventDefault();e.stopPropagation();
        const area=button.dataset.adminArea;
        if(currentAdminAreas.has(area))currentAdminAreas.delete(area);else currentAdminAreas.add(area);
        persistAdminAreas();filterAndRender();
      });

      host.querySelectorAll('details[data-admin-group]').forEach(group=>{
        const groupSummary=group.querySelector(':scope > summary');
        groupSummary.tabIndex=mobile?0:-1;
        group.addEventListener('toggle',()=>syncAdminGroupSummaryState(group));
        syncAdminGroupSummaryState(group);
      });

      const search=host.querySelector('[data-admin-search]');
      let searchWasActive=false;
      const applyAdminSearch=()=>{
        if(!search)return;
        const q=String(search.value||'').trim().toLocaleLowerCase();
        if(q&&!searchWasActive){
          host.querySelectorAll('details[data-admin-group]').forEach(group=>group.dataset.adminPreSearchOpen=group.open?'1':'0');
        }
        let visible=0;
        host.querySelectorAll('[data-admin-group]').forEach(group=>{
          let groupVisible=0;
          group.querySelectorAll('[data-admin-area]').forEach(button=>{
            const match=!q||(button.dataset.adminSearchText||'').includes(q);
            button.hidden=!match;
            if(match){visible++;groupVisible++;}
          });
          group.hidden=groupVisible===0;
          if(group.tagName==='DETAILS'){
            if(q&&groupVisible)group.open=true;
            else if(!q&&searchWasActive)group.open=group.dataset.adminPreSearchOpen==='1';
            syncAdminGroupSummaryState(group);
          }
        });
        const empty=host.querySelector('[data-admin-empty]');
        if(empty)empty.hidden=visible!==0;
        searchWasActive=!!q;
      };
      if(search){
        search.value=previousSearch;
        search.addEventListener('input',applyAdminSearch);
        search.addEventListener('click',e=>e.stopPropagation());
        applyAdminSearch();
      }

      if(mobile&&details.open)openMobileAdminPicker(details);
      if(!mobile&&document.body.classList.contains('admin-picker-open')){
        closeMobileAdminPicker({restoreFocus:false});
      }
    }

    adminPickerMedia.addEventListener('change',event=>{
      if(!event.matches&&document.body.classList.contains('admin-picker-open')){
        closeMobileAdminPicker({restoreFocus:false});
      }
      renderAdminFilter();
    });

    window.addEventListener('popstate',()=>{
      const restoreHistoryScrollMode=()=>{
        if(
          'scrollRestoration' in history &&
          adminPickerPreviousScrollRestoration!==null
        ){
          history.scrollRestoration=adminPickerPreviousScrollRestoration;
          adminPickerPreviousScrollRestoration=null;
        }
      };
      if(Number.isFinite(adminPickerPendingRestoreY)){
        const restoreY=adminPickerPendingRestoreY;
        adminPickerPendingRestoreY=null;
        restoreAdminPickerScroll(restoreY);
        setTimeout(restoreHistoryScrollMode,260);
        return;
      }
      if(!adminPickerHistoryArmed){
        restoreHistoryScrollMode();
        return;
      }
      const restoreY=adminPickerScrollY;
      adminPickerHistoryArmed=false;
      const details=document.querySelector('#admin-filter .admin-filter');
      if(details?.open)details.open=false;
      unlockAdminPickerScroll();
      restoreAdminPickerScroll(restoreY);
      setTimeout(restoreHistoryScrollMode,260);
      requestAnimationFrame(()=>{
        document.querySelector('#admin-filter .admin-filter > summary')?.focus({preventScroll:true});
      });
    });
    document.addEventListener('keydown',e=>{
      if(e.key==='Escape'&&document.body.classList.contains('admin-picker-open')){
        e.preventDefault();
        closeMobileAdminPicker();
      }
    });

    function setFilterPressed(button,on){
      button.classList.toggle('active',on);
      button.setAttribute('aria-pressed',on?'true':'false');
      button.style.background=on?'#38bdf8':'';
      button.style.color=on?'#0f172a':'';
      button.style.borderColor=on?'#38bdf8':'';
      button.style.fontWeight=on?'700':'';
    }
    function syncFilterHighlights(){
      document.querySelectorAll('#scene-nav .tag-btn').forEach(b=>setFilterPressed(b,b.dataset.key===currentScene));
      document.querySelectorAll('#theme-nav .tag-btn').forEach(b=>setFilterPressed(b,b.dataset.key===currentTheme));
    }
    function renderSceneNav(){}
    function renderThemeNav(){}
    function normalizeFilterCombination(){}
    function renderSortStatus(){
      const el=document.getElementById('sort-status');if(!el)return;
      const key=sortLocationStatus==='requesting'?'sort_location_requesting':sortLocationStatus==='using'?'sort_location_using_current':sortLocationStatus==='unavailable'?'sort_location_unavailable':'';
      el.textContent=key?d()[key]:'';
    }
    function updateFilterResultSummary(count){
      const el=document.getElementById('filter-result-summary');if(!el)return;
      const sortKeys={
        region:'result_count_region',
        score_desc:'result_count_score_desc',
        score_asc:'result_count_score_asc',
        distance_near:'result_count_distance_near',
        distance_far:'result_count_distance_far'
      };
      const template=currentSearch?d().search_result:(d()[sortKeys[currentSortMode]]||d().result_count);
      el.textContent=template.replace('{n}',count);
    }
    function setPlaceSearch(value){
      currentSearch=String(value||'').trim().toLocaleLowerCase();
      filterAndRender();
    }
    function setSortMode(mode){
      if(!VALID_SORT_MODES.includes(mode))mode='region';
      const select=document.getElementById('spot-sort');
      const requestId=++locationRequestSequence;
      if(mode.startsWith('distance_')&&!userLocation){
        if(!navigator.geolocation){
          currentSortMode='region';localStorage.setItem('chaselights_sort_mode','region');
          if(select)select.value='region';sortLocationStatus='unavailable';renderSortStatus();filterAndRender();return;
        }
        sortLocationStatus='requesting';renderSortStatus();
        navigator.geolocation.getCurrentPosition(
          position=>{
            if(requestId!==locationRequestSequence)return;
            userLocation={lat:Number(position.coords.latitude),lon:Number(position.coords.longitude)};
            currentSortMode=mode;if(select)select.value=mode;sortLocationStatus='using';renderSortStatus();filterAndRender();
          },
          ()=>{
            if(requestId!==locationRequestSequence)return;
            currentSortMode='region';localStorage.setItem('chaselights_sort_mode','region');
            if(select)select.value='region';sortLocationStatus='unavailable';renderSortStatus();filterAndRender();
          },
          {enableHighAccuracy:false,timeout:10000,maximumAge:300000}
        );
        return;
      }
      currentSortMode=mode;
      if(!mode.startsWith('distance_'))localStorage.setItem('chaselights_sort_mode',mode);
      sortLocationStatus=mode.startsWith('distance_')?'using':'';
      if(select)select.value=mode;
      renderSortStatus();filterAndRender();
    }
    function syncDayButtons(){const map={today:0,tomorrow:1,after_tomorrow:2};document.querySelectorAll('.day-btn').forEach((b,i)=>b.classList.toggle('active',i===map[currentDayFilter]));}
    function switchDay(k){currentDayFilter=k;localStorage.setItem('chaselights_day',k);syncDayButtons();updateDiscoveryText();filterAndRender();}
    function switchLanguage(k){
      if(!VALID_LANGS.includes(k))return;
      currentLang=k;localStorage.setItem('chaselights_lang',k);applyStaticI18n();renderSubNav();syncDayButtons();updateHeader();filterAndRender();
      if(activePlaceSpot&&document.getElementById('place-modal-overlay').style.display==='flex')openPlaceModal(activePlaceSpot,activePlaceSummary);
      if(activeModalSpot&&document.getElementById('modal-overlay').style.display==='flex')renderWeatherModal(activeModalSpot,activeModalSummary);
    }
    function switchTempUnit(k){if(!['C','F'].includes(k))return;currentTempUnit=k;localStorage.setItem('chaselights_temp_unit',k);document.getElementById('temp-unit-select').value=k;filterAndRender();if(activeModalSpot&&document.getElementById('modal-overlay').style.display==='flex')renderWeatherModal(activeModalSpot,activeModalSummary);}
    function switchRegion(k){if(!VALID_REGIONS.includes(k))k='tw';currentRegion=k;localStorage.setItem('chaselights_region',k);currentCategoryKey=localStorage.getItem(`chaselights_category_${k}`)||'__all__';currentAdminAreas=loadAdminAreas(k);showEmptyAdminAreas=false;document.getElementById('country-select').value=k;loadData(k);}
    function persistLegacyFavorites(){
      if(legacyFavorites.length)localStorage.setItem('chaselights_favs',JSON.stringify(legacyFavorites));
      else{
        localStorage.removeItem('chaselights_favs');
        favoriteMigrationRegions=[];
        localStorage.removeItem(FAVORITE_MIGRATION_KEY);
      }
    }
    function persistFavoriteMigrationRegions(){
      localStorage.setItem(FAVORITE_MIGRATION_KEY,JSON.stringify(favoriteMigrationRegions));
    }
    function toggleFavorite(id,event){
      event?.stopPropagation();
      const removing=favorites.includes(id);
      favorites=removing?favorites.filter(x=>x!==id):[...favorites,id];
      localStorage.setItem('chaselights_favs_v2',JSON.stringify(favorites));
      if(removing){
        const spot=currentSpots.find(s=>s.spot_id===id);
        const names=new Set(Object.values(spot?.name_i18n||{}).filter(Boolean));
        if(spot?.name_local)names.add(spot.name_local);
        legacyFavorites=legacyFavorites.filter(name=>!names.has(name));
        persistLegacyFavorites();
      }
      filterAndRender();
    }

    async function cacheMatch(url){try{if(!('caches'in window))return null;const c=await caches.open(CACHE_NAME);const r=await c.match(url);if(!r)return null;const j=await r.json();return schemaSupported(j)?j:null;}catch{return null;}}
    async function fetchAndCache(url,signal,cacheKey=url){const opts={cache:'no-cache'};if(signal)opts.signal=signal;const r=await fetch(url,opts);if(!r.ok)throw new Error(`HTTP ${r.status}`);const clone=r.clone();try{if('caches'in window){const c=await caches.open(CACHE_NAME);await c.put(cacheKey,clone);}}catch{}const j=await r.json();if(!schemaSupported(j))throw new Error(`Schema mismatch: expected ${MIN_SCHEMA_VERSION}-${MAX_SCHEMA_VERSION}, got ${j?.schema_version??'missing'}`);return j;}
    function applyData(data,region,seq){if(seq!==activeLoadSequence||region!==currentRegion||data.region!==region)return false;const prev=memorySummary.get(region);if(prev?.updated_at&&data?.updated_at&&prev.updated_at!==data.updated_at)clearMemoryDetails(region);currentData=data;currentSpots=data.spots||[];memorySummary.set(region,data);document.getElementById('loading').style.display='none';migrateFavorites(region);renderSubNav();syncDayButtons();updateHeader();filterAndRender();return true;}
    function migrateFavorites(region){
      if(!legacyFavorites.length||favoriteMigrationRegions.includes(region))return;
      const migratedNames=new Set();
      currentSpots.forEach(s=>{
        const names=[...Object.values(s.name_i18n||{}),s.name_local].filter(Boolean);
        if(names.some(n=>legacyFavorites.includes(n))){
          if(!favorites.includes(s.spot_id))favorites.push(s.spot_id);
          names.forEach(n=>migratedNames.add(n));
        }
      });
      if(migratedNames.size)localStorage.setItem('chaselights_favs_v2',JSON.stringify(favorites));
      legacyFavorites=legacyFavorites.filter(name=>!migratedNames.has(name));
      favoriteMigrationRegions=[...new Set([...favoriteMigrationRegions,region])];
      persistFavoriteMigrationRegions();
      persistLegacyFavorites();
    }
    async function refreshSummary(region,url,seq,controller,silent=false){try{const fresh=await fetchAndCache(url,controller.signal);if(applyData(fresh,region,seq))memorySummary.set(region,fresh);}catch(e){if(e?.name==='AbortError'||seq!==activeLoadSequence)return;if(!silent){const l=document.getElementById('loading');l.style.display='block';l.innerText=`⚠️ ${d().load_error}`;}}}
    async function loadData(region){
      const seq=++activeLoadSequence;if(activeLoadController)activeLoadController.abort();activeLoadController=new AbortController();
      const container=document.getElementById('spots-container'), loading=document.getElementById('loading');container.innerHTML='';currentSpots=[];currentData=null;renderSubNav();loading.innerText=d().loading;loading.style.display='block';updateHeader();
      const url=`./${region}_weather.json`;
      if(memorySummary.has(region)){applyData(memorySummary.get(region),region,seq);refreshSummary(region,url,seq,activeLoadController,true);return;}
      const cached=await cacheMatch(url);if(seq!==activeLoadSequence)return;if(cached){applyData(cached,region,seq);refreshSummary(region,url,seq,activeLoadController,true);return;}
      await refreshSummary(region,url,seq,activeLoadController,false);
    }

    function selectedDayOffset(){return currentDayFilter==='tomorrow'?1:currentDayFilter==='after_tomorrow'?2:0;}
    function localDateString(timeZone,offsetDays=0){
      const parts=new Intl.DateTimeFormat('en-CA',{timeZone:timeZone||'UTC',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
      const values=Object.fromEntries(parts.map(p=>[p.type,p.value]));
      const base=new Date(Date.UTC(Number(values.year),Number(values.month)-1,Number(values.day)+offsetDays));
      return `${base.getUTCFullYear()}-${String(base.getUTCMonth()+1).padStart(2,'0')}-${String(base.getUTCDate()).padStart(2,'0')}`;
    }
    function selectedDateForSpot(spot){return localDateString(spot?.timezone||'UTC',selectedDayOffset());}
    function currentDayForSpot(spot){const target=selectedDateForSpot(spot);return (spot.daily||[]).find(day=>day?.date===target)||null;}
    function getMetric(spot){const day=currentDayForSpot(spot);if(!day)return null;return day.all||null;}
    function fmtWindow(m){if(!m)return'—';const a=m.window_start,b=m.window_end,tz=m.timezone_abbr||'';if(!a||!b)return m.best_time||'—';const [ad,at]=a.split(' '),[bd,bt]=b.split(' ');const ad2=ad?.slice(5).replace('-', '/'),bd2=bd?.slice(5).replace('-', '/');return ad===bd?`${ad2} ${at}–${bt} ${tz}`:`${ad2} ${at} → ${bd2} ${bt} ${tz}`;}
    function confidenceLabel(value){const key=String(value||'').toLowerCase();return key==='high'?d().confidence_high:key==='medium'?d().confidence_medium:key==='low'?d().confidence_low:'—';}
    function astroText(m,theme){if(!m?.astronomy_valid)return'';const parts=[];if(['sunrise','sunset','sky_glow','blue_hour'].includes(theme)&&m.sun_elevation!=null)parts.push(`☀️ ${Math.round(m.sun_azimuth)}° / ${Math.round(m.sun_elevation)}°`);if(theme==='milky_way'){if(m.moon_illumination!=null)parts.push(`🌙 ${Math.round(m.moon_illumination)}%`);if(m.galactic_core_elevation!=null)parts.push(`🌌 ${Math.round(m.galactic_core_azimuth)}° / ${Math.round(m.galactic_core_elevation)}°`);}if(theme==='aurora'&&m.kp!=null)parts.push(`🌌 Kp ${m.kp}`);return parts.join(' · ');}
    function darkSkyText(spot,theme){if(!['milky_way','aurora'].includes(theme)||!spot?.bortle_class)return'';const b=spot.bortle_class;const qual=b<=2?'★★★★★':b<=4?'★★★★☆':b<=5?'★★★☆☆':b<=7?'★★☆☆☆':'★☆☆☆☆';return `🌌 ≈Bortle ${b} · ${qual}`;}

    function radarUrl(){if(currentRegion==='jp')return'https://www.jma.go.jp/bosai/nowc/';if(currentRegion==='us')return'https://radar.weather.gov/';return'https://www.cwa.gov.tw/V8/C/W/OBS_Radar.html';}

    function navigationTargetNote(target){
      const notes=target?.note_i18n||{};
      return localeText(notes);
    }

    function navigationToolHtml(spot){
      const target=spot?.navigation_target||null;
      const status=target?.status||'needs_review';
      const lat=Number(target?.lat),lon=Number(target?.lon);
      const hasCoords=Number.isFinite(lat)&&Number.isFinite(lon)&&lat>=-90&&lat<=90&&lon>=-180&&lon<=180;
      const note=navigationTargetNote(target);

      if(status==='verified'&&hasCoords){
        const url=`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(`${lat},${lon}`)}`;
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-navigation-mode="verified" title="${esc(note)}">${d().nav_link}</a>`;
      }
      if(status==='provisional_camera_anchor'&&hasCoords){
        const url=`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${lat},${lon}`)}`;
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="tool-link" data-navigation-mode="provisional-map-pin" title="${esc(note)}">${d().map_link}</a>`;
      }
      return `<span class="tool-link disabled" data-navigation-mode="${esc(status)}" title="${esc(note)}">${d().nav_pending}</span>`;
    }

    function createSpotCard(spot,metric){
      const card=document.createElement('div');card.className='card';card.tabIndex=0;card.setAttribute('role','button');card.onclick=()=>openPlaceModal(spot,metric);card.onkeydown=e=>{if(e.target.closest('a,button,input,select,summary'))return;if(e.key==='Enter'||e.key===' '){e.preventDefault();openPlaceModal(spot,metric);}};
      const noViable=!!metric.no_viable_opportunity;const researchPending=!!metric.research_pending||!spot.opportunities?.length;const hasScore=metric.score!==null&&metric.score!==undefined&&!researchPending&&!noViable;const score=hasScore?Number(metric.score):null;const scoreClass=!hasScore?'score-low':score>=92?'score-gold':score>=80?'score-high':score>=65?'score-mid':'score-low';const flame=hasScore&&score>=92?'🔥 ':'';const scoreText=hasScore?`${flame}${score}`:'—';const scoreLabel=!hasScore?'':score>=92?d().score_excellent:score>=80?d().score_good:score>=65?d().score_fair:d().score_low_label;
      const fav=favorites.includes(spot.spot_id);const scenes=spot.scenes||[];const visibleScenes=scenes.slice(0,4);const scenePills=visibleScenes.map(x=>`<span class="scene-pill">${sceneLabel(x)}</span>`).join('');const sceneMore=scenes.length>2?`<span class="scene-pill scene-more">+${scenes.length-2}</span>`:'';
      const theme=metric.theme||'mountain_view',opportunityName=researchPending?d().research_pending_card:(noViable?d().no_viable_card:opportunityDisplayName(spot,metric.opportunity_id,theme,metric.opportunity_name));const verdict=(researchPending||noViable)?{primary:'',detail:''}:opportunityVerdict(metric,opportunityName);const status=verdict.primary,indicator=(researchPending||noViable)?'':trMessage(metric.indicator_key);const astro=(researchPending||noViable)?'':astroText(metric,theme);const darkSky=(researchPending||noViable)?'':darkSkyText(spot,theme);const navTool=navigationToolHtml(spot);const access=localeText(spot.access_note_i18n);const showIndicator=indicator&&indicator!==status;const factors=(researchPending||noViable)?[]:(metric.factors||[]);const factorHtml=factors.map(f=>{const text=trFactor(f);return text?`<span class="factor-pill ${f.type==='minus'?'factor-minus':'factor-plus'}">${f.type==='minus'?'−':'＋'} ${text}</span>`:'';}).filter(Boolean).join('');const factorMore=factors.length>2?`<span class="factor-pill factor-more">+${factors.length-2}</span>`:'';
      const reasonHtml=(researchPending||noViable)?'':`${showIndicator?`<div><span class="indicator-pill">${indicator}</span></div>`:''}${factorHtml?`<div class="factor-row card-factor-row">${factorHtml}${factorMore}</div>`:''}`;
      const distance=distanceToSpotKm(spot);const distanceChip=currentSortMode.startsWith('distance_')&&distance!==null?`<span class="metric-chip">📍 ${distance<10?distance.toFixed(1):Math.round(distance)} km</span>`:'';
      const compactMetrics=(researchPending||noViable)?`<span class="metric-chip">🌡 ${formatTemp(metric.temp)}</span>`:[
        metric.cloud_base_agl!=null?`<span class="metric-chip">☁️ ${metric.cloud_base_agl}m</span>`:'',
        `<span class="metric-chip">🌡 ${formatTemp(metric.temp)}</span>`
      ].filter(Boolean).join('');
      card.innerHTML=`<div><div class="card-header"><div class="spot-title-group"><span class="spot-name"></span><div class="spot-local-name"></div><div style="margin-top:4px"><span class="category-tag">${esc(spotAdminAreas(spot).map(adminAreaLabel).join(" · ")||categoryLabel(spot.category))}</span></div></div><div class="card-header-actions"><span class="score-badge ${scoreClass}">${scoreText}${scoreLabel?`<span class="score-label">${esc(scoreLabel)}</span>`:''}</span><button class="fav-btn ${fav?'active':''}" data-fav aria-label="${esc(d().favorite_label)}">★</button></div></div><div class="tags-wrapper">${scenePills}${sceneMore}</div><div class="shooting-summary"><div class="theme-winner">${(researchPending||noViable)?`📷 ${esc(opportunityName)}`:d().best_theme+esc(opportunityName)}</div>${(researchPending||noViable)?'':`<div class="best-window-row">${d().best_window}<b>${fmtWindow(metric)}</b></div>`}</div>${reasonHtml?`<div class="recommendation-reasons">${reasonHtml}</div>`:''}<div class="card-secondary-meta"><div class="card-quick-meta"><span class="card-timezone">🕒 ${(spot.timezone==='Asia/Taipei'?'UTC+8':(metric.timezone_abbr||spot.timezone_abbr||spot.timezone||'—'))}</span><span class="card-metric-chips">${compactMetrics}${distanceChip}</span></div>${(researchPending||noViable)?'':`<div class="info-row forecast-status-row card-meta-row">${d().forecast_status}${status}</div>`}${astro?`<div class="info-row card-meta-row card-meta-astro">${astro}</div>`:''}${darkSky?`<div class="info-row card-meta-row card-meta-dark">${darkSky}</div>`:''}${access?`<div class="info-row access-note card-meta-row card-meta-access" title="${esc(access)}">⏰ ${esc(access)}</div>`:''}</div></div><div class="card-footer-tools" data-tools><div></div><div><a href="#" class="tool-link" data-weather>${d().weather_link}</a>${navTool}<a href="${radarUrl()}" target="_blank" rel="noopener noreferrer" class="tool-link">${d().radar_link}</a></div></div>`;
      card.querySelector('.spot-name').textContent=spotName(spot);const local=card.querySelector('.spot-local-name');const showLocal=!(currentRegion==='tw'&&currentLang==='zh-TW');local.textContent=showLocal&&spot.name_local&&spot.name_local!==spotName(spot)?spot.name_local:'';card.querySelector('[data-fav]').onclick=e=>toggleFavorite(spot.spot_id,e);card.querySelector('[data-tools]').onclick=e=>e.stopPropagation();card.querySelector('[data-weather]').onclick=e=>{e.preventDefault();e.stopPropagation();openWeatherModal(spot,metric);};
      return card;
    }

    function scoreSortValue(metric){
      const score=Number(metric?.score);
      return Number.isFinite(score)?score:null;
    }
    function distanceToSpotKm(spot){
      if(!userLocation)return null;
      const lat=Number(spot?.lat),lon=Number(spot?.lon);
      if(!Number.isFinite(lat)||!Number.isFinite(lon))return null;
      const toRad=value=>value*Math.PI/180;
      const dLat=toRad(lat-userLocation.lat),dLon=toRad(lon-userLocation.lon);
      const a=Math.sin(dLat/2)**2+Math.cos(toRad(userLocation.lat))*Math.cos(toRad(lat))*Math.sin(dLon/2)**2;
      return 6371*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
    }
    function sortRows(rows){
      rows.forEach(row=>row.distance=distanceToSpotKm(row.spot));
      rows.sort((a,b)=>{
        if(currentSortMode==='region')return compareGeographic(a,b);
        if(currentSortMode==='score_desc'||currentSortMode==='score_asc'){
          const av=scoreSortValue(a.metric),bv=scoreSortValue(b.metric);
          if(av===null&&bv!==null)return 1;
          if(bv===null&&av!==null)return -1;
          if(av!==null&&bv!==null&&av!==bv)return currentSortMode==='score_desc'?bv-av:av-bv;
          return compareGeographic(a,b);
        }
        if(currentSortMode==='distance_near'||currentSortMode==='distance_far'){
          const av=a.distance,bv=b.distance;
          if(av===null&&bv!==null)return 1;
          if(bv===null&&av!==null)return -1;
          if(av!==null&&bv!==null&&av!==bv)return currentSortMode==='distance_near'?av-bv:bv-av;
          return compareGeographic(a,b);
        }
        return compareGeographic(a,b);
      });
      return rows;
    }
    function appendSpotRows(target,rows){
      if(currentSortMode!=='region'){
        rows.forEach(({spot,metric})=>target.appendChild(createSpotCard(spot,metric)));
        return;
      }
      const grouped=new Map(),ungrouped=[];
      rows.forEach(row=>{
        const key=geographicPosition(row.spot).groupKey;
        if(!key){ungrouped.push(row);return;}
        if(!grouped.has(key))grouped.set(key,[]);
        grouped.get(key).push(row);
      });
      browseAreaGroups().forEach(group=>{
        const groupRows=grouped.get(group.key)||[];
        if(!groupRows.length)return;
        const section=document.createElement('section');section.className='spot-region-section';section.dataset.regionGroup=group.key;
        const heading=document.createElement('div');heading.className='spot-region-heading';
        heading.innerHTML=`<span>${esc(adminAreaGroupLabel(group.key))}</span><span class="spot-region-count">${esc(d().region_group_count.replace('{n}',groupRows.length))}</span>`;
        const grid=document.createElement('div');grid.className='spot-region-grid';
        groupRows.forEach(({spot,metric})=>grid.appendChild(createSpotCard(spot,metric)));
        section.append(heading,grid);target.appendChild(section);
      });
      ungrouped.forEach(({spot,metric})=>target.appendChild(createSpotCard(spot,metric)));
    }

    function filterAndRender(){
      syncFilterHighlights();
      const container=document.getElementById('spots-container');container.innerHTML='';if(!currentData)return;
      renderAdminFilter();
      let filtered=categoryBaseSpots();
      if(currentAdminAreas.size){
        filtered=filtered.filter(s=>spotAdminAreas(s).some(a=>currentAdminAreas.has(a)));
      }
      if(currentSearch){
        filtered=filtered.filter(s=>{
          const haystack=[...(Object.values(s.name_i18n||{})),s.name_local,s.map_query,s.category,...spotAdminAreas(s),...spotAdminAreas(s).map(adminAreaLabel)].filter(Boolean).join(' ').toLocaleLowerCase();
          return haystack.includes(currentSearch);
        });
      }
      const rows=[];for(const spot of filtered){const metric=getMetric(spot);if(metric)rows.push({spot,metric,distance:null});}
      sortRows(rows);
      updateFilterResultSummary(rows.length);
      if(!rows.length){container.innerHTML=`<div class="empty-state">📭 ${esc(d().no_spots)}</div>`;return;}

      const viableRows=rows.filter(({metric})=>!metric.no_viable_opportunity);
      const deferredRows=rows.filter(({metric})=>!!metric.no_viable_opportunity);
      appendSpotRows(container,viableRows);

      if(deferredRows.length){
        const details=document.createElement('details');details.className='deferred-group';
        const summary=document.createElement('summary');summary.textContent=d().no_viable_group.replace('{n}',deferredRows.length);
        const grid=document.createElement('div');grid.className='deferred-grid';
        appendSpotRows(grid,deferredRows);
        details.append(summary,grid);container.appendChild(details);
      }
    }

    function opportunityScoreClass(score){return score>=80?'high':score>=65?'mid':'low';}
    function userFacingResearchValue(value){
      const text=String(value||'').trim();
      if(!text)return '';
      return /(待證據|尚無足夠證據|待驗證|待氣候驗證|研究中|needs[_ -]?research|provisional|pending|unknown)/i.test(text)?'':text;
    }
    function openPlaceModal(spot,summaryMetric){
      activePlaceSpot=spot;activePlaceSummary=summaryMetric;
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
      const hasSelectedDateEvaluation=op=>{
        const m=dayScores[op.opportunity_id];
        return !!m&&!m.research_pending&&!m.no_viable_opportunity;
      };
      const selectedDateOpportunities=rankedOpportunities.filter(hasSelectedDateEvaluation);
      const selectedDateIds=new Set(selectedDateOpportunities.map(op=>op.opportunity_id));
      const guideOnlyOpportunities=rankedOpportunities.filter(op=>!selectedDateIds.has(op.opportunity_id));
      const renderOpportunityCard=(op,m,guideOnly=false)=>{
        const score=guideOnly?null:m?.score;
        const viewpoints=(op.viewpoints||[]).map(v=>localizedResearchValue(v,'name')).filter(Boolean);
        let suppressedLocalizedGuide=false;
        const variants=(op.condition_variants||[]).map(v=>{
          const rows=[];
          const variantName=localizedResearchValue(v,'variant_name');
          const required=localizedResearchValue(v,'required_conditions');
          const boosters=localizedResearchValue(v,'boosters');
          const penalties=localizedResearchValue(v,'penalties');
          if(required)rows.push(`<div><span class="research-label">${esc(d().guide_required)}：</span>${esc(required)}</div>`);
          if(boosters)rows.push(`<div><span class="research-label">${esc(d().guide_boosters)}：</span>${esc(boosters)}</div>`);
          if(penalties)rows.push(`<div><span class="research-label">${esc(d().guide_penalties)}：</span>${esc(penalties)}</div>`);
          if(currentLang!=='zh-TW'&&(v.variant_name||v.required_conditions||v.boosters||v.penalties)&&!variantName&&!rows.length)suppressedLocalizedGuide=true;
          if(!variantName&&!rows.length)return'';
          return `${variantName?`<div class="variant-name">${esc(variantName)}</div>`:''}${rows.join('')}`;
        }).filter(Boolean).join('');
        const scoreHtml=score===undefined||score===null?'':`<div class="opportunity-score ${opportunityScoreClass(score)}">${score}</div>`;
        const modalSubject=opportunityDisplayName(spot,op.opportunity_id,op.legacy_theme,op.name_zh);
        const scoreVerdict=!guideOnly&&m?opportunityVerdict(m,modalSubject):{primary:'',detail:''};
        const current=!guideOnly&&m&&scoreVerdict.primary?`<div class="opportunity-current">${esc(scoreVerdict.primary)}</div>`:'';
        const scoreFactors=(!guideOnly&&m?.factors||[]).map(f=>{const text=trFactor(f);return text?`<span class="factor-pill ${f.type==='minus'?'factor-minus':'factor-plus'}">${f.type==='minus'?'−':'＋'} ${text}</span>`:'';}).filter(Boolean).join('');
        const scoreStatus=!guideOnly&&m?scoreVerdict.primary:'';
        const scoreStatusDetail=!guideOnly&&m?scoreVerdict.detail:'';
        const scoreIndicator=!guideOnly&&m?trMessage(m.indicator_key):'';
        const scoreConfidence=!guideOnly&&m?.score_confidence?`<div class="score-explain-confidence"><span class="research-label">${esc(d().guide_confidence)}：</span>${esc(confidenceLabel(m.score_confidence))}</div>`:'';
        const scoreExplain=!guideOnly&&m?`<details class="score-explain"><summary>${esc(d().guide_score_why)}</summary><div class="score-explain-body"><div class="score-explain-status"><span class="research-label">${esc(d().guide_score_status)}：</span>${esc(scoreStatus)}${scoreStatusDetail&&scoreStatusDetail!==scoreStatus?`<br>${esc(scoreStatusDetail)}`:''}${scoreIndicator&&scoreIndicator!==scoreStatus&&scoreIndicator!==scoreStatusDetail?`<br>${esc(scoreIndicator)}`:''}</div>${scoreConfidence}${scoreFactors?`<div class="factor-row">${scoreFactors}</div>`:''}</div></details>`:'';
        const metaRows=[];
        const dayBestWindow=!guideOnly&&m&&(m.window_start||m.best_time)?fmtWindow(m):'';
        if(dayBestWindow)metaRows.push(`<div><span class="research-label">${esc(d().guide_day_best)}：</span>${esc(dayBestWindow)}</div>`);
        if(viewpoints.length)metaRows.push(`<div><span class="research-label">${esc(d().guide_viewpoint)}：</span>${esc(viewpoints.join('／'))}</div>`);
        const guideRows=[];
        const guideTime=localizedResearchValue(op,'best_time');
        if(guideTime)guideRows.push(`<div><span class="research-label">${esc(d().guide_time)}：</span>${esc(guideTime)}</div>`);
        const bestSeason=localizedResearchValue(op,'best_season');
        if(bestSeason)guideRows.push(`<div><span class="research-label">${esc(d().guide_season)}：</span>${esc(bestSeason)}</div>`);
        if(currentLang!=='zh-TW'&&((op.best_time&&!guideTime)||(op.best_season&&!bestSeason)||(op.viewpoints||[]).some(v=>v.name&&!localizedResearchValue(v,'name'))))suppressedLocalizedGuide=true;
        const localizationNote=suppressedLocalizedGuide?`<div class="association-note">${esc(d().guide_translation_limited)}</div>`:'';
        const guideBody=`${guideRows.join('')}${variants}${localizationNote}`;
        return `<div class="opportunity-card${guideOnly?' opportunity-card-guide':''}">
          <div class="opportunity-head"><div class="opportunity-title">${esc(modalSubject)}</div>${scoreHtml}</div>
          ${current}
          ${metaRows.length?`<div class="opportunity-meta">${metaRows.join('')}</div>`:''}
          ${scoreExplain}
          ${guideBody?`<details class="research-details"><summary>${esc(d().guide_details)}</summary><div class="research-block">${guideBody}</div></details>`:''}
        </div>`;
      };
      const selectedCards=selectedDateOpportunities.map(op=>renderOpportunityCard(op,dayScores[op.opportunity_id],false)).join('');
      const guideCards=guideOnlyOpportunities.map(op=>renderOpportunityCard(op,null,true)).join('');
      const selectedSection=selectedCards
        ? `<div class="opportunity-list">${selectedCards}</div>`
        : `<div class="place-guide-empty">${esc(d().guide_no_selected_date)}</div>`;
      const guideSummary=(selectedCards?d().guide_more_subjects:d().guide_all_subjects).replace('{n}',guideOnlyOpportunities.length);
      const guideSection=guideCards?`<details class="place-guide-more"><summary>${esc(guideSummary)}</summary><div class="place-guide-more-body"><div class="place-guide-intro">${esc(d().guide_subjects_note)}<br>${esc(d().researched_only)}</div><div class="opportunity-list">${guideCards}</div></div></details>`:'';
      body.innerHTML=`<div class="place-guide-time-note">🕒 ${esc(d().place_time_note)}</div><section class="place-guide-selected"><div class="place-guide-section-title">${esc(d().guide_selected_date)}</div>${selectedSection}</section>${guideSection}`;
      overlay.style.display='flex';
      syncModalScrollLock();
    }
    function syncModalScrollLock(){
      const open=[document.getElementById('place-modal-overlay'),document.getElementById('modal-overlay')].some(el=>el?.style.display==='flex');
      document.body.style.overflow=open?'hidden':'';
    }
    function closePlaceModal(){document.getElementById('place-modal-overlay').style.display='none';activePlaceSpot=null;activePlaceSummary=null;syncModalScrollLock();}

    async function loadDetails(region,spotId){
      const key=`${region}:${spotId}`,baseUrl=`./weather_details/${region}/${encodeURIComponent(spotId)}.json`;
      let expectedVersion=currentData?.updated_at||null;
      const versionMatches=(x,version=expectedVersion)=>!version||x?.updated_at===version;
      const detailUrl=(version,retry=0)=>{
        if(!version)return baseUrl;
        const suffix=`v=${encodeURIComponent(version)}${retry?`&retry=${retry}`:''}`;
        return `${baseUrl}?${suffix}`;
      };
      const remember=x=>{memoryDetails.set(key,x);return x;};
      if(memoryDetails.has(key)){const m=memoryDetails.get(key);if(versionMatches(m))return m;memoryDetails.delete(key);}

      let url=detailUrl(expectedVersion);
      const cached=await cacheMatch(baseUrl);
      if(cached&&versionMatches(cached)){
        remember(cached);
        fetchAndCache(url,null,baseUrl).then(x=>{if(versionMatches(x))memoryDetails.set(key,x);}).catch(()=>{});
        return cached;
      }

      const fresh=await fetchAndCache(url,null,baseUrl);
      if(versionMatches(fresh))return remember(fresh);

      // Summary and Place shards are committed together, but browser/CDN cache
      // turnover can briefly expose different generations. Re-sync the summary
      // once, never downgrade to an older summary, then retry this shard through
      // a versioned/cache-busted URL before surfacing a user-facing error.
      const summary=await fetchAndCache(`./${region}_weather.json`,null);
      const currentVersion=currentData?.updated_at||expectedVersion;
      const currentMs=Date.parse(currentVersion||'');
      const summaryMs=Date.parse(summary?.updated_at||'');
      const summaryIsNotOlder=!currentVersion||summary?.updated_at===currentVersion||
        (Number.isFinite(summaryMs)&&Number.isFinite(currentMs)&&summaryMs>=currentMs);
      if(summaryIsNotOlder){
        expectedVersion=summary?.updated_at||expectedVersion;
        if(region===currentRegion)applyData(summary,region,activeLoadSequence);
      }else{
        expectedVersion=currentVersion;
      }

      if(versionMatches(fresh,expectedVersion))return remember(fresh);
      url=detailUrl(expectedVersion,1);
      const retry=await fetchAndCache(url,null,baseUrl);
      if(versionMatches(retry,expectedVersion))return remember(retry);
      throw new Error(d().detail_sync_wait);
    }
    async function openWeatherModal(spot,summaryMetric){
      document.getElementById('modal-overlay').style.display='flex';syncModalScrollLock();const showLocal=!(currentRegion==='tw'&&currentLang==='zh-TW');document.getElementById('modal-spot-name').innerText=`🌦️ ${spotName(spot)} — ${d().weather_link.replace(/^🌦️\s*/, '')}`;document.getElementById('modal-summary').innerText=d().detail_loading;document.getElementById('timeline-head').innerHTML='';document.getElementById('timeline-body').innerHTML='';document.getElementById('timeline-mobile').innerHTML='';
      try{const payload=await loadDetails(currentRegion,spot.spot_id);const detail=payload?.spot;if(!detail||detail.spot_id!==spot.spot_id)throw new Error('missing spot');const latestSummarySpot=currentSpots.find(x=>x.spot_id===spot.spot_id);const latestSummaryMetric=latestSummarySpot?getMetric(latestSummarySpot):null;renderWeatherModal(detail,latestSummaryMetric||summaryMetric);}catch(e){document.getElementById('modal-summary').innerText=`⚠️ ${d().detail_error}`;}
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
      const day=currentDayForSpot(spot);const activeTheme=summaryMetric?.theme||'mountain_view';const activeOpportunityId=summaryMetric?.opportunity_id||null;const activeOpportunityName=opportunityDisplayName(spot,activeOpportunityId,activeTheme,summaryMetric?.opportunity_name);const selectedDate=selectedDateForSpot(currentSpots.find(x=>x.spot_id===spot.spot_id)||spot);
      const darkSky=darkSkyText(spot,activeTheme);document.getElementById('modal-summary').innerHTML=`<div class="modal-summary-main">${d().best_theme}${esc(activeOpportunityName)}</div><div class="modal-summary-window">${d().best_window}${fmtWindow(summaryMetric)}</div>${darkSky?`<div class="modal-summary-extra">${darkSky}</div>`:''}`;
      const isAurora=activeTheme==='aurora',thead=document.getElementById('timeline-head'),tbody=document.getElementById('timeline-body'),mobile=document.getElementById('timeline-mobile');thead.innerHTML=`<tr><th>${d().th_time}</th><th>${d().th_theme}</th><th>${d().th_score}</th><th>${d().th_status}</th>${isAurora?`<th>${d().th_kp}</th>`:''}<th class="key-metric">${d().th_cloud_base}</th><th>${d().th_temp} (${tempUnitLabel()})</th><th>${d().th_rh}</th><th class="key-metric">${d().th_clow}</th><th>${d().th_cmid}</th><th>${d().th_chigh}</th><th>${d().th_wind}</th><th class="key-metric">${d().th_vis}</th><th>${d().th_astro}</th></tr>`;tbody.innerHTML='';mobile.innerHTML='';
      let nowAnchorAssigned=false;
      (spot.hourly_forecast||[]).forEach(item=>{const metrics=(activeOpportunityId&&item.opportunity_scores?.[activeOpportunityId])||item.theme_scores?.[activeTheme];if(!metrics)return;const isNowAnchor=!nowAnchorAssigned&&!item.is_past;if(isNowAnchor)nowAnchorAssigned=true;const isBest=!!(selectedDate&&item.local_date===selectedDate&&summaryMetric?.window_start&&item.time>=summaryMetric.window_start&&item.time<summaryMetric.window_end);const rowClass=isBest?'best-row':(item.is_past?'past-row':'');const tr=document.createElement('tr');tr.className=rowClass;if(isNowAnchor)tr.dataset.nowAnchor='true';const astro=astroText(item,activeTheme);tr.innerHTML=`<td>${item.time}${item.is_past?` <span class="tag-past">${esc(d().tag_past)}</span>`:''}${isBest?` <span class="tag-best">${esc(d().tag_best)}</span>`:''}</td><td>${esc(activeOpportunityName)}</td><td><span class="timeline-score-badge ${opportunityScoreClass(Number(metrics.score))}">${metrics.score}</span></td><td>${esc(opportunityVerdict(metrics,activeOpportunityName).primary)}</td>${isAurora?`<td>${item.kp??'—'}</td>`:''}<td class="key-metric">${item.cloud_base_agl??'—'}m</td><td>${formatTemp(item.temp)}</td><td>${item.rh??'—'}%</td><td class="key-metric">${item.c_low??'—'}%</td><td>${item.c_mid??'—'}%</td><td>${item.c_high??'—'}%</td><td>${item.wind??'—'}m/s</td><td class="key-metric">${item.visibility??'—'}km</td><td>${astro||'—'}</td>`;tbody.appendChild(tr);
        const card=document.createElement('div');card.className=`timeline-mobile-card ${rowClass}`;if(isNowAnchor)card.dataset.nowAnchor='true';card.innerHTML=`<div class="timeline-mobile-head"><div><div class="timeline-mobile-time">${esc(item.time)}${item.is_past?` <span class="tag-past">${esc(d().tag_past)}</span>`:''}${isBest?` <span class="tag-best">${esc(d().tag_best)}</span>`:''}</div><div class="timeline-mobile-status">${esc(opportunityVerdict(metrics,activeOpportunityName).primary)}</div></div><div class="timeline-mobile-score"><span class="timeline-score-badge ${opportunityScoreClass(Number(metrics.score))}">${metrics.score}</span></div></div><div class="timeline-mobile-metrics"><div class="timeline-mobile-metric"><b>${d().th_temp}</b> ${formatTemp(item.temp)}</div><div class="timeline-mobile-metric primary"><b>${d().th_vis}</b> ${item.visibility??'—'} km</div><div class="timeline-mobile-metric primary"><b>${d().th_clow}</b> ${item.c_low??'—'}%</div><div class="timeline-mobile-metric"><b>${d().th_cmid}</b> ${item.c_mid??'—'}%</div><div class="timeline-mobile-metric"><b>${d().th_chigh}</b> ${item.c_high??'—'}%</div><div class="timeline-mobile-metric"><b>${d().th_wind}</b> ${item.wind??'—'} m/s</div><div class="timeline-mobile-metric primary"><b>${d().th_cloud_base}</b> ${item.cloud_base_agl??'—'} m</div><div class="timeline-mobile-metric"><b>${d().th_rh}</b> ${item.rh??'—'}%</div>${isAurora?`<div class="timeline-mobile-metric"><b>${d().th_kp}</b> ${item.kp??'—'}</div>`:''}</div>${astro?`<div class="timeline-mobile-astro">${esc(astro)}</div>`:''}`;mobile.appendChild(card);
      });
      scrollWeatherModalToCurrent();
    }
    function closeModal(){document.getElementById('modal-overlay').style.display='none';activeModalSpot=null;activeModalSummary=null;syncModalScrollLock();}
    document.addEventListener('keydown',e=>{
      if(e.key!=='Escape')return;
      if(document.getElementById('modal-overlay').style.display==='flex')closeModal();
      else if(document.getElementById('place-modal-overlay').style.display==='flex')closePlaceModal();
    });

    async function cleanupOldCaches(){try{if(!('caches'in window))return;const keys=await caches.keys();await Promise.all(keys.filter(k=>k.startsWith('chaselights-')&&k!==CACHE_NAME).map(k=>caches.delete(k)));}catch{}}
    function initializeApp(){cleanupOldCaches();applyStaticI18n();renderSubNav();syncDayButtons();loadData(currentRegion);}
    initializeApp();