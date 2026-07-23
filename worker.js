// locahun3d contact form Worker
// - POST /api/contact : send email via Cloudflare Email Routing (send_email binding)
// - everything else  : delegate to static assets

import { EmailMessage } from "cloudflare:email";

const TO_ADDR = "l3dtools@gmail.com";
const FROM_ADDR = "noreply@locahun3d.com";
const FROM_NAME = "locahun3d Web";

function utf8ToBase64(s) {
  const bytes = new TextEncoder().encode(s);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

function encodeHeaderJa(s) {
  // RFC 2047 base64 encoded-word for non-ASCII headers
  return "=?UTF-8?B?" + utf8ToBase64(s) + "?=";
}

function buildMime({ subject, body, replyTo }) {
  const date = new Date().toUTCString();
  const id = `${Date.now()}.${Math.random().toString(36).slice(2)}@locahun3d.com`;
  const encodedBody = utf8ToBase64(body).replace(/(.{76})/g, "$1\r\n");
  return [
    `From: =?UTF-8?B?${utf8ToBase64(FROM_NAME)}?= <${FROM_ADDR}>`,
    `To: <${TO_ADDR}>`,
    `Reply-To: <${replyTo}>`,
    `Subject: ${encodeHeaderJa(subject)}`,
    `Date: ${date}`,
    `Message-ID: <${id}>`,
    "MIME-Version: 1.0",
    "Content-Type: text/plain; charset=UTF-8",
    "Content-Transfer-Encoding: base64",
    "",
    encodedBody,
  ].join("\r\n");
}

function jsonResponse(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

function isEmail(s) {
  return typeof s === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

// ── Clerk config ──
const CLERK_ISSUER = "https://clerk.locahun3d.com";
const ADMIN_EMAILS = new Set(["nakamurakou1108@gmail.com", "l3dtools@gmail.com"]);

let _jwksCache = null;
let _jwksCacheTime = 0;
const JWKS_TTL = 3600_000; // 1 hour

async function getJWKS() {
  if (_jwksCache && Date.now() - _jwksCacheTime < JWKS_TTL) return _jwksCache;
  const res = await fetch(`${CLERK_ISSUER}/.well-known/jwks.json`);
  if (!res.ok) throw new Error("Failed to fetch JWKS");
  _jwksCache = await res.json();
  _jwksCacheTime = Date.now();
  return _jwksCache;
}

function base64UrlDecode(str) {
  str = str.replace(/-/g, "+").replace(/_/g, "/");
  while (str.length % 4) str += "=";
  return Uint8Array.from(atob(str), c => c.charCodeAt(0));
}

async function importJWK(jwk) {
  return crypto.subtle.importKey(
    "jwk", jwk,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["verify"]
  );
}

async function verifyClerkJWT(token) {
  try {
    const [headerB64, payloadB64, sigB64] = token.split(".");
    if (!headerB64 || !payloadB64 || !sigB64) return null;

    const header = JSON.parse(new TextDecoder().decode(base64UrlDecode(headerB64)));
    const jwks = await getJWKS();
    const jwk = jwks.keys.find(k => k.kid === header.kid);
    if (!jwk) return null;

    const key = await importJWK(jwk);
    const data = new TextEncoder().encode(`${headerB64}.${payloadB64}`);
    const sig = base64UrlDecode(sigB64);
    const valid = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, sig, data);
    if (!valid) return null;

    const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadB64)));
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload;
  } catch {
    return null;
  }
}

async function getClerkUser(request) {
  const auth = request.headers.get("Authorization") || "";
  if (auth.startsWith("Bearer ")) {
    const result = await verifyClerkJWT(auth.slice(7));
    if (result) return result;
  }
  const cookie = request.headers.get("Cookie") || "";
  const match = cookie.match(/__session=([^;]+)/);
  if (!match) return null;
  return verifyClerkJWT(match[1]);
}

