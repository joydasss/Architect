const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const { executeLibrary } = require('./schema_and_resolvers');
const { executeDashboard } = require('./request_scoped_dataloader');
const { encodeCursor, executeProducts } = require('./cursor_pagination_and_errors');
const { checkBudget, executePersisted } = require('./persisted_query');
const { parse } = require('graphql');

test('schema validates selections, resolves nested fields, and guards mutation', async () => {
  const allowed = await executeLibrary('{ book(id: "b-1") { title author { name } } }');
  assert.equal(allowed.data.book.author.name, 'N. K. Jemisin');

  const denied = await executeLibrary(`mutation {
    createBook(input: { title: "New", format: DIGITAL, authorId: "a-1" }) { id }
  }`);
  assert.equal(denied.errors[0].extensions.code, 'FORBIDDEN', JSON.stringify(denied));

  const invalid = await executeLibrary('{ book(id: "b-1") { missingField } }');
  assert.ok(invalid.errors[0].message.includes('Cannot query field'));
});

test('request-scoped DataLoader batches many seller fields into one call', async () => {
  const { result, batchCalls } = await executeDashboard();
  assert.equal(result.data.products.length, 40);
  assert.equal(batchCalls, 1);
  assert.equal(result.data.products[0].seller.name, 'Northwind');
});

test('cursor pages continue without overlap and nullable failure preserves data', async () => {
  const first = await executeProducts({ first: 1 });
  assert.equal(first.data.products.pageInfo.hasNextPage, true);
  const second = await executeProducts({ first: 1, after: first.data.products.pageInfo.endCursor });
  assert.equal(second.data.products.edges[0].node.id, 'p-2');
  assert.equal(second.data.products.edges[0].node.price, null);
  assert.deepEqual(second.errors[0].path, ['products', 'edges', 0, 'node', 'price']);

  const invalid = await executeProducts({ first: 51 });
  assert.ok(invalid.errors);
  assert.equal(encodeCursor('p-1').length > 0, true);
});

test('persisted operation verifies registration and rejects expensive documents', async () => {
  const dir = __dirname;
  const source = fs.readFileSync(path.join(dir, 'product_summary.graphql'), 'utf8');
  const operationId = crypto.createHash('sha256').update(source).digest('hex');
  const { result, estimate } = await executePersisted(operationId, { id: 'p-1' });
  assert.equal(result.data.product.seller.name, 'Northwind');
  assert.ok(estimate.maxDepth <= 5);

  await assert.rejects(executePersisted('not-registered', { id: 'p-1' }), /Unknown persisted operation/);
  const expensive = parse('{ products { edges { node { seller { products { id } } } } } }');
  assert.throws(() => checkBudget(expensive, { maxDepth: 3, maxCost: 4 }), /exceeds configured query budget/);
});