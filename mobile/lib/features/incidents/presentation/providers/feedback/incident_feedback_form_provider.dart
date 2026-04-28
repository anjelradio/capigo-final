import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/incidents/presentation/providers/request_service/request_service_repository_provider.dart';

final incidentFeedbackFormProvider = StateNotifierProvider.autoDispose
    .family<IncidentFeedbackFormNotifier, IncidentFeedbackFormState, String>((
      ref,
      incidentId,
    ) {
      final repository = ref.watch(incidentRepositoryProvider);

      Future<void> submitFeedback({
        required int rating,
        String? comment,
      }) async {
        await repository.submitIncidentFeedback(
          incidentId: incidentId,
          rating: rating,
          comment: comment,
        );
      }

      return IncidentFeedbackFormNotifier(onSubmit: submitFeedback);
    });

class IncidentFeedbackFormNotifier
    extends StateNotifier<IncidentFeedbackFormState> {
  IncidentFeedbackFormNotifier({required this.onSubmit})
    : super(IncidentFeedbackFormState());

  final Future<void> Function({required int rating, String? comment}) onSubmit;

  void onRatingChanged(int rating) {
    final ratingInput = IncidentRating.dirty(rating);
    state = state.copyWith(
      rating: ratingInput,
      errorMessages: const [],
      isValid: _validate(rating: ratingInput),
    );
  }

  void onCommentChanged(String value) {
    final comment = IncidentFeedbackComment.dirty(value);
    state = state.copyWith(
      comment: comment,
      errorMessages: const [],
      isValid: _validate(comment: comment),
    );
  }

  Future<bool> submit() async {
    _touchAll();
    if (!state.isValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await onSubmit(rating: state.rating.value, comment: state.comment.value);
      if (!mounted) return false;

      state = state.copyWith(isPosting: false, errorMessages: const []);
      return true;
    } on CustomError catch (error) {
      if (!mounted) return false;

      state = state.copyWith(isPosting: false, errorMessages: error.messages);
      return false;
    } catch (_) {
      if (!mounted) return false;

      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible enviar tu calificacion.'],
      );
      return false;
    }
  }

  bool _validate({IncidentRating? rating, IncidentFeedbackComment? comment}) {
    return Formz.validate([rating ?? state.rating, comment ?? state.comment]);
  }

  void _touchAll() {
    final rating = IncidentRating.dirty(state.rating.value);
    final comment = IncidentFeedbackComment.dirty(state.comment.value);
    state = state.copyWith(
      rating: rating,
      comment: comment,
      isFormPosted: true,
      isValid: Formz.validate([rating, comment]),
    );
  }
}

class IncidentFeedbackFormState {
  IncidentFeedbackFormState({
    this.rating = const IncidentRating.pure(),
    this.comment = const IncidentFeedbackComment.pure(),
    this.isPosting = false,
    this.isFormPosted = false,
    this.isValid = false,
    this.errorMessages = const [],
  });

  final IncidentRating rating;
  final IncidentFeedbackComment comment;
  final bool isPosting;
  final bool isFormPosted;
  final bool isValid;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  IncidentFeedbackFormState copyWith({
    IncidentRating? rating,
    IncidentFeedbackComment? comment,
    bool? isPosting,
    bool? isFormPosted,
    bool? isValid,
    List<String>? errorMessages,
  }) {
    return IncidentFeedbackFormState(
      rating: rating ?? this.rating,
      comment: comment ?? this.comment,
      isPosting: isPosting ?? this.isPosting,
      isFormPosted: isFormPosted ?? this.isFormPosted,
      isValid: isValid ?? this.isValid,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

enum IncidentRatingError { empty }

class IncidentRating extends FormzInput<int, IncidentRatingError> {
  const IncidentRating.pure() : super.pure(0);
  const IncidentRating.dirty(int value) : super.dirty(value);

  String? get errorMessage {
    if (isPure || isValid) return null;
    return 'Selecciona una calificacion de 1 a 5 estrellas';
  }

  @override
  IncidentRatingError? validator(int value) {
    if (value < 1 || value > 5) return IncidentRatingError.empty;
    return null;
  }
}

enum IncidentFeedbackCommentError { length }

class IncidentFeedbackComment
    extends FormzInput<String, IncidentFeedbackCommentError> {
  const IncidentFeedbackComment.pure() : super.pure('');
  const IncidentFeedbackComment.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isPure || isValid) return null;
    return 'El comentario no puede superar los 1000 caracteres';
  }

  @override
  IncidentFeedbackCommentError? validator(String value) {
    if (value.trim().length > 1000) return IncidentFeedbackCommentError.length;
    return null;
  }
}
