import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/presentation/providers/providers.dart';
import 'package:mobile/features/realtime/data/data.dart';
import 'package:mobile/features/realtime/domain/domain.dart';

final incidentRealtimeApiProvider = Provider<IncidentRealtimeApi>((ref) {
  final authState = ref.watch(authProvider);
  final token = authState.user?.token ?? '';
  return IncidentRealtimeApi(accessToken: token);
});

final incidentRealtimeRepositoryProvider = Provider<IncidentRealtimeRepository>(
  (ref) {
    final api = ref.watch(incidentRealtimeApiProvider);
    return IncidentRealtimeRepository(realtimeApi: api);
  },
);

final incidentRealtimeProvider =
    StateNotifierProvider.autoDispose<
      IncidentRealtimeNotifier,
      IncidentRealtimeState
    >((ref) {
      final repository = ref.watch(incidentRealtimeRepositoryProvider);
      return IncidentRealtimeNotifier(repository: repository);
    });

class IncidentRealtimeNotifier extends StateNotifier<IncidentRealtimeState> {
  IncidentRealtimeNotifier({required IncidentRealtimeRepository repository})
    : _repository = repository,
      super(IncidentRealtimeState());

  final IncidentRealtimeRepository _repository;
  WebSocket? _socket;
  StreamSubscription<dynamic>? _socketSubscription;
  Timer? _reconnectTimer;

  Future<void> connect({
    required String incidentId,
    required String initialStatus,
  }) async {
    final normalizedIncidentId = incidentId.trim();
    if (normalizedIncidentId.isEmpty) return;

    if (state.incidentId == normalizedIncidentId &&
        (state.isConnected || state.isConnecting)) {
      return;
    }

    await _disconnectSocket();

    state = state.copyWith(
      incidentId: normalizedIncidentId,
      currentStatus: initialStatus,
      isConnecting: true,
      isConnected: false,
      errorMessages: const [],
    );

    await _loadSnapshot(normalizedIncidentId);
    await _openSocket(normalizedIncidentId);
  }

  Future<void> disconnect() async {
    _clearReconnectTimer();
    await _disconnectSocket();
    if (!mounted) return;
    state = state.copyWith(isConnecting: false, isConnected: false);
  }

  void updateInitialStatus(String status) {
    if (state.currentStatus.isNotEmpty) return;
    state = state.copyWith(currentStatus: status);
  }

  Future<void> _loadSnapshot(String incidentId) async {
    try {
      final snapshot = await _repository.getIncidentSnapshot(incidentId);
      if (!mounted) return;

      state = state.copyWith(
        currentStatus: snapshot.status,
        snapshot: snapshot,
      );
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(
        errorMessages: const ['No se pudo cargar el estado en tiempo real.'],
      );
    }
  }

  Future<void> _openSocket(String incidentId) async {
    try {
      final socket = await _repository.connectIncidentChannel(incidentId);
      if (!mounted) {
        await socket.close();
        return;
      }

      _socket = socket;
      _socketSubscription = socket.listen(
        _handleSocketMessage,
        onDone: _handleSocketDone,
        onError: (error) {
          debugPrint('Incident realtime socket error: $error');
          _scheduleReconnect();
        },
        cancelOnError: true,
      );

      state = state.copyWith(
        isConnecting: false,
        isConnected: true,
        errorMessages: const [],
      );
    } catch (_) {
      debugPrint(
        'Incident realtime socket connection failed for incident=$incidentId',
      );
      if (!mounted) return;
      state = state.copyWith(
        isConnecting: false,
        isConnected: false,
        errorMessages: const ['No se pudo conectar al canal en tiempo real.'],
      );
      _scheduleReconnect();
    }
  }

