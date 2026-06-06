import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/features/incidents/data/offline/offline.dart';

final incidentOfflineQueueServiceProvider = Provider<IncidentOfflineQueueService>((ref) {
  final service = IncidentOfflineQueueService();
  ref.onDispose(() => unawaited(service.stop()));
  return service;
});
