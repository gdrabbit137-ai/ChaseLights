"""
ChaseLights v0.2 - 擴展天氣資料模組
增加月相、潮汐、AQI、更詳細的天氣預測
"""
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests module not available, some enhanced weather features will be disabled")

class EnhancedWeatherData:
    """擴展的天氣資料類"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    def get_moon_phase(self, date: datetime) -> Dict:
        """計算月相資訊"""
        # 使用天文算法計算月相
        year = date.year
        month = date.month
        day = date.day
        
        # Julian day calculation
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + a // 4
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        
        # Moon phase calculation
        days_since_new = (jd - 2451549.5) % 29.53058867
        phase = days_since_new / 29.53058867
        
        # 月相名稱
        if phase < 0.0625:
            phase_name = "新月"
            phase_emoji = "🌑"
        elif phase < 0.1875:
            phase_name = "蛾眉月"
            phase_emoji = "🌒"
        elif phase < 0.3125:
            phase_name = "上弦月"
            phase_emoji = "🌓"
        elif phase < 0.4375:
            phase_name = "盈凸月"
            phase_emoji = "🌔"
        elif phase < 0.5625:
            phase_name = "滿月"
            phase_emoji = "🌕"
        elif phase < 0.6875:
            phase_name = "虧凸月"
            phase_emoji = "🌖"
        elif phase < 0.8125:
            phase_name = "下弦月"
            phase_emoji = "🌗"
        else:
            phase_name = "殘月"
            phase_emoji = "🌘"
        
        # 計算月亮亮度 (0-1)
        illumination = (1 - abs(0.5 - phase) * 2) ** 0.5
        
        return {
            "phase": phase,
            "phase_name": phase_name,
            "phase_emoji": phase_emoji,
            "illumination": round(illumination, 2),
            "is_good_for_milkyway": illumination < 0.3,  # 銀河攝影適合度
            "rise_time": self._calculate_moon_rise(date, phase),
            "set_time": self._calculate_moon_set(date, phase)
        }
    
    def _calculate_moon_rise(self, date: datetime, phase: float) -> str:
        """計算月出時間（簡化版）"""
        # 簡化的月出時間計算
        base_hour = phase * 24  # 粗略估算
        rise_hour = int(base_hour) % 24
        rise_minute = int((base_hour - rise_hour) * 60)
        return f"{rise_hour:02d}:{rise_minute:02d}"
    
    def _calculate_moon_set(self, date: datetime, phase: float) -> str:
        """計算月落時間（簡化版）"""
        # 簡化的月落時間計算
        base_hour = (phase * 24 + 12) % 24
        set_hour = int(base_hour)
        set_minute = int((base_hour - set_hour) * 60)
        return f"{set_hour:02d}:{set_minute:02d}"
    
    def get_tidal_info(self, lat: float, lon: float, date: datetime) -> Dict:
        """取得潮汐資訊（簡化版，實際應串接潮汐API）"""
        # 這裡使用簡化的潮汐計算
        # 實際應用中應該串接專業的潮汐API如NOAA或其他服務
        
        # 簡化的潮汐模型（基於月相和地理位置）
        moon_phase = self.get_moon_phase(date)["phase"]
        
        # 一天兩次高潮兩次低潮
        hours = date.hour + date.minute / 60
        tide_cycle = (hours + lat * 0.1) % 12.42  # 月球日約12.42小時
        
        if tide_cycle < 3.1:
            tide_level = "高潮"
            tide_height = 1.5 + 0.5 * math.sin(tide_cycle * 2 * math.pi / 6.2)
        elif tide_cycle < 6.2:
            tide_level = "退潮"
            tide_height = 0.5 + 0.3 * math.cos(tide_cycle * 2 * math.pi / 6.2)
        elif tide_cycle < 9.3:
            tide_level = "低潮"  
            tide_height = 0.2 + 0.2 * math.sin(tide_cycle * 2 * math.pi / 6.2)
        else:
            tide_level = "漲潮"
            tide_height = 1.0 + 0.4 * math.cos(tide_cycle * 2 * math.pi / 6.2)
        
        return {
            "current_level": tide_level,
            "height_meters": round(tide_height, 1),
            "next_high": self._calculate_next_tide(date, "high"),
            "next_low": self._calculate_next_tide(date, "low"),
            "is_good_for_reflection": tide_level in ["低潮", "退潮後期"]
        }
    
    def _calculate_next_tide(self, date: datetime, tide_type: str) -> str:
        """計算下次潮汐時間"""
        # 簡化計算
        if tide_type == "high":
            next_time = date + timedelta(hours=6.2)
        else:
            next_time = date + timedelta(hours=3.1)
        
        return next_time.strftime("%H:%M")
    
    def get_air_quality(self, lat: float, lon: float) -> Dict:
        """取得空氣品質資訊"""
        if not REQUESTS_AVAILABLE:
            return {
                "pm25": None,
                "pm10": None,
                "aqi_level": "無資料",
                "aqi_color": "#999999",
                "visibility_impact": "無資料",
                "photography_suitable": True,
                "aerosol_optical_depth": None
            }
            
        try:
            # 使用Open-Meteo的空氣品質API
            url = "https://air-quality-api.open-meteo.com/v1/air-quality"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "ozone", "aerosol_optical_depth"],
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                
                # 計算綜合AQI（簡化版）
                pm25 = current.get("pm2_5", 0) or 0
                pm10 = current.get("pm10", 0) or 0
                
                # 簡化的AQI計算
                if pm25 <= 12:
                    aqi_level = "優"
                    aqi_color = "#00E400"
                elif pm25 <= 35:
                    aqi_level = "良"
                    aqi_color = "#FFFF00"
                elif pm25 <= 55:
                    aqi_level = "輕度污染"
                    aqi_color = "#FF7E00"
                elif pm25 <= 150:
                    aqi_level = "中度污染"
                    aqi_color = "#FF0000"
                else:
                    aqi_level = "重度污染"
                    aqi_color = "#8F3F97"
                
                visibility_impact = "良好" if pm25 <= 35 else "受影響"
                
                return {
                    "pm25": pm25,
                    "pm10": pm10,
                    "aqi_level": aqi_level,
                    "aqi_color": aqi_color,
                    "visibility_impact": visibility_impact,
                    "photography_suitable": pm25 <= 55,
                    "aerosol_optical_depth": current.get("aerosol_optical_depth")
                }
            
        except Exception as e:
            print(f"AQI API error: {e}")
        
        # 預設值
        return {
            "pm25": None,
            "pm10": None,
            "aqi_level": "無資料",
            "aqi_color": "#999999",
            "visibility_impact": "無資料",
            "photography_suitable": True,
            "aerosol_optical_depth": None
        }
    
    def get_enhanced_forecast(self, lat: float, lon: float, days: int = 3) -> Dict:
        """取得增強版天氣預報"""
        if not REQUESTS_AVAILABLE:
            return {
                "error": "Network module not available",
                "moon_phases": [self.get_moon_phase(datetime.now())],
                "tidal_info": [],
                "air_quality": self.get_air_quality(lat, lon)
            }
            
        try:
            # 原有的Open-Meteo參數 + 新增參數
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                    "precipitation", "weather_code", "cloud_cover", "pressure_msl",
                    "wind_speed_10m", "wind_direction_10m", "uv_index"
                ],
                "hourly": [
                    "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                    "apparent_temperature", "precipitation_probability", "precipitation",
                    "weather_code", "pressure_msl", "cloud_cover", "cloud_cover_low",
                    "cloud_cover_mid", "cloud_cover_high", "visibility",
                    "wind_speed_10m", "wind_direction_10m", "uv_index", "is_day"
                ],
                "daily": [
                    "weather_code", "temperature_2m_max", "temperature_2m_min",
                    "sunrise", "sunset", "precipitation_sum", "precipitation_hours",
                    "wind_speed_10m_max", "wind_gusts_10m_max", "uv_index_max"
                ],
                "forecast_days": days,
                "timezone": "auto"
            }
            
            response = requests.get(self.base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # 加入月相和潮汐資訊
                enhanced_data = data.copy()
                enhanced_data["moon_phases"] = []
                enhanced_data["tidal_info"] = []
                enhanced_data["air_quality"] = self.get_air_quality(lat, lon)
                
                # 為每一天添加月相和潮汐
                base_date = datetime.now()
                for i in range(days):
                    target_date = base_date + timedelta(days=i)
                    enhanced_data["moon_phases"].append(self.get_moon_phase(target_date))
                    
                    # 只有海岸景點才添加潮汐資訊
                    if self._is_coastal_location(lat, lon):
                        enhanced_data["tidal_info"].append(self.get_tidal_info(lat, lon, target_date))
                
                return enhanced_data
            
        except Exception as e:
            print(f"Enhanced weather API error: {e}")
            return {}
    
    def _is_coastal_location(self, lat: float, lon: float) -> bool:
        """判斷是否為海岸位置（簡化版）"""
        # 這裡應該使用更精確的地理資料庫
        # 簡化版：台灣海岸線粗略判斷
        if 22 <= lat <= 25.5 and 120 <= lon <= 122:
            # 台灣的一些已知海岸景點
            coastal_areas = [
                (25.2973, 121.5717),  # 野柳
                (25.1249, 121.8999),  # 鼻頭角
                (24.9578, 121.9014),  # 三貂角
                (23.9739, 121.6186),  # 清水斷崖
                (22.0015, 120.7479),  # 鵝鑾鼻
            ]
            
            # 簡單的距離檢查（約50km範圍內認為是海岸）
            for coastal_lat, coastal_lon in coastal_areas:
                distance = ((lat - coastal_lat) ** 2 + (lon - coastal_lon) ** 2) ** 0.5
                if distance < 0.5:  # 約50km
                    return True
        
        return False
    
    def calculate_golden_blue_hours(self, lat: float, lon: float, date: datetime) -> Dict:
        """計算黃金時刻和藍調時刻"""
        if not REQUESTS_AVAILABLE:
            # 預設值
            return {
                "sunrise": "06:00",
                "sunset": "18:00",
                "golden_hour_morning": {"start": "05:30", "end": "07:00"},
                "golden_hour_evening": {"start": "17:00", "end": "18:30"},
                "blue_hour_morning": {"start": "05:00", "end": "05:40"},
                "blue_hour_evening": {"start": "18:20", "end": "19:00"}
            }
            
        try:
            # 取得日出日落時間
            params = {
                "latitude": lat,
                "longitude": lon,
                "date": date.strftime("%Y-%m-%d"),
                "timezone": "auto"
            }
            
            response = requests.get("https://api.sunrise-sunset.org/json", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()["results"]
                
                sunrise_str = data["sunrise"]
                sunset_str = data["sunset"]
                
                # 轉換為datetime物件（需要處理UTC時區）
                sunrise = datetime.fromisoformat(sunrise_str.replace('Z', '+00:00'))
                sunset = datetime.fromisoformat(sunset_str.replace('Z', '+00:00'))
                
                # 計算各種時刻
                golden_hour_morning_start = sunrise - timedelta(minutes=30)
                golden_hour_morning_end = sunrise + timedelta(minutes=60)
                
                golden_hour_evening_start = sunset - timedelta(minutes=60)
                golden_hour_evening_end = sunset + timedelta(minutes=30)
                
                blue_hour_morning_start = sunrise - timedelta(minutes=60)
                blue_hour_morning_end = sunrise - timedelta(minutes=20)
                
                blue_hour_evening_start = sunset + timedelta(minutes=20)
                blue_hour_evening_end = sunset + timedelta(minutes=60)
                
                return {
                    "sunrise": sunrise.strftime("%H:%M"),
                    "sunset": sunset.strftime("%H:%M"),
                    "golden_hour_morning": {
                        "start": golden_hour_morning_start.strftime("%H:%M"),
                        "end": golden_hour_morning_end.strftime("%H:%M")
                    },
                    "golden_hour_evening": {
                        "start": golden_hour_evening_start.strftime("%H:%M"),
                        "end": golden_hour_evening_end.strftime("%H:%M")
                    },
                    "blue_hour_morning": {
                        "start": blue_hour_morning_start.strftime("%H:%M"),
                        "end": blue_hour_morning_end.strftime("%H:%M")
                    },
                    "blue_hour_evening": {
                        "start": blue_hour_evening_start.strftime("%H:%M"),
                        "end": blue_hour_evening_end.strftime("%H:%M")
                    }
                }
            
        except Exception as e:
            print(f"Golden/Blue hour calculation error: {e}")
        
        # 預設值
        return {
            "sunrise": "06:00",
            "sunset": "18:00",
            "golden_hour_morning": {"start": "05:30", "end": "07:00"},
            "golden_hour_evening": {"start": "17:00", "end": "18:30"},
            "blue_hour_morning": {"start": "05:00", "end": "05:40"},
            "blue_hour_evening": {"start": "18:20", "end": "19:00"}
        }

# 實例化全局物件
enhanced_weather = EnhancedWeatherData()