  void _handleSocketMessage(dynamic rawMessage) {
    if (!mounted) return;

    final snapshot = _repository.mapSnapshotFromSocket(rawMessage);
    if (snapshot != null) {
      state = state.copyWith(
        currentStatus: snapshot.status,
        snapshot: snapshot,
      );
      return;
    }

    final realtimeEvent = _repository.mapRealtimeEvent(rawMessage);
    if (realtimeEvent == null) return;

    var nextStatus = state.currentStatus;
    final statusValue = '${realtimeEvent.payload['status'] ?? ''}'.trim();
    if (statusValue.isNotEmpty) {
      nextStatus = statusValue;
    }

    final currentSnapshot = state.snapshot;
    final nextMechanicLatitude = _asDouble(
      realtimeEvent.payload['mechanic_latitude'] ??
          realtimeEvent.payload['latitude'] ??
          currentSnapshot?.mechanicLatitude,
    );
    final nextMechanicLongitude = _asDouble(
      realtimeEvent.payload['mechanic_longitude'] ??
          realtimeEvent.payload['longitude'] ??
          currentSnapshot?.mechanicLongitude,
    );
    final nextLocationUpdatedAt =
        _asDateTime(
          realtimeEvent.payload['mechanic_location_updated_at'] ??
              realtimeEvent.payload['updated_at'],
        ) ??
        currentSnapshot?.mechanicLocationUpdatedAt;

    final rebuiltSnapshot = currentSnapshot == null
        ? null
        : IncidentRealtimeSnapshot(
            incidentId: currentSnapshot.incidentId,
            status: nextStatus,
            assignmentId: currentSnapshot.assignmentId,
            repairShopId: currentSnapshot.repairShopId,
            mechanicId: currentSnapshot.mechanicId,
            mechanicLatitude: nextMechanicLatitude,
            mechanicLongitude: nextMechanicLongitude,
            mechanicLocationUpdatedAt: nextLocationUpdatedAt,
            lastEventAt: realtimeEvent.createdAt,
          );

    state = state.copyWith(
      currentStatus: nextStatus,
      snapshot: rebuiltSnapshot,
      events: [...state.events, realtimeEvent],
    );
  }

  double? _asDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    return double.tryParse('$value');
  }

  DateTime? _asDateTime(dynamic value) {
    if (value == null) return null;
    final parsed = DateTime.tryParse('$value');
    return parsed?.toLocal();
  }

  void _handleSocketDone() {
    debugPrint(
      'Incident realtime socket closed for incident=${state.incidentId}',
    );
    if (!mounted) return;
    state = state.copyWith(isConnected: false, isConnecting: false);
    _scheduleReconnect();
  }

  void _scheduleReconnect() {
    final incidentId = state.incidentId;
    final currentStatus = state.currentStatus;
    if (incidentId.isEmpty) return;
    if (_reconnectTimer != null) return;

    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      _reconnectTimer = null;
      if (!mounted) return;
      unawaited(connect(incidentId: incidentId, initialStatus: currentStatus));
    });
  }

  Future<void> _disconnectSocket() async {
    await _socketSubscription?.cancel();
    _socketSubscription = null;

    final socket = _socket;
    _socket = null;
    if (socket != null) {
      await socket.close();
    }
  }

  void _clearReconnectTimer() {
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
  }

  @override
  void dispose() {
    _clearReconnectTimer();
    unawaited(_disconnectSocket());
    super.dispose();
  }
}

class IncidentRealtimeState {
  IncidentRealtimeState({
    this.incidentId = '',
    this.currentStatus = '',
    this.isConnecting = false,
    this.isConnected = false,
    this.snapshot,
    this.events = const [],
    this.errorMessages = const [],
  });

  final String incidentId;
  final String currentStatus;
  final bool isConnecting;
  final bool isConnected;
  final IncidentRealtimeSnapshot? snapshot;
  final List<IncidentRealtimeEvent> events;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  IncidentRealtimeState copyWith({
    String? incidentId,
    String? currentStatus,
    bool? isConnecting,
    bool? isConnected,
    IncidentRealtimeSnapshot? snapshot,
    List<IncidentRealtimeEvent>? events,
    List<String>? errorMessages,
  }) {
    return IncidentRealtimeState(
      incidentId: incidentId ?? this.incidentId,
      currentStatus: currentStatus ?? this.currentStatus,
      isConnecting: isConnecting ?? this.isConnecting,
      isConnected: isConnected ?? this.isConnected,
      snapshot: snapshot ?? this.snapshot,
      events: events ?? this.events,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