function isAdmin(clerkPayload) {
  if (!clerkPayload) return false;
  const email = clerkPayload.email ||
    clerkPayload.primary_email_address ||
    (clerkPayload.email_addresses && clerkPayload.email_addresses[0]);
  return email && ADMIN_EMAILS.has(email);
}

// ── Works article gating ──
async function getArticleMeta(slug, env) {
  const val = await env.WORKS_KV.get(`works:${slug}`, "json");
  return val || { status: "published" };
}

async function handleWorksArticle(request, env, slug) {
  const meta = await getArticleMeta(slug, env);
  const url = new URL(request.url);

  if (meta.status === "published") {
    return env.ASSETS.fetch(request);
  }

  if (meta.status === "private" && meta.shareToken) {
    const token = url.searchParams.get("token");
    if (token === meta.shareToken) {
      return env.ASSETS.fetch(request);
    }
  }

  if (meta.status === "draft" || meta.status === "private") {
    const user = await getClerkUser(request);
    if (isAdmin(user)) {
      return env.ASSETS.fetch(request);
    }
  }

  return new Response("Not Found", { status: 404, headers: { "Content-Type": "text/plain" } });
}

// ── Works Admin API ──
async function handleWorksAPI(request, env) {
  const user = await getClerkUser(request);
  if (!isAdmin(user)) {
    return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
  }

  const url = new URL(request.url);
  const path = url.pathname;

  // GET /api/works — list all articles
  if (request.method === "GET" && path === "/api/works") {
    const list = await env.WORKS_KV.list({ prefix: "works:" });
    const articles = [];
    for (const key of list.keys) {
      const meta = await env.WORKS_KV.get(key.name, "json");
      articles.push({ slug: key.name.replace("works:", ""), ...meta });
    }
    return jsonResponse({ ok: true, articles });
  }

  // PUT /api/works/:slug — update article
  if (request.method === "PUT") {
    const match = path.match(/^\/api\/works\/([a-z0-9_-]+)$/);
    if (!match) return jsonResponse({ ok: false, error: "Invalid slug" }, 400);
    const slug = match[1];
    let body;
    try { body = await request.json(); } catch { return jsonResponse({ ok: false, error: "Invalid JSON" }, 400); }
    const status = body.status;
    if (!["published", "draft", "private"].includes(status)) {
      return jsonResponse({ ok: false, error: "Invalid status" }, 400);
    }
    const existing = await getArticleMeta(slug, env);
    const updated = { ...existing, status };
    if (status === "private" && !updated.shareToken) {
      updated.shareToken = crypto.randomUUID().replace(/-/g, "").slice(0, 16);
    }
    if (status !== "private") {
      updated.shareToken = null;
    }
    await env.WORKS_KV.put(`works:${slug}`, JSON.stringify(updated));
    return jsonResponse({ ok: true, article: { slug, ...updated } });
  }

  // POST /api/works/:slug/regenerate-token
  if (request.method === "POST") {
    const match = path.match(/^\/api\/works\/([a-z0-9_-]+)\/regenerate-token$/);
    if (!match) return jsonResponse({ ok: false, error: "Not found" }, 404);
    const slug = match[1];
    const existing = await getArticleMeta(slug, env);
    if (existing.status !== "private") {
      return jsonResponse({ ok: false, error: "Article not private" }, 400);
    }
    existing.shareToken = crypto.randomUUID().replace(/-/g, "").slice(0, 16);
    await env.WORKS_KV.put(`works:${slug}`, JSON.stringify(existing));
    return jsonResponse({ ok: true, article: { slug, ...existing } });
  }

  return jsonResponse({ ok: false, error: "Not found" }, 404);
}

const ALLOWED_ORIGINS = new Set([
  "https://web.locahun3d.com",
  "https://locahun3d.com",
  "https://locahun3dwebsite.nakamurakou1108.workers.dev",
]);

// silently look successful to bots — they won't retry / learn
const BOT_SILENT_OK = () => jsonResponse({ ok: true });

