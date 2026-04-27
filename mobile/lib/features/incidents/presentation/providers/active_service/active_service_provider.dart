import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/incidents/presentation/providers/request_service/request_service_repository_provider.dart';

final activeServiceProvider =
    StateNotifierProvider.autoDispose<
      ActiveServiceNotifier,
      ActiveServiceState
    >((ref) {
      final incidentRepository = ref.watch(incidentRepositoryProvider);
      return ActiveServiceNotifier(
        loadActiveIncidentCallback: incidentRepository.getActiveIncidentDetail,
      );
    });

class ActiveServiceNotifier extends StateNotifier<ActiveServiceState> {
  ActiveServiceNotifier({required this.loadActiveIncidentCallback})
    : super(ActiveServiceState());

  final Future<ActiveIncidentDetail?> Function() loadActiveIncidentCallback;

  Future<void> loadActiveIncident() async {
    if (state.isLoading || state.isRefreshing) return;
    await _resolveActiveIncident(isRefresh: false);
  }

  Future<void> refreshActiveIncident() async {
    if (state.isLoading || state.isRefreshing) return;
    await _resolveActiveIncident(isRefresh: true);
  }

  Future<void> _resolveActiveIncident({required bool isRefresh}) async {
    state = state.copyWith(
      isLoading: isRefresh ? state.isLoading : true,
      isRefreshing: isRefresh,
      errorMessages: const [],
    );

    try {
      final detail = await loadActiveIncidentCallback();
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
        errorMessages: const ['No fue posible cargar el servicio activo.'],
      );
    }
  }
}

class ActiveServiceState {
  ActiveServiceState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.detail,
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final ActiveIncidentDetail? detail;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  ActiveServiceState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    Object? detail = _unset,
    List<String>? errorMessages,
  }) {
    return ActiveServiceState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      detail: detail == _unset ? this.detail : detail as ActiveIncidentDetail?,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

const _unset = Object();
