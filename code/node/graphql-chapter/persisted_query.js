const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const {
  GraphQLError,
  buildSchema,
  graphql,
  parse,
  validate,
} = require('graphql');

const directory = __dirname;
const manifest = JSON.parse(
  fs.readFileSync(path.join(directory, 'persisted_operations.json'), 'utf8'),
);
const source = fs.readFileSync(path.join(directory, 'product_summary.graphql'), 'utf8');
const schema = buildSchema(`
  type Seller { id: ID!, name: String! }
  type Product { id: ID!, title: String!, seller: Seller! }
  type Query { product(id: ID!): Product }
`);

function estimateSelection(selectionSet, depth = 0) {
  let maxDepth = depth;
  let cost = 0;
  for (const selection of selectionSet?.selections ?? []) {
    if (selection.kind !== 'Field') continue;
    const nextDepth = depth + 1;
    const child = estimateSelection(selection.selectionSet, nextDepth);
    maxDepth = Math.max(maxDepth, child.maxDepth);
    cost += 1 + child.cost;
  }
  return { maxDepth, cost };
}

function checkBudget(document, { maxDepth = 5, maxCost = 20 } = {}) {
  const operation = document.definitions.find((definition) => definition.kind === 'OperationDefinition');
  const estimate = estimateSelection(operation?.selectionSet);
  if (estimate.maxDepth > maxDepth || estimate.cost > maxCost) {
    throw new GraphQLError('Operation exceeds configured query budget', {
      extensions: { code: 'QUERY_TOO_COMPLEX', ...estimate },
    });
  }
  return estimate;
}

async function executePersisted(operationId, variables = {}) {
  const approved = manifest.operations[operationId];
  if (!approved) {
    throw new GraphQLError('Unknown persisted operation', {
      extensions: { code: 'PERSISTED_QUERY_NOT_FOUND' },
    });
  }

  const operationSource = fs.readFileSync(path.join(directory, approved.file), 'utf8');
  const actualHash = crypto.createHash('sha256').update(operationSource).digest('hex');
  if (actualHash !== operationId || operationSource !== source) {
    throw new GraphQLError('Persisted operation manifest integrity check failed');
  }

  const document = parse(operationSource);
  const errors = validate(schema, document);
  if (errors.length) throw errors[0];
  const estimate = checkBudget(document);
  const result = await graphql({
    schema,
    source: operationSource,
    rootValue: {
      product: ({ id }) => id === 'p-1'
        ? { id, title: 'Desk lamp', seller: { id: 's-1', name: 'Northwind' } }
        : null,
    },
    variableValues: variables,
  });
  return { result, estimate };
}

module.exports = { checkBudget, executePersisted, schema };

if (require.main === module) {
  const [operationId] = Object.keys(manifest.operations);
  executePersisted(operationId, { id: 'p-1' }).then(({ result, estimate }) => {
    console.log(JSON.stringify({ estimate, result }, null, 2));
  }).catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}