const { buildSchema, graphql } = require('graphql');
const DataLoader = require('dataloader');

const schema = buildSchema(`
  type Seller { id: ID!, name: String! }
  type Product { id: ID!, name: String!, seller: Seller! }
  type Query { products: [Product!]! }
`);

const products = Array.from({ length: 40 }, (_, index) => ({
  id: `p-${index + 1}`,
  name: `Product ${index + 1}`,
  sellerId: `s-${(index % 4) + 1}`,
}));
const sellers = new Map([
  ['s-1', { id: 's-1', name: 'Northwind' }],
  ['s-2', { id: 's-2', name: 'Contoso' }],
  ['s-3', { id: 's-3', name: 'Fabrikam' }],
  ['s-4', { id: 's-4', name: 'Adventure Works' }],
]);

schema.getType('Product').getFields().seller.resolve = (product, _args, context) =>
  context.loaders.sellerById.load(product.sellerId);

async function executeDashboard() {
  let batchCalls = 0;
  const sellerById = new DataLoader(async (keys) => {
    batchCalls += 1;
    const rows = new Map(keys.map((key) => [key, sellers.get(key) ?? null]));
    return keys.map((key) => rows.get(key));
  }, { maxBatchSize: 100 });

  const result = await graphql({
    schema,
    source: '{ products { id name seller { id name } } }',
    rootValue: { products: () => products },
    contextValue: { loaders: { sellerById } },
  });
  return { result, batchCalls };
}

module.exports = { executeDashboard };

if (require.main === module) {
  executeDashboard().then(({ result, batchCalls }) => {
    console.log(`Returned ${result.data.products.length} products in ${batchCalls} seller batch.`);
  });
}