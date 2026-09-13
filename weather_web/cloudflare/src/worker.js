/**
 * PhotoWeather — Cloudflare Worker API Proxy
 * 
 * 架構：
 *   前端 (Cloudflare Pages) → Worker API Proxy → Python 後端 (VPS)
 *                                                      ↓
 *                                               Open-Meteo API
 * 
 * Worker 角色：
 * 1. 代理所有 /api/* 請求到 Python 後端
 * 2. 快取回應 5 分鐘（減少後端負載）
 * 3. 失敗時回傳上次的快取結果（graceful degradation）
 */

// Cloudflare KV 命名空間（用於持久快取）
// 需先在 Cloudflare Dashboard 建立 KV namespace
// const WEATHER_CACHE = caches.default;

// ─── 處理所有傳入請求 ────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const { pathname, search } = url;

    // 只處理 /api/* 路徑
    if (!pathname.startsWith('/api/')) {
      return new Response('Not found', { status: 404 });
    }

    // CORS 頭（允許前端跨域）
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // OPTIONS 預檢請求
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const backendUrl = env.BACKEND_URL || 'http://localhost:5000';
    const targetUrl = `${backendUrl}${pathname}${search}`;

    // 嘗試從快取讀取
    const cacheKey = new Request(targetUrl, request);
    const cache = caches.default;
    const cachedResponse = await cache.match(cacheKey);

    if (cachedResponse) {
      // 快取命中，回傳快取結果
      const resp = new Response(cachedResponse.body, {
        ...cachedResponse,
        headers: { ...cachedResponse.headers, ...corsHeaders },
      });
      resp.headers.set('X-Cache', 'HIT');
      return resp;
    }

    // 代理請求到 Python 後端
    try {
      const backendResponse = await fetch(targetUrl, {
        method: request.method,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'PhotoWeather-CF-Worker',
        },
      });

      if (!backendResponse.ok) {
        throw new Error(`Backend returned ${backendResponse.status}`);
      }

      const responseData = await backendResponse.json();

      // 存入快取 5 分鐘
      const responseToCache = new Response(JSON.stringify(responseData), {
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=300',  // 5 分鐘
          ...corsHeaders,
        },
      });
      ctx.waitUntil(cache.put(cacheKey, responseToCache.clone()));

      // 回傳給前端
      const response = new Response(JSON.stringify(responseData), {
        headers: {
          'Content-Type': 'application/json',
          'X-Cache': 'MISS',
          ...corsHeaders,
        },
      });
      return response;

    } catch (err) {
      console.error(`Proxy error: ${err.message}`);

      // 後端掛掉時，嘗試回傳 stale cache
      const staleCache = await cache.match(cacheKey);
      if (staleCache) {
        const resp = new Response(staleCache.body, {
          ...staleCache,
          headers: { ...staleCache.headers, ...corsHeaders },
        });
        resp.headers.set('X-Cache', 'STALE');
        return resp;
      }

      // 完全沒快取 → 回傳錯誤
      return new Response(JSON.stringify({
        error: '服務暫時不可用',
        message: err.message,
        timestamp: new Date().toISOString(),
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json', ...corsHeaders },
      });
    }
  },
};