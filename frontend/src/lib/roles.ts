export const CA_ROLES = ["ca_lead", "cs_lead"] as const;
export const FOUNDER_ROLES = ["user", "admin", "super_admin"] as const;

export function isCARole(role: string | undefined): boolean {
  return CA_ROLES.includes(role as any);
}

export function isFounderRole(role: string | undefined): boolean {
  return FOUNDER_ROLES.includes(role as any);
}
