// Fetch a tenancy record by the ID the database API returned (fictional).
// The database uses 64-bit integer keys.

export interface Tenancy { id: number; tenant: string; }

export function parseTenancyList(json: string): Tenancy[] {
  return JSON.parse(json) as Tenancy[];
}

// The database is queried with the ID as text, e.g. GET /tenancies/{id}.
export function findTenancy(records: Map<string, string>, id: number): string | undefined {
  return records.get(String(id));
}
