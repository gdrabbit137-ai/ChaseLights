#!/usr/bin/env python3
"""
PhotoWeather v0.2 測試啟動版本
"""
import json, os, sys
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, jsonify, request, session
import secrets

# 添加當前目錄到路徑
REGIONS_DIR = os.path.dirname(os.path.abspath(__file__))
if REGIONS_DIR not in sys.path:
    sys.path.insert(0, REGIONS_DIR)

from regions import REGIONS

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 嘗試導入新模組，如果失敗使用最小功能
try:
    from database import init_database
    init_database()
    DATABASE_AVAILABLE = True
    print("✓ 資料庫模組載入成功")
except Exception as e:
    DATABASE_AVAILABLE = False
    print(f"⚠ 資料庫模組載入失敗: {e}")

try:
    from enhanced_weather import enhanced_weather
    ENHANCED_WEATHER_AVAILABLE = True
    print("✓ 增強天氣模組載入成功")
except Exception as e:
    ENHANCED_WEATHER_AVAILABLE = False
    print(f"⚠ 增強天氣模組載入失敗: {e}")

try:
    from smart_recommendations import recommendation_engine
    RECOMMENDATIONS_AVAILABLE = True
    print("✓ 智慧推薦模組載入成功")
except Exception as e:
    RECOMMENDATIONS_AVAILABLE = False
    print(f"⚠ 智慧推薦模組載入失敗: {e}")

@app.route("/")
def home():
    """首頁"""
    return render_template("home.html")

@app.route("/summary")
def summary():
    """v0.2 增強版景點摘要頁"""
    region = request.args.get("region", "tw") or "tw"
    # 如果有新模版就用新的，否則用舊的
    try:
        return render_template("summary_v2.html", region=region)
    except:
        return render_template("summary.html", region=region)

@app.route("/weather-guide")
def weather_guide():
    """天氣對策指南頁"""
    return render_template("weather_guide.html")

# 簡化的 API 路由
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    """簡化版登入"""
    if not DATABASE_AVAILABLE:
        return jsonify({"error": "資料庫不可用"}), 503
    
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({"error": "使用者名稱不能為空"}), 400
    
    # 簡化版：直接設定 session
    session['user_id'] = 1
    session['username'] = username
    
    return jsonify({
        "success": True,
        "user": {
            "id": 1,
            "username": username,
            "preferences": {}
        }
    })

@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    """登出"""
    session.clear()
    return jsonify({"success": True})

@app.route("/api/auth/profile")
def api_profile():
    """使用者資料"""
    if 'user_id' not in session:
        return jsonify({"error": "未登入"}), 401
    
    return jsonify({
        "user": {
            "id": session['user_id'],
            "username": session['username'],
            "preferences": {}
        }
    })

# 導入原有的 API 路由
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")

@app.route("/api/best-spots")
def api_best_spots():
    """最佳景點 API (原有功能)"""
    region = request.args.get("region", "tw") or "tw"
    if region not in REGIONS:
        return jsonify({"error": "Invalid region"}), 400
    
    try:
        cache_file = os.path.join(CACHE_DIR, f"forecast_{region}.json")
        if not os.path.exists(cache_file):
            return jsonify({"error": "Weather data not available"}), 404
        
        # 簡化版：返回空資料避免複雜運算
        return jsonify({
            "today": [],
            "tomorrow": [],
            "dayafter": []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/update-status")
def api_update_status():
    """更新狀態 API"""
    try:
        status_file = os.path.join(CACHE_DIR, "update_status.json")
        if os.path.exists(status_file):
            with open(status_file, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        else:
            return jsonify({})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════╗
║  📷 PhotoWeather v0.2 (測試版)           ║
║                                          ║
║  🌐 http://localhost:5000                ║
║     → 首頁 (地區選單)                    ║
║  📋 http://localhost:5000/summary        ║
║     → 景點摘要頁                         ║
║                                          ║
║  ✨ v0.2 新功能測試中...                 ║
╚══════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=5000, debug=True)