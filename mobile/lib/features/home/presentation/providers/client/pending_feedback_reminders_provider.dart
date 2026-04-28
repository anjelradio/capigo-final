import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/incidents/presentation/providers/request_service/request_service_repository_provider.dart';

final pendingFeedbackRemindersProvider =
    StateNotifierProvider<
      PendingFeedbackRemindersNotifier,
      PendingFeedbackRemindersState
    >((ref) {
      final repository = ref.watch(incidentRepositoryProvider);
      return PendingFeedbackRemindersNotifier(
        loadReminders: repository.getPendingFeedbackReminders,
      );
    });

class PendingFeedbackRemindersNotifier
    extends StateNotifier<PendingFeedbackRemindersState> {
  PendingFeedbackRemindersNotifier({required this.loadReminders})
    : super(PendingFeedbackRemindersState());

  final Future<List<PendingFeedbackReminder>> Function() loadReminders;

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
      final reminders = await loadReminders();
      if (!mounted) return;
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        hasLoaded: true,
        reminders: reminders,
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
        errorMessages: const [
          'No fue posible cargar los recordatorios de calificacion.',
        ],
      );
    }
  }
}

class PendingFeedbackRemindersState {
  PendingFeedbackRemindersState({
    this.isLoading = false,
    this.isRefreshing = false,
    this.hasLoaded = false,
    this.reminders = const [],
    this.errorMessages = const [],
  });

  final bool isLoading;
  final bool isRefreshing;
  final bool hasLoaded;
  final List<PendingFeedbackReminder> reminders;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  PendingFeedbackRemindersState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    bool? hasLoaded,
    List<PendingFeedbackReminder>? reminders,
    List<String>? errorMessages,
  }) {
    return PendingFeedbackRemindersState(
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      hasLoaded: hasLoaded ?? this.hasLoaded,
      reminders: reminders ?? this.reminders,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
