import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/router/app_router_notifier.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/home/home.dart';
import 'package:mobile/features/incidents/incidents.dart';
import 'package:mobile/features/user/user.dart';

final goRouterProvider = Provider((ref) {
  final goRouterNotifier = ref.read(goRouterNotifierProvider);
  return GoRouter(
    initialLocation: '/check',
    refreshListenable: goRouterNotifier,
    routes: [
      GoRoute(
        path: '/home/client',
        builder: (context, state) {
          final reviewIncidentId =
              state.uri.queryParameters['reviewIncidentId']?.trim() ?? '';
          return ClientHomeScreen(
            reviewIncidentId: reviewIncidentId.isEmpty
                ? null
                : reviewIncidentId,
          );
        },
      ),
      GoRoute(
        path: '/home/mechanic',
        builder: (context, state) => const MechanicHomeScreen(),
      ),
      GoRoute(
        path: '/incidents/request-service',
        builder: (context, state) => const RequestServiceScreen(),
      ),
      GoRoute(
        path: '/incidents/active-service',
        builder: (context, state) => const ActiveServiceScreen(),
      ),
      GoRoute(
        path: '/incidents/services/:incidentId/detail',
        builder: (context, state) {
          final incidentId = state.pathParameters['incidentId'] ?? '';
          return ClientServiceDetailScreen(incidentId: incidentId);
        },
      ),
      GoRoute(
        path: '/incidents/mechanic',
        builder: (context, state) => const MechanicIncidentsScreen(),
      ),
      GoRoute(
        path: '/incidents/mechanic/services/:incidentId/detail',
        builder: (context, state) {
          final incidentId = state.pathParameters['incidentId'] ?? '';
          return MechanicServiceDetailScreen(incidentId: incidentId);
        },
      ),
      GoRoute(
        path: '/incidents/mechanic/active-service',
        builder: (context, state) => const MechanicActiveServiceScreen(),
      ),
      GoRoute(
        path: '/user',
        builder: (context, state) => const UserProfileScreen(),
      ),
      GoRoute(
        path: '/user/vehicles/new',
        builder: (context, state) {
          final fromSheet = state.uri.queryParameters['fromSheet'] == '1';
          return VehicleScreen(
            vehicleId: 'new',
            shouldCloseVehiclesSheetOnDelete: fromSheet,
          );
        },
      ),
      GoRoute(
        path: '/user/vehicles/create',
        redirect: (context, state) => '/user/vehicles/new',
      ),
      GoRoute(
        path: '/user/vehicles/:vehicleId',
        builder: (context, state) {
          final vehicleId = state.pathParameters['vehicleId'] ?? '';
          final fromSheet = state.uri.queryParameters['fromSheet'] == '1';
          return VehicleScreen(
            vehicleId: vehicleId,
            shouldCloseVehiclesSheetOnDelete: fromSheet,
          );
        },
      ),

      // Checking auth
      GoRoute(
        path: '/check',
        builder: (context, state) => const CheckAuthStatusScreen(),
      ),

      // Auth Routes
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
    ],
    redirect: (context, state) {
      final isGoingTo = state.uri.path;
      final authStatus = goRouterNotifier.authStatus;
      final roleHomePath = _resolveHomePath(goRouterNotifier.userRole);

      if (authStatus == AuthStatus.checking) {
        return isGoingTo == '/check' ? null : '/check';
      }

      if (authStatus == AuthStatus.notAuthenticated) {
        if (isGoingTo == '/login' || isGoingTo == '/register') {
          return null;
        }
        return '/login';
      }

      if (authStatus == AuthStatus.authenticated) {
        if (isGoingTo == '/login' ||
            isGoingTo == '/register' ||
            isGoingTo == '/check') {
          return roleHomePath;
        }

        if (isGoingTo == '/home/client' || isGoingTo == '/home/mechanic') {
          return isGoingTo == roleHomePath ? null : roleHomePath;
        }

        if (isGoingTo == '/user' || isGoingTo.startsWith('/user/vehicles')) {
          return null;
        }

        if (isGoingTo.startsWith('/incidents')) {
          return null;
        }

        return roleHomePath;
      }
      return null;
    },
  );
});

String _resolveHomePath(String? role) {
  final normalizedRole = role?.trim().toLowerCase() ?? '';
  if (normalizedRole == 'mechanic') return '/home/mechanic';
  return '/home/client';
}
