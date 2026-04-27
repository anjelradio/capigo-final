type UserRole = 'admin' | 'owner' | 'mechanic' | 'client';

export const MECHANIC_WEB_ACCESS_MESSAGE =
  'Por favor, ingresa desde la aplicacion movil';

export function isWebAllowedRole(role: UserRole): boolean {
  return role !== 'mechanic';
}
