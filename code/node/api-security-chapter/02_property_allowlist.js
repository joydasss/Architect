const assert = require("node:assert/strict");

const editableFields = new Set(["title", "body", "visibility"]);
const allowedVisibility = new Set(["private", "team"]);

function applyDocumentUpdate(document, input) {
  if (input === null || typeof input !== "object" || Array.isArray(input)) {
    throw new TypeError("request body must be an object");
  }

  const unexpected = Object.keys(input).filter((field) => !editableFields.has(field));
  if (unexpected.length > 0) {
    throw new TypeError("request contains unsupported fields");
  }

  const update = {};
  if (Object.hasOwn(input, "title")) {
    if (typeof input.title !== "string" || input.title.length > 120) {
      throw new TypeError("title is invalid");
    }
    update.title = input.title;
  }
  if (Object.hasOwn(input, "body")) {
    if (typeof input.body !== "string" || input.body.length > 10000) {
      throw new TypeError("body is invalid");
    }
    update.body = input.body;
  }
  if (Object.hasOwn(input, "visibility")) {
    if (!allowedVisibility.has(input.visibility)) {
      throw new TypeError("visibility is invalid");
    }
    update.visibility = input.visibility;
  }

  return { ...document, ...update };
}

const original = {
  id: "doc-42",
  tenantId: "tenant-a",
  ownerId: "user-17",
  title: "Old title",
  body: "Old body",
  visibility: "private",
  isAdminOnly: false,
};
const updated = applyDocumentUpdate(original, { title: "New title", visibility: "team" });
assert.equal(updated.title, "New title");
assert.equal(updated.ownerId, "user-17");
assert.equal(updated.isAdminOnly, false);
assert.throws(() => applyDocumentUpdate(original, { ownerId: "attacker" }), /unsupported fields/);
assert.throws(() => applyDocumentUpdate(original, { isAdminOnly: true }), /unsupported fields/);
assert.throws(() => applyDocumentUpdate(original, { visibility: "public" }), /visibility is invalid/);
console.log("property allow-list checks passed");
