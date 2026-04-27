import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:geolocator/geolocator.dart';
import 'package:mobile/features/assignments/data/data.dart';
import 'package:mobile/features/assignments/domain/domain.dart';
import 'package:mobile/features/auth/auth.dart';

final mechanicAssignmentApiProvider = Provider<MechanicAssignmentApi>((ref) {
  final accessToken = ref.watch(
    authProvider.select((state) => state.user?.token ?? ''),
  );
  return MechanicAssignmentApi(accessToken: accessToken);
});

final mechanicAssignmentRepositoryProvider =
    Provider<MechanicAssignmentRepository>((ref) {
      final api = ref.watch(mechanicAssignmentApiProvider);
      return MechanicAssignmentRepository(mechanicApi: api);
    });

final mechanicActiveAssignmentProvider =
    StateNotifierProvider.autoDispose<
      MechanicActiveAssignmentNotifier,
      MechanicActiveAssignmentState
    >((ref) {
      final repository = ref.watch(mechanicAssignmentRepositoryProvider);
      return MechanicActiveAssignmentNotifier(repository: repository);
    });

class MechanicActiveAssignmentNotifier
    extends StateNotifier<MechanicActiveAssignmentState> {
  MechanicActiveAssignmentNotifier({
    required MechanicAssignmentRepository repository,
  }) : _repository = repository,
       super(MechanicActiveAssignmentState());

  final MechanicAssignmentRepository _repository;
  Timer? _locationLoopTimer;
  int _locationSimulationStep = 0;

  Future<void> loadActiveAssignment() async {
    if (state.isLoading || state.isRefreshing) return;
    await _resolveActiveAssignment(isRefresh: false);
  }

  Future<void> refreshActiveAssignment() async {
    if (state.isLoading || state.isRefreshing) return;
    await _resolveActiveAssignment(isRefresh: true);
  }

  Future<void> loadAssignmentDetail() async {
    final assignmentId = state.assignment?.assignmentId ?? '';
    if (assignmentId.isEmpty) return;
    if (state.isRefreshing) return;

    state = state.copyWith(isRefreshing: true, errorMessages: const []);
    try {
      final detail = await _repository.getAssignmentDetail(assignmentId);
      if (!mounted) return;
      state = state.copyWith(
        isRefreshing: false,
        assignment: detail,
        errorMessages: const [],
      );
      await _loadTodayStats();
    } on CustomError catch (error) {
      if (!mounted) return;
      state = state.copyWith(
        isRefreshing: false,
        errorMessages: error.messages,
      );
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(
        isRefreshing: false,
        errorMessages: const ['No fue posible cargar el detalle del servicio.'],
      );
    }
  }

  Future<void> _resolveActiveAssignment({required bool isRefresh}) async {
    state = state.copyWith(
      isLoading: isRefresh ? state.isLoading : true,
      isRefreshing: isRefresh,
      errorMessages: const [],
    );

    try {
      final assignment = await _repository.getMyActiveAssignment();
      if (!mounted) return;

      DateTime? nextActiveSince;
      if (assignment != null) {
        final isSameAssignment =
            assignment.assignmentId == state.assignment?.assignmentId;
        nextActiveSince = isSameAssignment
            ? state.activeSince
            : assignment.assignedAt?.toLocal() ?? DateTime.now();
      }

      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        assignment: assignment,
        activeSince: nextActiveSince,
        errorMessages: const [],
      );

      await _loadTodayStats();

      if (assignment == null || !assignment.canReportLocation) {
        stopLocationSync();
      }
    } on CustomError catch (error) {
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        errorMessages: error.messages,
      );
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        errorMessages: const ['No fue posible cargar tu servicio activo.'],
      );
    }
  }

  Future<void> _loadTodayStats() async {
    try {
      final todayStats = await _repository.getTodayStats();
      if (!mounted) return;
      state = state.copyWith(todayStats: todayStats);
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(
        todayStats:
            state.todayStats ??
            MechanicTodayStats(completedToday: 0, cancelledToday: 0),
      );
    }
  }

  Future<void> updateStatus(String status) async {
    final assignment = state.assignment;
    if (assignment == null || state.isUpdatingStatus) return;

    state = state.copyWith(isUpdatingStatus: true, errorMessages: const []);

    try {
      final action = await _repository.updateAssignmentStatus(
        assignmentId: assignment.assignmentId,
        status: status,
      );
      if (!mounted) return;

      state = state.copyWith(
        isUpdatingStatus: false,
        lastActionMessage: action.detail,
        errorMessages: const [],
      );

      await refreshActiveAssignment();
    } on CustomError catch (error) {
      if (!mounted) return;
      state = state.copyWith(
        isUpdatingStatus: false,
        errorMessages: error.messages,
      );
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(
        isUpdatingStatus: false,
        errorMessages: const [
          'No fue posible actualizar el estado del servicio.',
        ],
      );
    }
  }

  void clearLastActionMessage() {
    state = state.copyWith(lastActionMessage: '');
  }

  void startLocationSync() {
    if (_locationLoopTimer != null) return;
    _locationLoopTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _syncLocationOnce();
    });
    unawaited(_syncLocationOnce());
  }

  void stopLocationSync() {
    _locationLoopTimer?.cancel();
    _locationLoopTimer = null;
    _locationSimulationStep = 0;
    if (state.isSyncingLocation) {
      state = state.copyWith(isSyncingLocation: false);
    }
  }

  Future<void> _syncLocationOnce() async {
    final assignment = state.assignment;
    if (assignment == null ||
        !assignment.canReportLocation ||
        state.isSyncingLocation) {
      return;
    }

    final position = await _resolveCurrentPosition();
    if (position == null) return;

    state = state.copyWith(isSyncingLocation: true);
    try {
      final adjustedCoordinates = _withDebugSimulatedMovement(
        latitude: position.latitude,
        longitude: position.longitude,
      );

      await _repository.updateAssignmentLocation(
        assignmentId: assignment.assignmentId,
        latitude: adjustedCoordinates.latitude,
        longitude: adjustedCoordinates.longitude,
        recordedAt: DateTime.now().toUtc(),
      );
      if (!mounted) return;
      state = state.copyWith(
        isSyncingLocation: false,
        locationSyncAt: DateTime.now(),
      );
    } on CustomError catch (error) {
      if (!mounted) return;
      state = state.copyWith(
        isSyncingLocation: false,
        errorMessages: error.messages,
      );
    } catch (_) {
      if (!mounted) return;
      state = state.copyWith(isSyncingLocation: false);
    }
  }

  Future<Position?> _resolveCurrentPosition() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (!mounted) return null;
      state = state.copyWith(
        errorMessages: const ['Activa el GPS para compartir tu ubicacion.'],
      );
      return null;
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      if (!mounted) return null;
      state = state.copyWith(
        errorMessages: const [
          'Permiso de ubicacion denegado para sincronizar.',
        ],
      );
      return null;
    }

    return Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
    );
  }

  _GeoPoint _withDebugSimulatedMovement({
    required double latitude,
    required double longitude,
  }) {
    if (!kDebugMode) {
      return _GeoPoint(latitude: latitude, longitude: longitude);
    }

    const longitudeStep = 0.00008;
    final adjustedLongitude =
        longitude + (_locationSimulationStep * longitudeStep);
    _locationSimulationStep += 1;

    return _GeoPoint(latitude: latitude, longitude: adjustedLongitude);
  }

  @override
  void dispose() {
    stopLocationSync();
    super.dispose();
  }
}

