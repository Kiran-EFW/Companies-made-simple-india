export const FOUNDER_ROLES = ["user", "admin", "super_admin"] as const;

export function isFounderRole(role: string | undefined): boolean {
  return FOUNDER_ROLES.includes(role as any);
}
