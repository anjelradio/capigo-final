import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/incidents/presentation/providers/request_service/request_service_repository_provider.dart';

enum ClientServicesListMode { completed, history }

final clientServicesProvider = StateNotifierProvider.autoDispose
    .family<
      ClientServicesNotifier,
      ClientServicesState,
      ClientServicesListMode
    >((ref, mode) {
      final repository = ref.watch(incidentRepositoryProvider);

      Future<List<ClientServiceItem>> loader() {
        if (mode == ClientServicesListMode.completed) {
          return repository.getCompletedServices();
        }
        return repository.getServicesHistory();
      }

      return ClientServicesNotifier(loadServices: loader);
    });

final clientServiceDetailProvider = StateNotifierProvider.autoDispose
    .family<ClientServiceDetailNotifier, ClientServiceDetailState, String>((
      ref,
      incidentId,
    ) {
      final repository = ref.watch(incidentRepositoryProvider);
      return ClientServiceDetailNotifier(
        loadDetail: () => repository.getServiceDetail(incidentId: incidentId),
      );
    });

class ClientServicesNotifier extends StateNotifier<ClientServicesState> {
  ClientServicesNotifier({required this.loadServices})
    : super(ClientServicesState());

  final Future<List<ClientServiceItem>> Function() loadServices;

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
        errorMessages: const ['No fue posible cargar los servicios.'],
      );
    }
  }
}

class ClientServicesState {
  ClientServicesState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.services = const [],
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final List<ClientServiceItem> services;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  ClientServicesState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    List<ClientServiceItem>? services,
    List<String>? errorMessages,
  }) {
    return ClientServicesState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      services: services ?? this.services,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

class ClientServiceDetailNotifier
    extends StateNotifier<ClientServiceDetailState> {
  ClientServiceDetailNotifier({required this.loadDetail})
    : super(ClientServiceDetailState());

  final Future<ClientServiceDetail> Function() loadDetail;

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
        errorMessages: const ['No fue posible cargar el detalle del servicio.'],
      );
    }
  }
}

class ClientServiceDetailState {
  ClientServiceDetailState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.detail,
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final ClientServiceDetail? detail;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  ClientServiceDetailState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    ClientServiceDetail? detail,
    List<String>? errorMessages,
  }) {
    return ClientServiceDetailState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      detail: detail ?? this.detail,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
