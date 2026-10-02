const assert = require("node:assert/strict");

function canAccessDocument(principal, document, action) {
  if (!principal || !document || principal.tenantId !== document.tenantId) {
    return false;
  }

  if (action === "read") {
    return document.ownerId === principal.subjectId || principal.permissions.includes("documents:read:any");
  }

  if (action === "update") {
    return document.ownerId === principal.subjectId && principal.permissions.includes("documents:update:own");
  }

  return false;
}

function getDocument(principal, documentId, documents) {
  const document = documents.get(documentId);
  if (!document || !canAccessDocument(principal, document, "read")) {
    return null;
  }
  return document;
}

const user = { subjectId: "user-17", tenantId: "tenant-a", permissions: ["documents:update:own"] };
const otherTenantUser = { subjectId: "user-17", tenantId: "tenant-b", permissions: ["documents:read:any"] };
const document = { id: "doc-42", tenantId: "tenant-a", ownerId: "user-17", body: "synthetic" };
const documents = new Map([[document.id, document]]);

assert.equal(canAccessDocument(user, document, "read"), true);
assert.equal(canAccessDocument(user, document, "update"), true);
assert.equal(canAccessDocument(otherTenantUser, document, "read"), false);
assert.equal(canAccessDocument(user, document, "delete"), false);
assert.equal(getDocument(otherTenantUser, document.id, documents), null);
console.log("object authorization checks passed");
