// Minimal HTTP server demonstrating method dispatch and status-code semantics.
// Referenced from 05_Networking_and_OS/CH01_HTTP.md (Section 10).
const http = require('http');

const products = new Map([[42, { id: 42, name: 'Widget' }]]);

const server = http.createServer((req, res) => {
  const match = req.url.match(/^\/product\/(\d+)$/);
  const id = match ? Number(match[1]) : null;

  if (req.method === 'GET' && id !== null) {
    const product = products.get(id);
    if (!product) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ error: 'not found' }));
    }
    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=60',
      ETag: `"${product.id}-v1"`,
    });
    return res.end(JSON.stringify(product));
  }

  if (req.method === 'PUT' && id !== null) {
    // PUT is idempotent: replacing with the same body repeatedly is safe.
    let raw = '';
    req.on('data', (chunk) => { raw += chunk; });
    req.on('end', () => {
      products.set(id, JSON.parse(raw));
      res.writeHead(204);
      res.end();
    });
    return;
  }

  res.writeHead(405, { Allow: 'GET, PUT' });
  res.end();
});

server.listen(8080);
