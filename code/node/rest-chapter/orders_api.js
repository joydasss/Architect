// Minimal REST orders API demonstrating status codes, Location, and ETag concurrency.
// Referenced from 08_API_Architecture/CH01_REST.md (Section 10).
const http = require('http');

const orders = new Map([[42, { id: 42, status: 'pending', version: 1 }]]);
let nextId = 43;

function send(res, status, payload, extraHeaders = {}) {
  res.writeHead(status, { 'Content-Type': 'application/json', ...extraHeaders });
  res.end(payload === undefined ? undefined : JSON.stringify(payload));
}

const server = http.createServer((req, res) => {
  const match = req.url.match(/^\/orders\/(\d+)$/);

  if (req.method === 'POST' && req.url === '/orders') {
    const id = nextId++;
    const order = { id, status: 'pending', version: 1 };
    orders.set(id, order);
    return send(res, 201, order, { Location: `/orders/${id}` });
  }

  if (req.method === 'GET' && match) {
    const order = orders.get(Number(match[1]));
    if (!order) return send(res, 404, { error: 'not found' });
    const etag = `"${order.id}-v${order.version}"`;
    if (req.headers['if-none-match'] === etag) {
      res.writeHead(304);
      return res.end();
    }
    return send(res, 200, order, { ETag: etag });
  }

  if (req.method === 'PUT' && match) {
    const order = orders.get(Number(match[1]));
    if (!order) return send(res, 404, { error: 'not found' });
    const expectedEtag = `"${order.id}-v${order.version}"`;
    if (req.headers['if-match'] !== expectedEtag) {
      // Optimistic concurrency: reject stale writes.
      return send(res, 409, { error: 'version conflict' });
    }
    let raw = '';
    req.on('data', (chunk) => { raw += chunk; });
    req.on('end', () => {
      const body = JSON.parse(raw);
      order.status = body.status;
      order.version += 1;
      send(res, 200, order);
    });
    return;
  }

  send(res, 404, { error: 'not found' });
});

server.listen(8082);