async function handleContact(request, env) {
  // --- 1. Origin / Referer check ---
  const origin = request.headers.get("Origin") || "";
  const referer = request.headers.get("Referer") || "";
  const fromAllowed =
    (origin && ALLOWED_ORIGINS.has(origin)) ||
    (!origin && [...ALLOWED_ORIGINS].some(o => referer.startsWith(o + "/")));
  if (!fromAllowed) {
    return jsonResponse({ ok: false, error: "Forbidden origin" }, 403);
  }

  // --- 2. Payload size check ---
  const contentLength = parseInt(request.headers.get("Content-Length") || "0", 10);
  if (contentLength > 50 * 1024) {
    return jsonResponse({ ok: false, error: "Request too large" }, 413);
  }

  let data;
  try {
    data = await request.json();
  } catch {
    return jsonResponse({ ok: false, error: "リクエストが不正です" }, 400);
  }

  // --- 3. Honeypot field (hidden in HTML) ---
  // If a bot filled this, pretend success and bail
  if (data.website && String(data.website).trim() !== "") {
    return BOT_SILENT_OK();
  }

  // --- 3b. Cloudflare Turnstile token verification ---
  if (env.TURNSTILE_SECRET) {
    const token = (data.cf_turnstile_token || "").toString();
    if (!token) {
      return jsonResponse({ ok: false, error: "認証トークンがありません。ページを再読み込みのうえ再度お試しください。" }, 400);
    }
    const formData = new FormData();
    formData.append("secret", env.TURNSTILE_SECRET);
    formData.append("response", token);
    formData.append("remoteip", request.headers.get("CF-Connecting-IP") || "");
    try {
      const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
        method: "POST",
        body: formData,
      });
      const result = await verify.json();
      if (!result.success) {
        // bot or expired token — silent OK pattern to avoid leaking detection logic
        return BOT_SILENT_OK();
      }
    } catch {
      return jsonResponse({ ok: false, error: "認証サーバーに到達できませんでした。時間をおいて再度お試しください。" }, 503);
    }
  }

  // --- 4. Time-on-page guard (humans need ≥ 3s to fill the form) ---
  const formOpenedAt = Number(data._t) || 0;
  if (formOpenedAt > 0) {
    const elapsedMs = Date.now() - formOpenedAt;
    if (elapsedMs < 3000) {
      // suspiciously fast — likely a bot
      return BOT_SILENT_OK();
    }
    if (elapsedMs > 24 * 60 * 60 * 1000) {
      // stale form (24h+) — re-submit replay attempt
      return jsonResponse({ ok: false, error: "ページを再読み込みのうえ再度お試しください" }, 400);
    }
  }

  const name = (data.name || "").toString().trim();
  const company = (data.company || "").toString().trim();
  const email = (data.email || "").toString().trim();
  const phone = (data.phone || "").toString().trim();
  const subject = (data.subject || "").toString().trim();
  const message = (data.message || "").toString().trim();

  if (!name) return jsonResponse({ ok: false, error: "お名前を入力してください" }, 400);
  if (!isEmail(email)) return jsonResponse({ ok: false, error: "メールアドレスを正しく入力してください" }, 400);
  if (!message) return jsonResponse({ ok: false, error: "ご用件を入力してください" }, 400);
  if (message.length > 5000) return jsonResponse({ ok: false, error: "本文が長すぎます (5000 文字以内)" }, 400);

  // --- 5. Content sanity: reject if message has >5 URLs (typical spam pattern) ---
  const urlCount = (message.match(/https?:\/\//gi) || []).length;
  if (urlCount > 5) return BOT_SILENT_OK();

  const bodyText = [
    "【ロケハン3D Web からの問い合わせ】",
    "",
    `■ お名前: ${name}`,
    `■ 会社名: ${company || "—"}`,
    `■ メール: ${email}`,
    `■ 電話番号: ${phone || "—"}`,
    `■ 種別: ${subject || "—"}`,
    "",
    "──── ご用件 ────",
    message,
    "",
    "──────────────",
    `送信元: ${request.headers.get("CF-Connecting-IP") || "-"}`,
    `User-Agent: ${request.headers.get("User-Agent") || "-"}`,
  ].join("\n");

  const mailSubject = `【ロケハン3D】${subject || "お問い合わせ"} - ${name}様`;

  const raw = buildMime({
    subject: mailSubject,
    body: bodyText,
    replyTo: email,
  });

  try {
    const msg = new EmailMessage(FROM_ADDR, TO_ADDR, raw);
    await env.MAIL.send(msg);
  } catch (err) {
    return jsonResponse(
      { ok: false, error: "送信処理でエラーが発生しました。お手数ですが時間をおいて再度お試しください。" },
      500
    );
  }

  return jsonResponse({ ok: true });
}

// HTTP security headers — applied to all responses via withSecurityHeaders()
// CSP allowlist matches actual external resources used by the site:
//   - Google Fonts (CSS + woff2)
//   - jsdelivr (flatpickr CSS + JS on demo page)
//   - npmcdn (flatpickr ja locale)
//   - challenges.cloudflare.com (Turnstile)
const CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com https://cdn.jsdelivr.net https://npmcdn.com https://clerk.locahun3d.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://clerk.locahun3d.com",
  "font-src 'self' https://fonts.gstatic.com data:",
  "img-src 'self' data: blob: https: https://img.clerk.com",
  "media-src 'self' blob:",
  "connect-src 'self' https://challenges.cloudflare.com https://clerk.locahun3d.com https://accounts.locahun3d.com",
  "frame-src https://challenges.cloudflare.com https://www.youtube-nocookie.com https://clerk.locahun3d.com",
  "frame-ancestors 'none'",
  "form-action 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "worker-src 'self' blob:",
  "upgrade-insecure-requests",
].join("; ");

