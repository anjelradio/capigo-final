import {
  Building2,
  ClipboardCheck,
  LayoutDashboard,
  LucideIconData,
  Settings,
  Users,
  Wallet,
  Wrench,
} from 'lucide-angular';

import { APP_ROUTES } from '../../../../core/config/routes';

export type HomeNavRole = 'superadmin' | 'repairshop';

export interface HomeNavItem {
  label: string;
  icon: LucideIconData;
  path: string;
}

const REPAIR_SHOP_NAV_ITEMS: HomeNavItem[] = [
  {
    label: 'Inicio',
    icon: LayoutDashboard,
    path: APP_ROUTES.APP_OWNER_HOME,
  },
  {
    label: 'Solicitudes',
    icon: ClipboardCheck,
    path: APP_ROUTES.APP_OWNER_REQUESTS,
  },
  {
    label: 'Asignaciones',
    icon: Users,
    path: APP_ROUTES.APP_OWNER_ASSIGNMENTS,
  },
  {
    label: 'Saldo',
    icon: Wallet,
    path: APP_ROUTES.APP_OWNER_BALANCE,
  },
  {
    label: 'Mecanicos',
    icon: Wrench,
    path: APP_ROUTES.APP_OWNER_MECHANICS,
  },
  {
    label: 'Taller',
    icon: Settings,
    path: APP_ROUTES.APP_OWNER_SHOP_SETTINGS,
  },
];

const SUPERADMIN_NAV_ITEMS: HomeNavItem[] = [
  {
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: APP_ROUTES.APP_HOME_ADMIN,
  },
  {
    label: 'Talleres',
    icon: Building2,
    path: APP_ROUTES.APP_ADMIN_REPAIR_SHOPS,
  },
  {
    label: 'Usuarios',
    icon: Users,
    path: '/app/users',
  },
  {
    label: 'Actividad',
    icon: Building2,
    path: '/app/activity',
  },
];

export const HOME_NAV_BY_ROLE: Record<HomeNavRole, HomeNavItem[]> = {
  superadmin: SUPERADMIN_NAV_ITEMS,
  repairshop: REPAIR_SHOP_NAV_ITEMS,
};
