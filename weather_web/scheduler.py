"""
ChaseLights — 自動排程更新器
每小時自動執行 build_cache.py 更新天氣資料
支援 Windows (Task Scheduler) 和 Linux (systemd/cron) 兩種模式
"""

import os, sys, time, subprocess, json, logging
from datetime import datetime
from pathlib import Path

# ─── 設定 ───────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
BUILD_CACHE = Path(__file__).resolve().parent / "build_cache.py"
LOG_DIR = Path(__file__).resolve().parent / ".logs"
HOURS_BETWEEN_RUNS = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def run_build_cache():
    """執行一次 build_cache.py"""
    start = time.time()
    logging.info("🔄 開始更新天氣資料...")
    result = subprocess.run(
        [sys.executable, str(BUILD_CACHE)],
        capture_output=True, text=True, timeout=120,
        cwd=str(PROJECT_DIR),
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        points = 0
        for line in result.stdout.split("\n"):
            if "Done" in line:
                parts = line.split()
                for p in parts:
                    if p.isdigit():
                        points = int(p)
                        break
        logging.info(f"✅ 更新完成 ({elapsed:.1f}s) — {points} 個資料點")
    else:
        logging.error(f"❌ 更新失敗 ({elapsed:.1f}s): {result.stderr[-200:]}")
    return result.returncode == 0


def create_windows_task():
    """建立 Windows 工作排程器任務"""
    task_name = "ChaseLights-DataRefresh"
    script_path = sys.executable
    args = f'"{BUILD_CACHE}"'
    working_dir = str(PROJECT_DIR)
    
    # 用 schtasks 建立每小時任務
    cmd = (
        f'schtasks /Create /SC HOURLY /TN "{task_name}" '
        f'/TR "{script_path} {args}" '
        f'/ST 00:00 /F'
    )
    print(f"若要建立 Windows 排程，請以系統管理員執行：")
    print(f"  {cmd}")
    print(f"\n或手動：工作排程器 → 建立基本工作 → 觸發器:每小時 → 動作:啟動程式")
    print(f"  程式: {script_path}")
    print(f"  引數: {args}")
    print(f"  起始位置: {working_dir}")


def create_linux_service():
    """建立 Linux systemd service + timer"""
    service_content = """[Unit]
Description=ChaseLights Data Refresh Service
After=network.target

[Service]
Type=oneshot
ExecStart={python} {script}
WorkingDirectory={workdir}
User={user}

[Install]
WantedBy=multi-user.target
"""
    timer_content = """[Unit]
Description=Run ChaseLights refresh every hour

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
"""
    print("Linux systemd 設定：")
    print()
    print(f"/etc/systemd/system/chaselights-refresh.service:")
    print(service_content.format(
        python=sys.executable,
        script=BUILD_CACHE,
        workdir=PROJECT_DIR,
        user=os.getenv("USER", "nobody"),
    ))
    print()
    print("/etc/systemd/system/chaselights-refresh.timer:")
    print(timer_content)
    print()
    print("啟用：")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable --now chaselights-refresh.timer")


def loop_mode():
    """簡易迴圈模式：適合長時間執行的背景程序，每日00/06/12/18更新"""
    logging.info(f"🚀 ChaseLights 自動排程啟動")
    logging.info(f"   每日 00:00 / 06:00 / 12:00 / 18:00 更新")
    logging.info(f"   快取目錄: {PROJECT_DIR / 'weather_web' / '.cache'}")
    
    # 啟動時先執行一次
    run_build_cache()
    
    while True:
        now = datetime.now()
        next_hour = ((now.hour // 6) + 1) * 6
        next_run = now.replace(hour=next_hour % 24, minute=0, second=0, microsecond=0)
        if next_hour >= 24:
            next_run += timedelta(days=1)
            next_run = next_run.replace(hour=0)
        sleep_sec = (next_run - now).total_seconds()
        logging.info(f"  ⏰ 下次更新: {next_run.strftime('%Y-%m-%d %H:%M')}（等待 {int(sleep_sec//3600)}hr {int(sleep_sec%3600//60)}min）")
        time.sleep(sleep_sec)
        run_build_cache()


if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "loop"
    
    if mode == "loop":
        loop_mode()
    elif mode == "install-windows":
        create_windows_task()
    elif mode == "install-linux":
        create_linux_service()
    elif mode == "once":
        run_build_cache()
    else:
        print(f"用法: python {__file__} [loop|once|install-windows|install-linux]")
        print(f"  loop            — 每小時自動更新（預設，建議用於背景執行）")
        print(f"  once            — 只執行一次")
        print(f"  install-windows — 顯示 Windows 排程設定")
        print(f"  install-linux   — 顯示 Linux systemd 設定")