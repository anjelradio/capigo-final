import 'package:dio/dio.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/config.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  debugPrint('Push background message id=${message.messageId}');
}

class PushNotificationsService {
  PushNotificationsService._();

  static final PushNotificationsService instance = PushNotificationsService._();

  bool _initialized = false;
  String _accessToken = '';
  String _lastKnownPushToken = '';

  Future<void> setAccessToken(String token) async {
    final normalized = token.trim();
    _accessToken = normalized;
    if (normalized.isEmpty) return;

    if (_lastKnownPushToken.isNotEmpty) {
      await _sendPushTokenToBackend(_lastKnownPushToken);
      return;
    }

    final messagingToken = await FirebaseMessaging.instance.getToken();
    if (messagingToken == null || messagingToken.trim().isEmpty) return;
    _lastKnownPushToken = messagingToken.trim();
    await _sendPushTokenToBackend(_lastKnownPushToken);
  }

  void clearAccessToken() {
    _accessToken = '';
  }

  Future<void> initialize({required GoRouter router}) async {
    if (_initialized) return;

    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

    final messaging = FirebaseMessaging.instance;
    await messaging.requestPermission(alert: true, badge: true, sound: true);

    final token = await messaging.getToken();
    if (token != null && token.trim().isNotEmpty) {
      _lastKnownPushToken = token.trim();
      debugPrint('Push token obtained: $_lastKnownPushToken');
      await _sendPushTokenToBackend(_lastKnownPushToken);
    }

    messaging.onTokenRefresh.listen((nextToken) async {
      _lastKnownPushToken = nextToken.trim();
      debugPrint('Push token refreshed: $nextToken');
      await _sendPushTokenToBackend(_lastKnownPushToken);
    });

    FirebaseMessaging.onMessage.listen((message) {
      debugPrint('Push foreground message id=${message.messageId}');
    });

    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      _handleNotificationNavigation(router, message);
    });

    final initialMessage = await messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationNavigation(router, initialMessage);
    }

    _initialized = true;
  }

  Future<void> _sendPushTokenToBackend(String pushToken) async {
    if (_accessToken.trim().isEmpty) return;
    if (pushToken.trim().isEmpty) return;

    try {
      final dio = Dio(
        BaseOptions(
          baseUrl: Environment.apiUrl,
          headers: {'Authorization': 'Bearer $_accessToken'},
        ),
      );

      await dio.post(
        '/realtime/me/push-token',
        data: {
          'push_token': pushToken,
          'platform': defaultTargetPlatform.name,
          'device_id': null,
        },
      );
    } catch (error) {
      debugPrint('Push token sync failed: $error');
    }
  }

  void _handleNotificationNavigation(GoRouter router, RemoteMessage message) {
    final data = message.data;
    final routeFromData = '${data['route'] ?? ''}'.trim();
    final type = '${data['type'] ?? ''}'.trim();

    var route = routeFromData;
    if (route.isEmpty && type == 'mechanic.assignment.created') {
      route = '/incidents/mechanic/active-service';
    }

    if (route.isEmpty || !route.startsWith('/')) return;
    router.go(route);
  }
}
