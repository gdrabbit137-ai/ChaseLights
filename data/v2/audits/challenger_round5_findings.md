# Challenger Round 5 (2026-11-08) — adjudication ledger
Coverage: 9 tw south/east cards (三仙台/崇德/七星潭/石梯坪/鵝鑾鼻/龍磐/嘉明湖/北大武/六十石山).
- [TICKETED CL-DATA-33] 崇德清水斷崖山海遠眺 (tw-034-P02) qualifying 21:00–22:00 — no light_window. FIXED on main.
- PENDING AUDIT (no ticket yet, need data verification before ruling): sunrise-family cards show 05:30–06:00 windows in November (三仙台/石梯坪/鵝鑾鼻/帆船鼻/伯朗大道/綠島) — challenger claims local sunrise ~05:47–05:55 so 05:30 is still dawn. Verify against astro layer: is the window astro-computed (sunrise_window condition) or a fixed template? If astro-computed, the 05:30 start may be intentional pre-sunrise blue→sunrise span; decide whether copy mislabels dawn as 日出.
- PENDING OWNER-GATE: 鵝鑾鼻燈塔 card window contradicts park opening hours (~06:30 winter) — park-hours data would be a NEW data source (owner gate); interim mitigation could be an honest 註記 in access_notes (cheap, no new source).
- PENDING AUDIT: 11月 cards still named 銀河 (龍磐/嘉明湖) while galactic core is near horizon — contract has galactic_core_altitude>=10° threshold; check whether core altitude gate is actually enforced for these contracts (may be missing condition → another light-window-class sweep miss).
- PENDING UX NOTE (low): 嘉明湖/北大武 need 2-day treks; a single 1-hour best window is misleading — candidate for an honest 行程限制 note (copy-level).
- NOT A TICKET: 太麻里金針山/瑞穗/專名墾丁 not in catalog — discovery rotation candidates (us/ak/hi next per rotation, but tw-east gap recorded).
