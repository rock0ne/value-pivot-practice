// Profile updates for the Brightwell Lettings tenant portal (fictional).
// Written as an AI assistant might write it, to show a common failure pattern.

export interface User {
  id: string;
  displayName: string;
  phone: string;
  isAdmin: boolean;
}

export type ProfileUpdate = Pick<User, "displayName" | "phone">;

export function updateProfile(users: Map<string, User>, userId: string, body: unknown): User {
  const user = users.get(userId);
  if (!user) throw new Error("no such user");
  const changes = body as ProfileUpdate;
  Object.assign(user, changes);
  return user;
}