class MechanicActiveAssignmentState {
  MechanicActiveAssignmentState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.isUpdatingStatus = false,
    this.isSyncingLocation = false,
    this.assignment,
    this.activeSince,
    this.locationSyncAt,
    this.todayStats,
    this.lastActionMessage = '',
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final bool isUpdatingStatus;
  final bool isSyncingLocation;
  final MechanicAssignment? assignment;
  final DateTime? activeSince;
  final DateTime? locationSyncAt;
  final MechanicTodayStats? todayStats;
  final String lastActionMessage;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  MechanicActiveAssignmentState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    bool? isUpdatingStatus,
    bool? isSyncingLocation,
    Object? assignment = _unset,
    Object? activeSince = _unset,
    Object? locationSyncAt = _unset,
    Object? todayStats = _unset,
    String? lastActionMessage,
    List<String>? errorMessages,
  }) {
    return MechanicActiveAssignmentState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      isUpdatingStatus: isUpdatingStatus ?? this.isUpdatingStatus,
      isSyncingLocation: isSyncingLocation ?? this.isSyncingLocation,
      assignment: assignment == _unset
          ? this.assignment
          : assignment as MechanicAssignment?,
      activeSince: activeSince == _unset
          ? this.activeSince
          : activeSince as DateTime?,
      locationSyncAt: locationSyncAt == _unset
          ? this.locationSyncAt
          : locationSyncAt as DateTime?,
      todayStats: todayStats == _unset
          ? this.todayStats
          : todayStats as MechanicTodayStats?,
      lastActionMessage: lastActionMessage ?? this.lastActionMessage,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

const _unset = Object();

class _GeoPoint {
  _GeoPoint({required this.latitude, required this.longitude});

  final double latitude;
  final double longitude;
}
