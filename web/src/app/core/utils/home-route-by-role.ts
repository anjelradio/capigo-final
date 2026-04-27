import { APP_ROUTES } from '../config/routes';

type UserRole = 'admin' | 'owner' | 'mechanic' | 'client';

export function resolveHomeRouteByRole(role: UserRole | null | undefined): string {
  switch (role) {
    case 'admin':
      return APP_ROUTES.APP_HOME_ADMIN;
    case 'owner':
      return APP_ROUTES.APP_OWNER_REQUESTS;
    case 'mechanic':
      return APP_ROUTES.APP_HOME_MECHANIC;
    case 'client':
      return APP_ROUTES.APP_HOME_CLIENT;
    default:
      return APP_ROUTES.APP_HOME_CLIENT;
  }
}
