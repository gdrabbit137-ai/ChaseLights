# 🚀 PhotoWeather 上線部署指南

> 推薦方案：**DigitalOcean $6/月 + Cloudflare CDN**

---

## 🏆 推薦的上線方案

```
                 使用者瀏覽器
                      │
                      ▼
     ┌────────────────────────────────┐
     │   Cloudflare CDN (全球節點)     │  ← 免費，加速全球連線
     │   + Cloudflare Workers API      │  ← 免費，100k req/天
     └────────┬───────────────────────┘
              │
     ┌────────┴───────────────────────┐
     │   VPS: DigitalOcean $6/月       │  ← Python Flask 後端
     │   - Waitress 生產伺服器         │
     │   - 每小時自動更新天氣資料       │
     └────────────────────────────────┘
```

## 每月成本估算

| 項目 | 規格 | 費用 |
|------|------|:----:|
| **VPS** | DigitalOcean 基本方案 (1GB RAM, 25GB SSD) | **$6/月** |
| **Cloudflare** | CDN + Workers 免費方案 | **$0/月** |
| **Open-Meteo** | 免費方案 (10,000次/天) | **$0/月** |
| **網域** | 自訂網域 (可省略用 Cloudflare 提供的網域) | $0-10/月 |
| **總計** | | **$6~16/月** |

## 部署步驟

### Step 1️⃣ 購買 VPS

```bash
# 用 DigitalOcean 或 Linode 或 Vultr
# 最低方案：1 vCPU, 1GB RAM, 25GB SSD ($6/月)
# 選擇離台灣最近的機房：Singapore 或 Tokyo
```

### Step 2️⃣ 在 VPS 上部署 Python 後端

```bash
# SSH 進入 VPS
ssh root@你的VPS_IP

# 安裝 Python + git
apt update && apt install -y python3 python3-pip git

# 複製專案（從你的 GitHub）
git clone https://github.com/你的帳號/PhotoWeather.git
cd PhotoWeather

# 安裝依賴
pip3 install flask requests waitress

# 啟動 Waitress 生產伺服器
python3 -c "
from waitress import serve
from weather_web.app import app
serve(app, host='0.0.0.0', port=5000, threads=4)
"
```

### Step 3️⃣ 設定自動排程 (每小時更新資料)

```bash
# 將 scheduler.py 複製到 VPS
# 建立 systemd service（scheduler.py 已支援）
sudo python3 weather_web/scheduler.py install-linux
# 照印出的指示設定
```

### Step 4️⃣ 設定 Cloudflare

```bash
# 1. 註冊 Cloudflare 帳號 (免費)
# 2. 將你的網域 DNS 交給 Cloudflare 管理
# 3. 安裝 wrangler CLI:
npm install -g wrangler

# 4. 登入 Cloudflare
wrangler login

# 5. 部署 API Worker
cd weather_web/cloudflare
wrangler deploy

# 6. 部署前端 Pages
wrangler pages deploy ../templates/ --name=photoweather
```

### Step 5️⃣ 啟動排程（在本機或 VPS）

```bash
# Windows: 用工作排程器
# 以系統管理員執行:
python weather_web/scheduler.py install-windows

# Linux: 用 systemd
# 或用簡單背景程序:
nohup python weather_web/scheduler.py loop &
```

---

## 架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare  (全球 CDN)                    │
│  ┌─────────────────────┐   ┌────────────────────────────┐   │
│  │ Pages (靜態前端)    │   │ API Worker (代理/快取)     │   │
│  │ index.html          │   │  /api/forecast             │   │
│  │ summary.html        │   │  /api/best-spots           │   │
│  │ style.css           │   │  /api/refresh              │   │
│  └────────┬────────────┘   └────────┬───────────────────┘   │
└───────────┼─────────────────────────┼───────────────────────┘
            │                         │
            │  Cloudflare Tunnel      │  HTTPS
            │  (或直接暴露 5000 port) │
            ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  VPS (DigitalOcean $6/月)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Waitress WSGI 伺服器 (4 threads)                    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Flask App (app.py)                        │    │   │
│  │  │  • 讀取快取 JSON                           │    │   │
│  │  │  • 計算今日最佳景點評分                       │    │   │
│  │  │  • 回傳 API 回應                           │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                     │   │
│  │  ⏰ 每小時執行 scheduler.py                          │   │
│  │  └→ build_cache.py → 164次API呼叫→寫入快取            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 注意事項

| 問題 | 解法 |
|------|------|
| **VPS 費用** | $6/月是最低方案，若預算考量可先用 **Railway 免費層** 或 **Fly.io** |
| **API 呼叫限制** | Open-Meteo 每天約 10,000 次免費，164次 × 24小時 = **3,936次/天**，還在限制內 ✅ |
| **SSL 憑證** | Cloudflare 自動提供 HTTPS，不需自己處理 |
| **後端掛掉** | Cloudflare Worker 會回傳上次的快取，前端仍可正常顯示 |
| **資料延遲** | 每小時更新一次，最差情況資料可能落後 1 小時 |

---

## 目前的檔案結構（已就緒）

```
weather_web/
├── app.py                  ✅ 已支援 API_BASE 環境變數
├── scheduler.py            ✅ 三個模式: loop / once / install
├── build_cache.py          ✅ 資料更新器
├── cloudflare/
│   ├── wrangler.toml       ✅ Cloudflare Workers 設定
│   ├── pages.toml          ✅ Cloudflare Pages 設定
│   └── src/
│       └── worker.js       ✅ API Proxy Worker (快取+容錯)
└── templates/
    ├── index.html          ✅ 支援 API_BASE 變數
    └── summary.html        ✅ 支援 API_BASE 變數
```