const SECURITY_HEADERS = {
  "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()",
  "X-Frame-Options": "DENY",
  "Cross-Origin-Opener-Policy": "same-origin",
  "Content-Security-Policy": CSP,
};

function withSecurityHeaders(response) {
  const headers = new Headers(response.headers);
  for (const [k, v] of Object.entries(SECURITY_HEADERS)) {
    headers.set(k, v);
  }
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

async function route(request, env) {
  const url = new URL(request.url);

  // 301 redirect: root / and /index.html → /locahun3d_manifesto.html
  if (url.pathname === "/" || url.pathname === "/index.html") {
    return Response.redirect(`${url.origin}/locahun3d_manifesto.html`, 301);
  }

  // EN mirror: /en, /en/ → English home (manifesto)
  if (url.pathname === "/en" || url.pathname === "/en/" || url.pathname === "/en/index.html") {
    return Response.redirect(`${url.origin}/en/locahun3d_manifesto.html`, 301);
  }
  // EN contact merged into EN demo page
  if (url.pathname === "/en/locahun3d_contact.html") {
    return Response.redirect(`${url.origin}/en/locahun3d_demo.html#contact`, 301);
  }

  // 301 redirect: former contact page merged into demo page
  if (url.pathname === "/locahun3d_contact.html") {
    return Response.redirect(`${url.origin}/locahun3d_demo.html#contact`, 301);
  }

  if (url.pathname === "/api/contact") {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }
    if (request.method !== "POST") {
      return jsonResponse({ ok: false, error: "POST only" }, 405);
    }
    return handleContact(request, env);
  }

  // Works Admin API
  if (url.pathname.startsWith("/api/works")) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }
    return handleWorksAPI(request, env);
  }

  // Works article gating — intercept individual article pages (JP + EN share one KV entry per slug)
  const worksMatch = url.pathname.match(/^(?:\/en)?\/works\/([a-z0-9_-]+)\.html$/);
  if (worksMatch && worksMatch[1] !== "index" && worksMatch[1] !== "blog" && worksMatch[1] !== "admin") {
    return handleWorksArticle(request, env, worksMatch[1]);
  }

  // delegate everything else to static assets
  return env.ASSETS.fetch(request);
}

export default {
  async fetch(request, env) {
    const response = await route(request, env);
    return withSecurityHeaders(response);
  },
};
