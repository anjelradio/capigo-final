import { Routes } from '@angular/router';

import { AppShellComponent } from './core/layout/app-shell/app-shell.component';
import { AuthShellComponent } from './core/layout/auth-shell/auth-shell.component';
import { APP_ROUTES } from './core/config/routes';
import { authGuard } from './core/guards/auth.guard';
import { ownerServicesCompleteGuard } from './core/guards/owner-services-complete.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: APP_ROUTES.AUTH_LOGIN,
  },
  {
    path: 'auth',
    component: AuthShellComponent,
    loadChildren: () =>
      import('./features/auth/presentation/auth.routes').then((m) => m.authRoutes),
  },
  {
    path: 'app',
    component: AppShellComponent,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'client',
      },
      {
        path: 'admin',
        pathMatch: 'full',
        redirectTo: 'repair-shops',
      },
      {
        path: 'repair-shops',
        canActivate: [roleGuard(['admin'])],
        loadComponent: () =>
          import('./features/home/presentation/pages/admin-pages/admin-dashboard-page.component').then(
            (m) => m.AdminDashboardPageComponent,
          ),
      },
      {
        path: 'repair-shops/:shopId/mechanics',
        canActivate: [roleGuard(['admin'])],
        loadComponent: () =>
          import('./features/repair-shop/presentation/pages/admin-repair-shops/admin-repair-shop-mechanics-page.component').then(
            (m) => m.AdminRepairShopMechanicsPageComponent,
          ),
      },
      {
        path: 'repair-shops/:shopId',
        canActivate: [roleGuard(['admin'])],
        loadComponent: () =>
          import('./features/repair-shop/presentation/pages/admin-repair-shops/admin-repair-shop-detail-page.component').then(
            (m) => m.AdminRepairShopDetailPageComponent,
          ),
      },
      {
        path: 'owner',
        pathMatch: 'full',
        redirectTo: 'owner/requests',
      },
      {
        path: 'owner/requests',
        canActivate: [roleGuard(['owner']), ownerServicesCompleteGuard],
        loadComponent: () =>
          import('./features/home/presentation/pages/owner-pages/owner-orders-page.component').then(
            (m) => m.OwnerOrdersPageComponent,
          ),
      },
      {
        path: 'owner/balance',
        canActivate: [roleGuard(['owner']), ownerServicesCompleteGuard],
        loadComponent: () =>
          import('./features/wallet/presentation/pages/owner-wallet-page.component').then(
            (m) => m.OwnerWalletPageComponent,
          ),
      },
      {
        path: 'owner/assignments',
        canActivate: [roleGuard(['owner']), ownerServicesCompleteGuard],
        loadComponent: () =>
          import('./features/home/presentation/pages/owner-pages/owner-assignments-page.component').then(
            (m) => m.OwnerAssignmentsPageComponent,
          ),
      },
      {
        path: 'owner/assignments/:assignmentId/detail',
        canActivate: [roleGuard(['owner']), ownerServicesCompleteGuard],
        loadComponent: () =>
          import('./features/home/presentation/pages/owner-pages/owner-assignment-detail-page.component').then(
            (m) => m.OwnerAssignmentDetailPageComponent,
          ),
      },
      {
        path: 'owner/orders',
        pathMatch: 'full',
        redirectTo: 'owner/requests',
      },
      {
        path: 'owner/history',
        pathMatch: 'full',
        redirectTo: 'owner/balance',
      },
      {
        path: 'owner/mechanics',
        canActivate: [roleGuard(['owner']), ownerServicesCompleteGuard],
        loadComponent: () =>
          import('./features/home/presentation/pages/owner-pages/owner-mechanics-page.component').then(
            (m) => m.OwnerMechanicsPageComponent,
          ),
      },
      {
        path: 'owner/activity',
        pathMatch: 'full',
        redirectTo: 'owner/requests',
      },
      {
        path: 'owner/shop-settings',
        canActivate: [roleGuard(['owner']), ownerServicesCompleteGuard],
        loadComponent: () =>
          import('./features/home/presentation/pages/owner-pages/owner-shop-settings-page.component').then(
            (m) => m.OwnerShopSettingsPageComponent,
          ),
      },
      {
        path: 'mechanic',
        loadComponent: () =>
          import('./features/home/presentation/pages/owner-pages/owner-dashboard-page.component').then(
            (m) => m.OwnerDashboardPageComponent,
          ),
      },
      {
        path: 'repair-shop',
        pathMatch: 'full',
        canActivate: [roleGuard(['client'])],
        loadComponent: () =>
          import('./features/repair-shop/presentation/pages/repair-shop-onboarding/create-repair-shop-page.component').then(
            (m) => m.CreateRepairShopPageComponent,
          ),
      },
      {
        path: 'repair-shop/onboarding',
        pathMatch: 'full',
        redirectTo: 'repair-shop',
      },
      {
        path: 'repair-shop/services',
        canActivate: [roleGuard(['owner'])],
        loadComponent: () =>
          import('./features/repair-shop/presentation/pages/repair-shop-onboarding/register-shop-services-page.component').then(
            (m) => m.RegisterShopServicesPageComponent,
          ),
      },
      {
        path: 'client',
        pathMatch: 'full',
        redirectTo: 'repair-shop',
      },
      {
        path: 'repair-shop/start',
        pathMatch: 'full',
        redirectTo: 'repair-shop',
      },
      {
        path: 'teacher',
        pathMatch: 'full',
        redirectTo: 'owner',
      },
      {
        path: 'profile',
        canActivate: [roleGuard(['admin', 'owner', 'client'])],
        loadComponent: () =>
          import('./features/user/presentation/pages/user-profile-page/user-profile-page.component').then(
            (m) => m.UserProfilePageComponent,
          ),
      },
    ],
  },
  {
    path: '404',
    loadComponent: () =>
      import('./features/shared/presentation/pages/not-found-page/not-found-page.component').then(
        (m) => m.NotFoundPageComponent,
      ),
  },
  {
    path: '**',
    redirectTo: APP_ROUTES.NOT_FOUND,
  },
];
