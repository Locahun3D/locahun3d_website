// locahun3d contact form Worker
// - POST /api/contact : send email via Cloudflare Email Routing (send_email binding)
// - everything else  : delegate to static assets

import { EmailMessage } from "cloudflare:email";

const TO_ADDR = "nakamurakou1108@gmail.com";
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
  "script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com https://cdn.jsdelivr.net https://npmcdn.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
  "font-src 'self' https://fonts.gstatic.com data:",
  "img-src 'self' data: blob: https:",
  "media-src 'self' blob:",
  "connect-src 'self' https://challenges.cloudflare.com",
  "frame-src https://challenges.cloudflare.com",
  "frame-ancestors 'none'",
  "form-action 'self'",
  "base-uri 'self'",
  "object-src 'none'",
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

  // delegate everything else to static assets
  return env.ASSETS.fetch(request);
}

export default {
  async fetch(request, env) {
    const response = await route(request, env);
    return withSecurityHeaders(response);
  },
};
