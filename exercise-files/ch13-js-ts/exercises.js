// Chapter 13 exercises. The answers are in this file, so don't read it until you've tried.
// Use the page's 'Show one possible answer' button instead.
window.EXERCISES = [
{
  id: "13_01", title: "The field that rode along",
  book: "Scenario 1, the field that rode along",
  fn: "updateProfile",
  task: "Tenants update their profile through <code>updateProfile(user, body)</code>. The assistant's version copies " +
    "whatever the request contains into the stored record, so a tenant can send <code>{\"isAdmin\": true}</code>. " +
    "Rewrite it. Only <code>displayName</code> and <code>phone</code> may change, each must be a string of 100 " +
    "characters or fewer, and anything else must be refused with an error. A refused request must change " +
    "<strong>nothing</strong>, even if part of it was fine.",
  hint: "Check the whole request first and collect the changes in a separate object. Only when every field has passed, " +
    "copy them onto the user with one <code>Object.assign</code>.",
  begin:
"// The assistant's version (TypeScript types removed, so it runs in your browser).\n" +
"function updateProfile(user, body) {\n" +
"  const changes = body; // TypeScript said this was a ProfileUpdate. At run time, nothing checks it.\n" +
"  Object.assign(user, changes);\n" +
"  return user;\n" +
"}\n",
  end:
"const ALLOWED = [\"displayName\", \"phone\"];\n\n" +
"function updateProfile(user, body) {\n" +
"  if (typeof body !== \"object\" || body === null || Array.isArray(body)) throw new Error(\"body must be an object\");\n" +
"  const extra = Object.keys(body).filter((k) => !ALLOWED.includes(k));\n" +
"  if (extra.length) throw new Error(\"field not allowed: \" + extra.join(\", \"));\n" +
"  const changes = {};\n" +
"  for (const key of ALLOWED) {\n" +
"    const value = body[key];\n" +
"    if (value === undefined) continue;\n" +
"    if (typeof value !== \"string\" || value.length > 100) throw new Error(key + \" must be a short string\");\n" +
"    changes[key] = value;\n" +
"  }\n" +
"  Object.assign(user, changes);\n" +
"  return user;\n" +
"}\n",
  tests: [
    ["updates the display name", function (f) { var u = jo(); f(u, { displayName: "Jo K" }); return u.displayName === "Jo K"; }],
    ["updates the phone number", function (f) { var u = jo(); f(u, { phone: "01632 960002" }); return u.phone === "01632 960002"; }],
    ["refuses isAdmin, and the tenant stays a tenant", function (f) { var u = jo(); return throws(function () { f(u, { displayName: "Jo", isAdmin: true }); }) && u.isAdmin === false; }],
    ["refuses a phone number that isn't text", function (f) { var u = jo(); return throws(function () { f(u, { phone: 123 }); }) && u.phone === "01632 960001"; }],
    ["refuses a mixed request, and changes nothing (good name, bad phone)", function (f) { var u = jo(); return throws(function () { f(u, { displayName: "Changed", phone: 123 }); }) && u.displayName === "Jo"; }],
    ["refuses a name longer than 100 characters", function (f) { var u = jo(); return throws(function () { f(u, { displayName: "x".repeat(101) }); }) && u.displayName === "Jo"; }],
    ["refuses a body that isn't an object", function (f) { var u = jo(); return throws(function () { f(u, null); }) && throws(function () { f(u, ["isAdmin"]); }); }]
  ]
},
{
  id: "13_02", title: "The neighbour's tenancy",
  book: "Scenario 2, the neighbour's tenancy",
  fn: "parseTenancyList",
  task: "The database's API sends tenancy IDs as 64-bit numbers, and the portal shows the tenancy for the ID it parsed. " +
    "Press <strong>Run my tests</strong> on the assistant's version: ID 9007199254740993 comes back as 9007199254740992, " +
    "the neighbour's flat. Rewrite <code>parseTenancyList(json)</code> so every <code>id</code> comes back as a string " +
    "with its exact digits, whether the API sends it as a number or as a string.",
  hint: "<code>JSON.parse</code> takes a second argument, a function that sees each value as it's parsed. In current " +
    "browsers that function gets a third argument, <code>context</code>, and <code>context.source</code> is the " +
    "original text of a number, before it was rounded.",
  begin:
"// The assistant's version.\n" +
"function parseTenancyList(json) {\n" +
"  return JSON.parse(json);\n" +
"}\n",
  end:
"function parseTenancyList(json) {\n" +
"  return JSON.parse(json, function (key, value, context) {\n" +
"    if (key === \"id\" && typeof value === \"number\") {\n" +
"      if (context && context.source) return context.source; // the exact digits the API sent\n" +
"      if (!Number.isSafeInteger(value)) throw new Error(\"unsafe numeric id: send ids as strings\");\n" +
"      return String(value);\n" +
"    }\n" +
"    return value;\n" +
"  });\n" +
"}\n",
  tests: [
    ["a small ID still works (it comes back as the string \"1042\")", function (f) { return f('[{"id": 1042, "tenant": "Flat 3"}]')[0].id === "1042"; }],
    ["Flat 7's ID keeps its last digit: 9007199254740993", function (f) { return f('[{"id": 9007199254740993, "tenant": "Flat 7, Holm Road"}]')[0].id === "9007199254740993"; }],
    ["an ID the API already sends as a string is left alone", function (f) { return f('[{"id": "9007199254740993", "tenant": "Flat 7, Holm Road"}]')[0].id === "9007199254740993"; }],
    ["Flat 6 and Flat 7 get different IDs", function (f) { var l = f('[{"id": 9007199254740992, "tenant": "Flat 6"}, {"id": 9007199254740993, "tenant": "Flat 7"}]'); return l[0].id !== l[1].id; }],
    ["other fields are untouched", function (f) { return f('[{"id": 1, "tenant": "Flat 3"}]')[0].tenant === "Flat 3"; }]
  ]
}
];

function jo() { return { id: "u1", displayName: "Jo", phone: "01632 960001", isAdmin: false }; }
function throws(fn) { try { fn(); return false; } catch (e) { return true; } }
