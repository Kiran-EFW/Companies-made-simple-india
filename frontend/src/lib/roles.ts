export const FOUNDER_ROLES = ["user", "admin", "super_admin"];
export const CA_ROLES = ["ca_lead", "cs_lead"];
export const STAFF_ROLES = ["filing_coordinator", "customer_success"];
export const ALL_ROLES = [...FOUNDER_ROLES, ...CA_ROLES, ...STAFF_ROLES];

export function isFounderRole(role: string): boolean {
  return FOUNDER_ROLES.includes(role);
}

export function isCaRole(role: string): boolean {
  return CA_ROLES.includes(role);
}

export function isStaffRole(role: string): boolean {
  return STAFF_ROLES.includes(role);
}
