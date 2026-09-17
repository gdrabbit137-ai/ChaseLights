"""
ChaseLights v0.2 - 資料庫模組
提供使用者系統、收藏、評論等功能
"""
import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "chaselights.db")

def init_database():
    """初始化資料庫表格"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 使用者表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            preferences TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 收藏表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            spot_name TEXT NOT NULL,
            region TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 景點評論表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spot_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            spot_name TEXT NOT NULL,
            region TEXT NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            weather_conditions TEXT,
            photo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 使用者上傳作品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            spot_name TEXT NOT NULL,
            region TEXT NOT NULL,
            image_url TEXT NOT NULL,
            description TEXT,
            camera_settings TEXT,
            weather_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 天氣歷史記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_name TEXT NOT NULL,
            region TEXT NOT NULL,
            date TEXT NOT NULL,
            weather_data TEXT NOT NULL,
            score INTEGER,
            best_genre TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """取得資料庫連接"""
    return sqlite3.connect(DB_PATH)

def create_user(username, email=None, preferences=None):
    """創建新使用者"""
    conn = get_connection()
    cursor = conn.cursor()
    
    preferences_json = json.dumps(preferences or {})
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, preferences)
            VALUES (?, ?, ?)
        ''', (username, email, preferences_json))
        
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user(user_id=None, username=None):
    """取得使用者資訊"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    elif username:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    else:
        return None
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'preferences': json.loads(user[3]),
            'created_at': user[4]
        }
    return None

def add_favorite(user_id, spot_name, region):
    """新增收藏景點"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 檢查是否已收藏
    cursor.execute('''
        SELECT id FROM user_favorites 
        WHERE user_id = ? AND spot_name = ? AND region = ?
    ''', (user_id, spot_name, region))
    
    if cursor.fetchone():
        conn.close()
        return False  # 已收藏
    
    cursor.execute('''
        INSERT INTO user_favorites (user_id, spot_name, region)
        VALUES (?, ?, ?)
    ''', (user_id, spot_name, region))
    
    conn.commit()
    conn.close()
    return True

def remove_favorite(user_id, spot_name, region):
    """移除收藏景點"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM user_favorites 
        WHERE user_id = ? AND spot_name = ? AND region = ?
    ''', (user_id, spot_name, region))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_user_favorites(user_id):
    """取得使用者收藏列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT spot_name, region, created_at FROM user_favorites 
        WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    
    favorites = cursor.fetchall()
    conn.close()
    
    return [{'spot_name': f[0], 'region': f[1], 'created_at': f[2]} for f in favorites]

def add_review(user_id, spot_name, region, rating, comment=None, weather_conditions=None, photo_url=None):
    """新增景點評論"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO spot_reviews (user_id, spot_name, region, rating, comment, weather_conditions, photo_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, spot_name, region, rating, comment, weather_conditions, photo_url))
    
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return review_id

def get_spot_reviews(spot_name, region, limit=10):
    """取得景點評論"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, u.username FROM spot_reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.spot_name = ? AND r.region = ?
        ORDER BY r.created_at DESC LIMIT ?
    ''', (spot_name, region, limit))
    
    reviews = cursor.fetchall()
    conn.close()
    
    result = []
    for r in reviews:
        result.append({
            'id': r[0],
            'rating': r[4],
            'comment': r[5],
            'weather_conditions': r[6],
            'photo_url': r[7],
            'created_at': r[8],
            'username': r[9]
        })
    
    return result

def save_weather_history(spot_name, region, date, weather_data, score, best_genre):
    """儲存天氣歷史記錄"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 檢查是否已存在該日期的記錄
    cursor.execute('''
        SELECT id FROM weather_history 
        WHERE spot_name = ? AND region = ? AND date = ?
    ''', (spot_name, region, date))
    
    if cursor.fetchone():
        # 更新現有記錄
        cursor.execute('''
            UPDATE weather_history 
            SET weather_data = ?, score = ?, best_genre = ?
            WHERE spot_name = ? AND region = ? AND date = ?
        ''', (json.dumps(weather_data), score, best_genre, spot_name, region, date))
    else:
        # 新增記錄
        cursor.execute('''
            INSERT INTO weather_history (spot_name, region, date, weather_data, score, best_genre)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (spot_name, region, date, json.dumps(weather_data), score, best_genre))
    
    conn.commit()
    conn.close()

def get_weather_history(spot_name, region, days=30):
    """取得天氣歷史記錄"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, weather_data, score, best_genre FROM weather_history
        WHERE spot_name = ? AND region = ?
        ORDER BY date DESC LIMIT ?
    ''', (spot_name, region, days))
    
    history = cursor.fetchall()
    conn.close()
    
    result = []
    for h in history:
        result.append({
            'date': h[0],
            'weather_data': json.loads(h[1]),
            'score': h[2],
            'best_genre': h[3]
        })
    
    return result

# 初始化資料庫
if __name__ == "__main__":
    init_database()
    print("資料庫初始化完成")