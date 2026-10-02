const {
  GraphQLBoolean,
  GraphQLError,
  GraphQLFloat,
  GraphQLID,
  GraphQLInt,
  GraphQLNonNull,
  GraphQLObjectType,
  GraphQLSchema,
  GraphQLString,
  graphql,
} = require('graphql');

const products = [
  { id: 'p-1', name: 'Desk lamp', price: 35.5 },
  { id: 'p-2', name: 'Task chair', price: 219.0 },
  { id: 'p-3', name: 'Monitor arm', price: 88.0 },
];

function encodeCursor(id) {
  return Buffer.from(JSON.stringify({ id })).toString('base64url');
}

function decodeCursor(cursor) {
  try {
    const decoded = JSON.parse(Buffer.from(cursor, 'base64url').toString('utf8'));
    if (!products.some((product) => product.id === decoded.id)) throw new Error();
    return decoded.id;
  } catch {
    throw new GraphQLError('Invalid cursor', {
      extensions: { code: 'BAD_USER_INPUT' },
    });
  }
}

const ProductType = new GraphQLObjectType({
  name: 'Product',
  fields: {
    id: { type: new GraphQLNonNull(GraphQLID) },
    name: { type: new GraphQLNonNull(GraphQLString) },
    price: {
      type: GraphQLFloat,
      resolve: (product) => {
        if (product.id === 'p-2') throw new Error('Pricing service timeout');
        return product.price;
      },
    },
  },
});

const EdgeType = new GraphQLObjectType({
  name: 'ProductEdge',
  fields: {
    cursor: { type: new GraphQLNonNull(GraphQLString) },
    node: { type: new GraphQLNonNull(ProductType) },
  },
});
const PageInfoType = new GraphQLObjectType({
  name: 'PageInfo',
  fields: {
    endCursor: { type: GraphQLString },
    hasNextPage: { type: new GraphQLNonNull(GraphQLBoolean) },
  },
});
const ConnectionType = new GraphQLObjectType({
  name: 'ProductConnection',
  fields: {
    edges: { type: new GraphQLNonNull(new (require('graphql').GraphQLList)(new GraphQLNonNull(EdgeType))) },
    pageInfo: { type: new GraphQLNonNull(PageInfoType) },
  },
});

const schema = new GraphQLSchema({
  query: new GraphQLObjectType({
    name: 'Query',
    fields: {
      products: {
        type: new GraphQLNonNull(ConnectionType),
        args: {
          first: { type: GraphQLInt, defaultValue: 2 },
          after: { type: GraphQLString },
        },
        resolve: (_root, { first, after }) => {
          if (first < 1 || first > 50) {
            throw new GraphQLError('first must be between 1 and 50');
          }
          const startIndex = after
            ? products.findIndex((product) => product.id === decodeCursor(after)) + 1
            : 0;
          const rows = products.slice(startIndex, startIndex + first + 1);
          const hasNextPage = rows.length > first;
          const pageRows = rows.slice(0, first);
          const edges = pageRows.map((node) => ({ node, cursor: encodeCursor(node.id) }));
          return {
            edges,
            pageInfo: {
              endCursor: edges.at(-1)?.cursor ?? null,
              hasNextPage,
            },
          };
        },
      },
    },
  }),
});

function executeProducts({ first = 2, after } = {}) {
  return graphql({
    schema,
    source: `query Page($first: Int!, $after: String) {
      products(first: $first, after: $after) {
        edges { cursor node { id name price } }
        pageInfo { endCursor hasNextPage }
      }
    }`,
    variableValues: { first, after },
  });
}

module.exports = { encodeCursor, executeProducts };

if (require.main === module) {
  executeProducts().then((result) => console.log(JSON.stringify(result, null, 2)));
}