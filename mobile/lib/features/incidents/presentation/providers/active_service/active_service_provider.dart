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
        cancelIncidentCallback: incidentRepository.cancelIncident,
        loadIncidentOffersCallback: incidentRepository.getIncidentOffers,
        acceptIncidentOfferCallback: incidentRepository.acceptIncidentOffer,
        rejectIncidentOfferCallback: incidentRepository.rejectIncidentOffer,
      );
    });

class ActiveServiceNotifier extends StateNotifier<ActiveServiceState> {
  ActiveServiceNotifier({
    required this.loadActiveIncidentCallback,
    required this.cancelIncidentCallback,
    required this.loadIncidentOffersCallback,
    required this.acceptIncidentOfferCallback,
    required this.rejectIncidentOfferCallback,
  }) : super(ActiveServiceState());

  final Future<ActiveIncidentDetail?> Function() loadActiveIncidentCallback;
  final Future<void> Function({required String incidentId})
  cancelIncidentCallback;
  final Future<List<ClientIncidentOffer>> Function({required String incidentId})
  loadIncidentOffersCallback;
  final Future<ClientOfferActionResult> Function({
    required String incidentId,
    required String assignmentId,
  })
  acceptIncidentOfferCallback;
  final Future<ClientOfferActionResult> Function({
    required String incidentId,
    required String assignmentId,
  })
  rejectIncidentOfferCallback;

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

      if (detail == null) {
        state = state.copyWith(
          isLoading: false,
          isRefreshing: false,
          hasLoaded: true,
          detail: null,
          offers: const [],
          offersErrorMessages: const [],
          errorMessages: const [],
        );
        return;
      }

      final offersResult = await _loadIncidentOffersGuarded(
        incidentId: detail.incident.id,
      );
      if (!mounted) return;

      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        detail: detail,
        offers: offersResult.offers,
        offersErrorMessages: offersResult.errorMessages,
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

  Future<void> refreshOffersForIncident() async {
    if (state.isLoadingOffers) return;

    final incidentId = state.detail?.incident.id.trim() ?? '';
    if (incidentId.isEmpty) {
      state = state.copyWith(offers: const [], offersErrorMessages: const []);
      return;
    }

    state = state.copyWith(
      isLoadingOffers: true,
      offersErrorMessages: const [],
    );
    final result = await _loadIncidentOffersGuarded(incidentId: incidentId);
    if (!mounted) return;

    state = state.copyWith(
      isLoadingOffers: false,
      offers: result.offers,
      offersErrorMessages: result.errorMessages,
    );
  }

