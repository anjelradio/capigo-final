import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/assignments/domain/domain.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';

import 'mechanic_active_assignment_provider.dart';

enum MechanicServicesMode { completed, history }

final mechanicServicesProvider = StateNotifierProvider.autoDispose
    .family<
      MechanicServicesNotifier,
      MechanicServicesState,
      MechanicServicesMode
    >((ref, mode) {
      final repository = ref.watch(mechanicAssignmentRepositoryProvider);

      Future<List<MechanicServiceItem>> loader() {
        if (mode == MechanicServicesMode.completed) {
          return repository.getCompletedServices();
        }
        return repository.getServicesHistory();
      }

      return MechanicServicesNotifier(loadServices: loader);
    });

final mechanicServiceDetailProvider = StateNotifierProvider.autoDispose
    .family<MechanicServiceDetailNotifier, MechanicServiceDetailState, String>((
      ref,
      incidentId,
    ) {
      final repository = ref.watch(mechanicAssignmentRepositoryProvider);
      return MechanicServiceDetailNotifier(
        loadDetail: () => repository.getIncidentDetail(incidentId),
      );
    });

class MechanicServicesNotifier extends StateNotifier<MechanicServicesState> {
  MechanicServicesNotifier({required this.loadServices})
    : super(MechanicServicesState());

  final Future<List<MechanicServiceItem>> Function() loadServices;

  Future<void> load() async {
    if (state.isLoading || state.isRefreshing) return;
    await _fetch(isRefresh: false);
  }

  Future<void> refresh() async {
    if (state.isLoading || state.isRefreshing) return;
    await _fetch(isRefresh: true);
  }

  Future<void> _fetch({required bool isRefresh}) async {
    state = state.copyWith(
      isLoading: isRefresh ? state.isLoading : true,
      isRefreshing: isRefresh,
      errorMessages: const [],
    );

    try {
      final services = await loadServices();
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        services: services,
        errorMessages: const [],
      );
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
        errorMessages: const ['No fue posible cargar servicios.'],
      );
    }
  }
}

class MechanicServicesState {
  MechanicServicesState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.services = const [],
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final List<MechanicServiceItem> services;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  MechanicServicesState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    List<MechanicServiceItem>? services,
    List<String>? errorMessages,
  }) {
    return MechanicServicesState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      services: services ?? this.services,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

class MechanicServiceDetailNotifier
    extends StateNotifier<MechanicServiceDetailState> {
  MechanicServiceDetailNotifier({required this.loadDetail})
    : super(MechanicServiceDetailState());

  final Future<MechanicAssignment> Function() loadDetail;

  Future<void> load() async {
    if (state.isLoading || state.isRefreshing) return;
    await _fetch(isRefresh: false);
  }

  Future<void> refresh() async {
    if (state.isLoading || state.isRefreshing) return;
    await _fetch(isRefresh: true);
  }

  Future<void> _fetch({required bool isRefresh}) async {
    state = state.copyWith(
      isLoading: isRefresh ? state.isLoading : true,
      isRefreshing: isRefresh,
      errorMessages: const [],
    );

    try {
      final detail = await loadDetail();
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        detail: detail,
        errorMessages: const [],
      );
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
        errorMessages: const ['No fue posible cargar el detalle.'],
      );
    }
  }
}

class MechanicServiceDetailState {
  MechanicServiceDetailState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.detail,
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final MechanicAssignment? detail;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  MechanicServiceDetailState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    MechanicAssignment? detail,
    List<String>? errorMessages,
  }) {
    return MechanicServiceDetailState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      detail: detail ?? this.detail,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
