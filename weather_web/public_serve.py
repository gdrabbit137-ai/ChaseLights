"""
ChaseLights — 公開分享啟動器
啟動 Flask 伺服器 + ngrok 隧道，讓其他人可以瀏覽
"""
import os
import sys
import time
import threading
import webbrowser
from pyngrok import ngrok, conf

# 設定 ngrok 配置目錄
import pathlib
NGROK_CONFIG_DIR = pathlib.Path.home() / ".config" / "ngrok"
NGROK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
conf.get_default().config_path = str(NGROK_CONFIG_DIR / "ngrok.yml")

def start_flask():
    """啟動 Flask 應用程式"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from app import app
    # 綁定所有網路介面，讓區域網路也能連線
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    print("╔══════════════════════════════════════════╗")
    print("║ 📷 ChaseLights — 公開分享啟動器         ║")
    print("║                                          ║")
    print("║  正在啟動 Flask 伺服器...                ║")
    print("╚══════════════════════════════════════════╝")
    
    # 在背景執行緒啟動 Flask
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(3)  # 等待 Flask 啟動
    
    print("  ✅ Flask 伺服器已啟動 (http://localhost:5000)")
    print()
    print("  ⏳ 正在建立 ngrok 公開隧道...")
    
    try:
        # 建立 HTTP 隧道
        tunnel = ngrok.connect(5000, domain=None)
        public_url = tunnel.public_url
        
        print(f"  ✅ ngrok 隧道已建立！")
        print()
        print("  ══════════════════════════════════════════")
        print(f"  🌐 公開網址: {public_url}")
        print("  ══════════════════════════════════════════")
        print()
        print(f"  🗺️  能見度地圖: {public_url}")
        print(f"  📋 最佳景點:   {public_url}summary")
        print()
        print("  ⚠️  注意：免費 ngrok 隧道每次啟動網址不同")
        print("       且每分鐘 40 個連線限制")
        print()
        print("  ⏹️  按 Ctrl+C 停止分享")
        print()
        
        # 自動開啟瀏覽器
        try:
            webbrowser.open(public_url)
        except:
            pass
        
        # 保持程式運行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print()
        print("  ⏹️  正在關閉...")
    except Exception as e:
        print(f"  ❌ ngrok 錯誤: {e}")
        print()
        print("  💡 替代方案：請自行下載 ngrok (https://ngrok.com/download)")
        print("     然後執行: ngrok http 5000")
    finally:
        # 清理隧道
        try:
            ngrok.kill()
        except:
            pass
        print("  ✅ 已停止分享")

if __name__ == '__main__':
    main()