  Future<bool> acceptOffer({required String assignmentId}) async {
    final incidentId = state.detail?.incident.id.trim() ?? '';
    if (incidentId.isEmpty) return false;
    if (state.actingOfferId.isNotEmpty) return false;

    state = state.copyWith(
      actingOfferId: assignmentId,
      isAcceptingOffer: true,
      offersErrorMessages: const [],
    );

    try {
      await acceptIncidentOfferCallback(
        incidentId: incidentId,
        assignmentId: assignmentId,
      );
      if (!mounted) return false;

      await _resolveActiveIncident(isRefresh: true);
      if (!mounted) return false;

      state = state.copyWith(actingOfferId: '', isAcceptingOffer: false);
      return true;
    } on CustomError catch (error) {
      if (!mounted) return false;
      state = state.copyWith(
        actingOfferId: '',
        isAcceptingOffer: false,
        offersErrorMessages: error.messages,
      );
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        actingOfferId: '',
        isAcceptingOffer: false,
        offersErrorMessages: const ['No fue posible aceptar la oferta.'],
      );
      return false;
    }
  }

  Future<bool> rejectOffer({required String assignmentId}) async {
    final incidentId = state.detail?.incident.id.trim() ?? '';
    if (incidentId.isEmpty) return false;
    if (state.actingOfferId.isNotEmpty) return false;

    state = state.copyWith(
      actingOfferId: assignmentId,
      isAcceptingOffer: false,
      offersErrorMessages: const [],
    );

    try {
      await rejectIncidentOfferCallback(
        incidentId: incidentId,
        assignmentId: assignmentId,
      );
      if (!mounted) return false;

      final nextOffers = state.offers
          .where((offer) => offer.assignmentId != assignmentId)
          .toList();
      state = state.copyWith(
        actingOfferId: '',
        offers: nextOffers,
        offersErrorMessages: const [],
      );

      await refreshOffersForIncident();
      if (!mounted) return false;
      return true;
    } on CustomError catch (error) {
      if (!mounted) return false;
      state = state.copyWith(
        actingOfferId: '',
        offersErrorMessages: error.messages,
      );
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        actingOfferId: '',
        offersErrorMessages: const ['No fue posible rechazar la oferta.'],
      );
      return false;
    }
  }

  Future<_OfferLoadResult> _loadIncidentOffersGuarded({
    required String incidentId,
  }) async {
    try {
      final offers = await loadIncidentOffersCallback(incidentId: incidentId);
      return _OfferLoadResult(offers: offers, errorMessages: const []);
    } on CustomError catch (error) {
      return _OfferLoadResult(offers: const [], errorMessages: error.messages);
    } catch (_) {
      return _OfferLoadResult(
        offers: const [],
        errorMessages: const ['No fue posible cargar ofertas disponibles.'],
      );
    }
  }

  Future<bool> cancelActiveIncident() async {
    final incidentId = state.detail?.incident.id ?? '';
    if (incidentId.trim().isEmpty || state.isCancelling) return false;

    state = state.copyWith(isCancelling: true, errorMessages: const []);
    try {
      await cancelIncidentCallback(incidentId: incidentId);
      if (!mounted) return false;

      state = state.copyWith(
        isCancelling: false,
        detail: null,
        errorMessages: const [],
      );
      return true;
    } on CustomError catch (error) {
      if (!mounted) return false;
      state = state.copyWith(
        isCancelling: false,
        errorMessages: error.messages,
      );
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        isCancelling: false,
        errorMessages: const ['No fue posible cancelar el servicio.'],
      );
      return false;
    }
  }
}

class ActiveServiceState {
  ActiveServiceState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.isCancelling = false,
    this.hasLoaded = false,
    this.detail,
    this.offers = const [],
    this.isLoadingOffers = false,
    this.actingOfferId = '',
    this.isAcceptingOffer = false,
    this.offersErrorMessages = const [],
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool isCancelling;
  final bool hasLoaded;
  final ActiveIncidentDetail? detail;
  final List<ClientIncidentOffer> offers;
  final bool isLoadingOffers;
  final String actingOfferId;
  final bool isAcceptingOffer;
  final List<String> offersErrorMessages;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  String get offersErrorMessage =>
      offersErrorMessages.isNotEmpty ? offersErrorMessages.first : '';

  ActiveServiceState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? isCancelling,
    bool? hasLoaded,
    Object? detail = _unset,
    List<ClientIncidentOffer>? offers,
    bool? isLoadingOffers,
    String? actingOfferId,
    bool? isAcceptingOffer,
    List<String>? offersErrorMessages,
    List<String>? errorMessages,
  }) {
    return ActiveServiceState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      isCancelling: isCancelling ?? this.isCancelling,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      detail: detail == _unset ? this.detail : detail as ActiveIncidentDetail?,
      offers: offers ?? this.offers,
      isLoadingOffers: isLoadingOffers ?? this.isLoadingOffers,
      actingOfferId: actingOfferId ?? this.actingOfferId,
      isAcceptingOffer: isAcceptingOffer ?? this.isAcceptingOffer,
      offersErrorMessages: offersErrorMessages ?? this.offersErrorMessages,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

class _OfferLoadResult {
  _OfferLoadResult({required this.offers, required this.errorMessages});

  final List<ClientIncidentOffer> offers;
  final List<String> errorMessages;
}

const _unset = Object();
