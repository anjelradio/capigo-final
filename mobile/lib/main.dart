import 'dart:async';

import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/realtime/realtime.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Environment.initEnvironment();
  await Firebase.initializeApp();
  await Hive.initFlutter();
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

class _MainAppState extends ConsumerState<MainApp> with WidgetsBindingObserver {
  bool _offlineQueueStarted = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    Future.microtask(() async {
      final router = ref.read(goRouterProvider);
      await PushNotificationsService.instance.initialize(router: router);
      await _startOfflineQueueSync();
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      unawaited(_syncOfflineQueue());
    }
  }

  Future<void> _startOfflineQueueSync() async {
    if (_offlineQueueStarted) return;
    _offlineQueueStarted = true;

    await ref.read(incidentOfflineQueueServiceProvider).start(
      repositoryResolver: () async => ref.read(incidentRepositoryProvider),
      canSync: () {
        final authState = ref.read(authProvider);
        final token = authState.user?.token ?? '';
        return authState.authStatus == AuthStatus.authenticated && token.trim().isNotEmpty;
      },
    );
  }

  Future<void> _syncOfflineQueue() async {
    if (!_offlineQueueStarted) return;
    await ref.read(incidentOfflineQueueServiceProvider).syncPending();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    unawaited(ref.read(incidentOfflineQueueServiceProvider).stop());
    super.dispose();
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
      unawaited(_syncOfflineQueue());
    });

    return MaterialApp.router(
      routerConfig: appRouter,
      theme: AppTheme().getTheme(),
      debugShowCheckedModeBanner: false,
    );
  }
}
