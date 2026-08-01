// Demonstrates conditional-request validators (ETag/If-None-Match,
// Last-Modified/If-Modified-Since), Set-Cookie attribute hygiene, and a CORS
// preflight + simple-request exchange.
// Referenced from 05_Networking_and_OS/CH01_HTTP.md (Section 10).
const http = require('http');
const crypto = require('crypto');

const ALLOWED_ORIGIN = 'https://app.example.com';
const article = {
  id: 7,
  title: 'Understanding Conditional Requests',
  body: 'ETags let a server say "nothing changed" without resending the body.',
  updatedAt: new Date('2026-06-01T12:00:00Z'),
};

function computeEtag(resource) {
  // Strong validator: byte-for-byte hash of the serialized representation.
  const hash = crypto.createHash('sha1').update(JSON.stringify(resource)).digest('hex');
  return `"${hash}"`;
}

function applyCorsHeaders(req, res) {
  const origin = req.headers.origin;
  if (origin === ALLOWED_ORIGIN) {
    res.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Vary', 'Origin');
  }
}

const server = http.createServer((req, res) => {
  applyCorsHeaders(req, res);

  // CORS preflight: browsers send this before a "non-simple" cross-origin
  // request (e.g. one carrying a custom header or using PUT/DELETE).
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With');
    res.setHeader('Access-Control-Max-Age', '600'); // cache the preflight result
    res.writeHead(204);
    return res.end();
  }

  if (req.method === 'GET' && req.url === '/articles/7') {
    const etag = computeEtag(article);
    const lastModified = article.updatedAt.toUTCString();

    // Strong validator wins if present; fall back to Last-Modified otherwise.
    const ifNoneMatch = req.headers['if-none-match'];
    const ifModifiedSince = req.headers['if-modified-since'];
    const notModified =
      ifNoneMatch === etag ||
      (!ifNoneMatch && ifModifiedSince && new Date(ifModifiedSince) >= article.updatedAt);

    res.setHeader('ETag', etag);
    res.setHeader('Last-Modified', lastModified);
    res.setHeader('Cache-Control', 'private, max-age=0, must-revalidate');
    // Session cookie hardened against script access and cross-site leakage.
    res.setHeader('Set-Cookie', [
      `session_id=${crypto.randomUUID()}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=1800`,
    ]);

    if (notModified) {
      res.writeHead(304);
      return res.end();
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify(article));
  }

  res.writeHead(404);
  res.end();
});

server.listen(8081);
