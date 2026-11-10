// The fix: check the whole request at run time, then change the stored record once.
// Nothing is changed unless every field passes.
import type { User } from "../project/profile.ts";

const ALLOWED = ["displayName", "phone"] as const;

export function updateProfile(users: Map<string, User>, userId: string, body: unknown): User {
  const user = users.get(userId);
  if (!user) throw new Error("no such user");
  if (typeof body !== "object" || body === null || Array.isArray(body)) throw new Error("body must be an object");
  const extra = Object.keys(body).filter((k) => !(ALLOWED as readonly string[]).includes(k));
  if (extra.length) throw new Error(`field not allowed: ${extra.join(", ")}`);
  const changes: Partial<Pick<User, "displayName" | "phone">> = {};
  for (const key of ALLOWED) {
    const value = (body as Record<string, unknown>)[key];
    if (value === undefined) continue;
    if (typeof value !== "string" || value.length > 100) throw new Error(`${key} must be a short string`);
    changes[key] = value;
  }
  Object.assign(user, changes);
  return user;
}
