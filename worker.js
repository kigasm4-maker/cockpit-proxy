export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const target = url.searchParams.get('url');

    const ALLOWED = [
      'api.twelvedata.com',
      'api.coingecko.com',
      'api.frankfurter.app',
      'gamma-api.polymarket.com'
    ];

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders() });
    }

    if (!target) {
      return json({ error: 'missing url param' }, 400);
    }

    let targetUrl;
    try {
      targetUrl = new URL(target);
    } catch (e) {
      return json({ error: 'invalid url' }, 400);
    }

    if (!ALLOWED.includes(targetUrl.hostname)) {
      return json({ error: 'domain not allowed' }, 403);
    }

    if (targetUrl.hostname === 'api.twelvedata.com' && env.TD_KEY) {
      targetUrl.searchParams.set('apikey', env.TD_KEY);
    }

    const cacheKey = new Request(targetUrl.toString(), request);
    const cache = caches.default;
    let response = await cache.match(cacheKey);

    if (!response) {
      const upstream = await fetch(targetUrl.toString(), { cf: { cacheTtl: 10 } });
      const body = await upstream.text();
      response = new Response(body, {
        status: upstream.status,
        headers: { ...corsHeaders(), 'Content-Type': 'application/json' }
      });
      response.headers.set('Cache-Control', 's-maxage=10');
      await cache.put(cacheKey, response.clone());
    } else {
      response = new Response(response.body, response);
      Object.entries(corsHeaders()).forEach(([k, v]) => response.headers.set(k, v));
    }

    return response;
  }
};

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...corsHeaders(), 'Content-Type': 'application/json' }
  });
}
