const fs = require('node:fs');
const path = require('node:path');
const { buildSchema, graphql, GraphQLError } = require('graphql');

const schema = buildSchema(
  fs.readFileSync(path.join(__dirname, 'library.graphql'), 'utf8'),
);

const authors = new Map([
  ['a-1', { id: 'a-1', name: 'N. K. Jemisin' }],
  ['a-2', { id: 'a-2', name: 'Ursula K. Le Guin' }],
]);
const books = new Map([
  ['b-1', { id: 'b-1', title: 'The Fifth Season', format: 'PAPERBACK', authorId: 'a-1' }],
  ['b-2', { id: 'b-2', title: 'A Wizard of Earthsea', format: 'HARDCOVER', authorId: 'a-2' }],
]);
let nextBookId = 3;

schema.getType('Book').getFields().author.resolve = (book, _args, context) => {
  const author = context.authors.get(book.authorId);
  if (!author) throw new GraphQLError('Author is unavailable');
  return author;
};

const rootValue = {
  book: ({ id }) => books.get(id) ?? null,
  books: ({ first }) => [...books.values()].slice(0, Math.min(first, 50)),
  search: ({ term }) => {
    const normalized = term.toLowerCase();
    const matchingBooks = [...books.values()]
      .filter((book) => book.title.toLowerCase().includes(normalized))
      .map((book) => ({ ...book, __typename: 'Book' }));
    const matchingAuthors = [...authors.values()]
      .filter((author) => author.name.toLowerCase().includes(normalized))
      .map((author) => ({ ...author, __typename: 'Author' }));
    return [...matchingBooks, ...matchingAuthors];
  },
  createBook: ({ input }, context) => {
    if (!context.viewer?.roles.includes('EDITOR')) {
      throw new GraphQLError('Editor role required', {
        extensions: { code: 'FORBIDDEN' },
      });
    }
    if (!authors.has(input.authorId)) {
      throw new GraphQLError('Author does not exist', {
        extensions: { code: 'BAD_USER_INPUT' },
      });
    }
    const book = {
      id: `b-${nextBookId++}`,
      title: input.title,
      format: input.format ?? 'PAPERBACK',
      authorId: input.authorId,
    };
    books.set(book.id, book);
    return book;
  },
};

function executeLibrary(source, { variables = {}, viewer = { roles: [] } } = {}) {
  return graphql({
    schema,
    source,
    rootValue,
    variableValues: variables,
    contextValue: { viewer, authors },
  });
}

module.exports = { executeLibrary, schema };

if (require.main === module) {
  executeLibrary(`query BookDetail($id: ID!) {
    book(id: $id) { title format author { name } }
  }`, { variables: { id: 'b-1' } }).then((result) => {
    console.log(JSON.stringify(result, null, 2));
  });
}