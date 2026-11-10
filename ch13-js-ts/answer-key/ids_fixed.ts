// The fix: treat 64-bit keys as text end to end. The API sends "id" as a string,
// and nothing ever converts it to a JavaScript number.

export interface Tenancy { id: string; tenant: string; }

export function parseTenancyList(json: string): Tenancy[] {
  const raw = JSON.parse(json, function (key, value, context?: { source?: string }) {
    // If an old API still sends a bare number, keep its exact digits.
    if (key === "id" && typeof value === "number") {
      if (context?.source) return context.source;
      if (!Number.isSafeInteger(value)) throw new Error("unsafe numeric id: send ids as strings");
      return String(value);
    }
    return value;
  });
  return raw as Tenancy[];
}

export function findTenancy(records: Map<string, string>, id: string): string | undefined {
  return records.get(id);
}
