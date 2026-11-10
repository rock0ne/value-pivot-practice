// Show both faults, using the module named on the command line.
import { strict as assert } from "node:assert";
const which = process.argv[2] ?? "original";
const prof = await import(which === "original" ? "./profile.ts" : "../answer-key/profile_fixed.ts");
const ids = await import(which === "original" ? "./ids.ts" : "../answer-key/ids_fixed.ts");

const users = new Map([["u1", { id: "u1", displayName: "Jo", phone: "01632 960001", isAdmin: false }]]);
let profileOutcome: string;
try {
  const u = prof.updateProfile(users, "u1", { displayName: "Jo", isAdmin: true });
  profileOutcome = `accepted; isAdmin is now ${u.isAdmin}`;
} catch (e) {
  profileOutcome = `rejected: ${(e as Error).message}`;
}
console.log("profile update with isAdmin:", profileOutcome);

// One good field and one bad one: the request must change nothing.
// "regression" runs the Draft 1.8.1 fix, kept in tools/regression.
const mixedUsers = new Map([["u1", { id: "u1", displayName: "Jo", phone: "01632 960001", isAdmin: false }]]);
const mixedProf = which === "regression" ? await import("../tools/regression/profile_fixed_v1_8_1.ts") : prof;
let mixedOutcome: string;
try {
  mixedProf.updateProfile(mixedUsers, "u1", { displayName: "Changed", phone: 123 });
  mixedOutcome = "accepted";
} catch (e) {
  mixedOutcome = `rejected: ${(e as Error).message}`;
}
console.log("mixed update:", mixedOutcome + "; stored name is now", mixedUsers.get("u1")!.displayName);

// Two neighbouring tenancies, as the database API sends them.
const apiJson = '[{"id": 9007199254740993, "tenant": "Flat 7, Holm Road"}]';
// The database holds the exact keys.
const records = new Map<string, string>([
  ["9007199254740992", "Flat 6, Holm Road"],
  ["9007199254740993", "Flat 7, Holm Road"],
]);
const list = ids.parseTenancyList(apiJson);
const found = ids.findTenancy(records, list[0].id);
console.log("asked for:", "9007199254740993", "parsed id:", String(list[0].id), "record fetched:", found);
