// The tests that came with the code. They pass.
import { test } from "node:test";
import assert from "node:assert/strict";
import { updateProfile, type User } from "../profile.ts";
import { parseTenancyList } from "../ids.ts";

function users(): Map<string, User> {
  return new Map([["u1", { id: "u1", displayName: "Jo", phone: "01632 960001", isAdmin: false }]]);
}

test("updates the display name", () => {
  const u = updateProfile(users(), "u1", { displayName: "Jo K" });
  assert.equal(u.displayName, "Jo K");
});

test("updates the phone number", () => {
  const u = updateProfile(users(), "u1", { phone: "01632 960002" });
  assert.equal(u.phone, "01632 960002");
});

test("parses the tenancy list", () => {
  const list = parseTenancyList('[{"id": 1042, "tenant": "Flat 3"}]');
  assert.equal(list[0].id, 1042);
});
