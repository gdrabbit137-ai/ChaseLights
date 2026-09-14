"""
PhotoWeather v0.2 - 智慧推薦系統
基於使用者偏好、歷史行為和天氣條件提供個人化推薦
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import get_user, get_user_favorites, get_weather_history
import random

class SmartRecommendationEngine:
    """智慧推薦引擎"""
    
    def __init__(self):
        # 攝影類型權重配置
        self.genre_weights = {
            "mountain": {"visibility": 0.4, "cloud_cover": 0.3, "weather_code": 0.2, "wind": 0.1},
            "coastal": {"visibility": 0.3, "cloud_cover": 0.2, "weather_code": 0.3, "tide": 0.2},
            "waterfall": {"cloud_cover": 0.4, "humidity": 0.3, "weather_code": 0.2, "lighting": 0.1},
            "forest": {"cloud_cover": 0.3, "humidity": 0.2, "weather_code": 0.3, "lighting": 0.2},
            "urban": {"visibility": 0.4, "weather_code": 0.4, "air_quality": 0.2},
            "star": {"cloud_cover": 0.5, "moon_phase": 0.3, "visibility": 0.2}
        }
        
        # 季節性題材
        self.seasonal_themes = {
            1: ["雪景", "冬季", "霧淞", "冰瀑"],
            2: ["梅花", "雪景", "冬末"],
            3: ["櫻花", "春芽", "油菜花"],
            4: ["櫻花", "春花", "新綠", "銀河"],
            5: ["新綠", "銀河", "螢火蟲"],
            6: ["藍眼淚", "夏季", "銀河"],
            7: ["夏日", "銀河", "鮭魚", "藍眼淚"],
            8: ["金針花", "銀河", "極光", "鮭魚"],
            9: ["金針花", "秋芒", "極光"],
            10: ["楓葉", "紅葉", "秋色", "極光"],
            11: ["楓葉", "紅葉", "秋末", "極光"],
            12: ["雪景", "冬季", "極光", "星空"]
        }
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """取得使用者偏好設定"""
        user = get_user(user_id=user_id)
        if user and user['preferences']:
            return user['preferences']
        
        # 預設偏好
        return {
            "preferred_genres": ["mountain", "coastal"],
            "preferred_times": ["sunrise", "sunset", "golden_hour"],
            "weather_tolerance": "moderate",  # strict, moderate, flexible
            "notification_regions": [],
            "skill_level": "intermediate",  # beginner, intermediate, advanced
            "equipment": {
                "has_tripod": True,
                "has_filters": False,
                "preferred_focal_length": "wide"  # wide, normal, telephoto, all
            }
        }
    
    def analyze_user_behavior(self, user_id: int) -> Dict:
        """分析使用者行為模式"""
        favorites = get_user_favorites(user_id)
        
        # 分析收藏的景點類型
        genre_count = {}
        region_count = {}
        
        for fav in favorites:
            # 這裡需要查找景點的類型資訊
            # 簡化版：從景點名稱推測
            spot_genre = self._guess_spot_genre(fav['spot_name'])
            genre_count[spot_genre] = genre_count.get(spot_genre, 0) + 1
            region_count[fav['region']] = region_count.get(fav['region'], 0) + 1
        
        # 計算偏好權重
        total_favs = len(favorites)
        genre_preferences = {}
        region_preferences = {}
        
        if total_favs > 0:
            for genre, count in genre_count.items():
                genre_preferences[genre] = count / total_favs
            
            for region, count in region_count.items():
                region_preferences[region] = count / total_favs
        
        return {
            "favorite_genres": genre_preferences,
            "favorite_regions": region_preferences,
            "activity_score": min(total_favs / 10.0, 1.0),  # 活躍度 0-1
            "diversity_score": len(genre_count) / max(len(self.genre_weights), 1)  # 多樣性 0-1
        }
    
    def _guess_spot_genre(self, spot_name: str) -> str:
        """從景點名稱推測攝影類型"""
        spot_name = spot_name.lower()
        
        if any(keyword in spot_name for keyword in ['山', '峰', '嶺', '主峰', '北峰', 'mountain']):
            return "mountain"
        elif any(keyword in spot_name for keyword in ['海', '港', '漁港', '岬', '角', '海灘', 'coast']):
            return "coastal"
        elif any(keyword in spot_name for keyword in ['瀑布', '溪', '潭', 'waterfall', 'falls']):
            return "waterfall"
        elif any(keyword in spot_name for keyword in ['森林', '林道', '步道', 'forest', 'trail']):
            return "forest"
        elif any(keyword in spot_name for keyword in ['city', '城市', '大樓', '橋']):
            return "urban"
        else:
            return "general"
    
    def get_personalized_recommendations(self, user_id: int, region: str, 
                                        weather_data: Dict, 
                                        spots_data: List[Dict],
                                        limit: int = 5) -> List[Dict]:
        """取得個人化推薦"""
        
        user_prefs = self.get_user_preferences(user_id)
        user_behavior = self.analyze_user_behavior(user_id)
        current_month = datetime.now().month
        
        # 為每個景點計算個人化分數
        personalized_spots = []
        
        for spot in spots_data:
            # 基礎天氣分數
            base_score = spot.get('score', 0)
            
            # 個人化調整
            personalization_bonus = 0
            
            # 1. 類型偏好加分
            spot_genre = self._guess_spot_genre(spot['name'])
            if spot_genre in user_prefs.get('preferred_genres', []):
                personalization_bonus += 15
            
            # 2. 歷史行為加分
            if spot_genre in user_behavior.get('favorite_genres', {}):
                weight = user_behavior['favorite_genres'][spot_genre]
                personalization_bonus += int(weight * 20)
            
            # 3. 季節性加分
            seasonal_themes = self.seasonal_themes.get(current_month, [])
            spot_themes = spot.get('themes', [])
            for theme in spot_themes:
                if any(seasonal in theme for seasonal in seasonal_themes):
                    personalization_bonus += 10
                    break
            
            # 4. 天氣容忍度調整
            weather_tolerance = user_prefs.get('weather_tolerance', 'moderate')
            if weather_tolerance == 'strict' and base_score < 60:
                personalization_bonus -= 20
            elif weather_tolerance == 'flexible' and base_score >= 40:
                personalization_bonus += 10
            
            # 5. 技能等級調整
            skill_level = user_prefs.get('skill_level', 'intermediate')
            difficulty_keywords = ['主峰', '高山', '困難', 'difficult', 'challenging']
            is_difficult = any(keyword in spot['name'] for keyword in difficulty_keywords)
            
            if skill_level == 'beginner' and is_difficult:
                personalization_bonus -= 15
            elif skill_level == 'advanced' and is_difficult:
                personalization_bonus += 10
            
            # 計算最終分數
            final_score = max(0, min(100, base_score + personalization_bonus))
            
            personalized_spot = spot.copy()
            personalized_spot['personalized_score'] = final_score
            personalized_spot['personalization_bonus'] = personalization_bonus
            personalized_spot['recommendation_reason'] = self._generate_recommendation_reason(
                user_prefs, user_behavior, spot, personalization_bonus
            )
            
            personalized_spots.append(personalized_spot)
        
        # 排序並返回前N個
        personalized_spots.sort(key=lambda x: x['personalized_score'], reverse=True)
        return personalized_spots[:limit]
    
    def _generate_recommendation_reason(self, user_prefs: Dict, user_behavior: Dict, 
                                      spot: Dict, bonus: int) -> str:
        """生成推薦理由"""
        reasons = []
        
        spot_genre = self._guess_spot_genre(spot['name'])
        
        if spot_genre in user_prefs.get('preferred_genres', []):
            genre_names = {
                "mountain": "山岳攝影",
                "coastal": "海岸攝影", 
                "waterfall": "瀑布攝影",
                "forest": "森林攝影",
                "urban": "城市攝影"
            }
            reasons.append(f"符合您偏好的{genre_names.get(spot_genre, '攝影類型')}")
        
        if spot_genre in user_behavior.get('favorite_genres', {}):
            reasons.append("與您的收藏偏好相符")
        
        if bonus > 10:
            reasons.append("當季推薦題材")
        
        if spot.get('score', 0) > 80:
            reasons.append("天氣條件極佳")
        
        if not reasons:
            reasons.append("值得探索的景點")
        
        return " • ".join(reasons[:3])  # 最多顯示3個理由
    
    def get_smart_tips(self, user_id: int, spot_data: Dict, weather_data: Dict) -> Dict:
        """取得智慧拍攝建議"""
        user_prefs = self.get_user_preferences(user_id)
        skill_level = user_prefs.get('skill_level', 'intermediate')
        equipment = user_prefs.get('equipment', {})
        
        tips = {
            "camera_settings": self._get_camera_settings(spot_data, weather_data, skill_level),
            "equipment_advice": self._get_equipment_advice(spot_data, weather_data, equipment),
            "composition_tips": self._get_composition_tips(spot_data, skill_level),
            "timing_advice": self._get_timing_advice(spot_data, weather_data),
            "safety_notes": self._get_safety_notes(spot_data, weather_data)
        }
        
        return tips
    
    def _get_camera_settings(self, spot_data: Dict, weather_data: Dict, skill_level: str) -> List[str]:
        """取得相機設定建議"""
        settings = []
        
        # 基於天氣條件的設定
        visibility = weather_data.get('visibility', 30)
        cloud_cover = weather_data.get('cloud_cover', 50)
        
        if visibility > 20:
            settings.append("光圈 f/8-f/11 獲得最佳銳利度")
        else:
            settings.append("光圈 f/5.6-f/8 在霧霾中保持對比")
        
        if cloud_cover > 70:
            settings.append("陰天漫射光，ISO 400-800")
        else:
            settings.append("晴天強光，ISO 100-200")
        
        # 基於景點類型的設定
        spot_genre = self._guess_spot_genre(spot_data.get('name', ''))
        
        if spot_genre == "waterfall":
            settings.append("慢快門 1/4-2秒 拍攝流水絲綢感")
        elif spot_genre == "mountain":
            settings.append("超焦距對焦 前景到無限遠都清晰")
        elif spot_genre == "coastal":
            settings.append("使用CPL濾鏡減少反光")
        
        # 技能等級調整
        if skill_level == "beginner":
            settings.append("建議使用光圈先決模式 (A/Av)")
        elif skill_level == "advanced":
            settings.append("手動模式精確控制曝光")
        
        return settings
    
    def _get_equipment_advice(self, spot_data: Dict, weather_data: Dict, equipment: Dict) -> List[str]:
        """取得器材建議"""
        advice = []
        
        spot_genre = self._guess_spot_genre(spot_data.get('name', ''))
        
        # 鏡頭建議
        preferred_focal = equipment.get('preferred_focal_length', 'wide')
        
        if spot_genre == "mountain":
            if preferred_focal == 'wide':
                advice.append("廣角鏡 16-35mm 拍攝壯闊山景")
            advice.append("長焦鏡 70-200mm 壓縮遠山層次")
        elif spot_genre == "coastal":
            advice.append("廣角鏡捕捉海天一線")
        
        # 濾鏡建議
        has_filters = equipment.get('has_filters', False)
        
        if not has_filters:
            if spot_genre == "waterfall":
                advice.append("建議購買ND濾鏡拍攝流水")
            elif spot_genre == "coastal":
                advice.append("CPL濾鏡可減少海面反光")
        
        # 三腳架建議
        has_tripod = equipment.get('has_tripod', False)
        wind_speed = weather_data.get('wind_speed', 0)
        
        if not has_tripod:
            advice.append("建議攜帶三腳架穩定拍攝")
        elif wind_speed > 15:
            advice.append("強風天氣，加重三腳架或降低高度")
        
        return advice
    
    def _get_composition_tips(self, spot_data: Dict, skill_level: str) -> List[str]:
        """取得構圖建議"""
        tips = []
        
        spot_genre = self._guess_spot_genre(spot_data.get('name', ''))
        
        if spot_genre == "mountain":
            tips.append("尋找前景元素增加層次感")
            tips.append("利用引導線指向主峰")
        elif spot_genre == "coastal":
            tips.append("利用海浪線條作為引導")
            tips.append("岩石作前景平衡海天構圖")
        elif spot_genre == "waterfall":
            tips.append("包含周圍岩石展現瀑布規模")
            tips.append("垂直構圖強調瀑布高度")
        
        # 技能等級調整
        if skill_level == "beginner":
            tips.append("遵循三分法則放置主體")
        elif skill_level == "advanced":
            tips.append("嘗試打破常規創造獨特視角")
        
        return tips
    
    def _get_timing_advice(self, spot_data: Dict, weather_data: Dict) -> List[str]:
        """取得時機建議"""
        advice = []
        
        best_time = spot_data.get('best_time', '')
        
        if '日出' in best_time:
            advice.append("日出前30分鐘到達準備")
            advice.append("藍調時刻有特殊光線效果")
        elif '日落' in best_time:
            advice.append("日落前1小時確認構圖")
            advice.append("日落後30分鐘仍有餘輝")
        
        # 天氣相關時機
        cloud_cover = weather_data.get('cloud_cover', 50)
        
        if cloud_cover > 80:
            advice.append("雨後放晴時刻最佳")
        elif cloud_cover < 30:
            advice.append("晴天適合全日拍攝")
        
        return advice
    
    def _get_safety_notes(self, spot_data: Dict, weather_data: Dict) -> List[str]:
        """取得安全提醒"""
        notes = []
        
        # 天氣安全
        wind_speed = weather_data.get('wind_speed', 0)
        precipitation = weather_data.get('precipitation_probability', 0)
        
        if wind_speed > 20:
            notes.append("強風天氣，注意器材安全")
        
        if precipitation > 60:
            notes.append("高降雨機率，準備防水裝備")
        
        # 地點安全
        spot_name = spot_data.get('name', '').lower()
        
        if any(keyword in spot_name for keyword in ['山', '峰', '高山']):
            notes.append("山區氣候變化快，注意保暖")
        
        if any(keyword in spot_name for keyword in ['海', '岸', '岬']):
            notes.append("注意潮汐變化和海浪安全")
        
        return notes
    
    def get_trending_spots(self, region: str, days: int = 7) -> List[Dict]:
        """取得熱門趨勢景點"""
        # 這裡可以基於使用者活動、評論、收藏等資料
        # 簡化版：隨機選擇一些景點作為趨勢
        
        trending = [
            {"name": "合歡山主峰", "trend_score": 95, "reason": "雲海大爆發"},
            {"name": "清水斷崖", "trend_score": 88, "reason": "天氣極佳"},
            {"name": "阿里山", "trend_score": 82, "reason": "日出雲海"},
            {"name": "太魯閣", "trend_score": 79, "reason": "峽谷光影"},
            {"name": "墾丁", "trend_score": 75, "reason": "夕陽火燒雲"}
        ]
        
        return trending

# 實例化全局推薦引擎
recommendation_engine = SmartRecommendationEngine()