import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/realtime/realtime.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Environment.initEnvironment();
  await Firebase.initializeApp();
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  runApp(const ProviderScope(child: MainApp()));
}

class MainApp extends ConsumerStatefulWidget {
  const MainApp({super.key});

  @override
  ConsumerState<MainApp> createState() => _MainAppState();
}

class _MainAppState extends ConsumerState<MainApp> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      final router = ref.read(goRouterProvider);
      await PushNotificationsService.instance.initialize(router: router);
    });
  }

  @override
  Widget build(BuildContext context) {
    final appRouter = ref.watch(goRouterProvider);

    ref.listen<AuthState>(authProvider, (previous, next) {
      final token = next.user?.token ?? '';
      if (token.trim().isEmpty) {
        PushNotificationsService.instance.clearAccessToken();
        return;
      }
      unawaited(PushNotificationsService.instance.setAccessToken(token));
    });

    return MaterialApp.router(
      routerConfig: appRouter,
      theme: AppTheme().getTheme(),
      debugShowCheckedModeBanner: false,
    );
  }
}
