import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';

final forgottenPasswordFormProvider =
    StateNotifierProvider.autoDispose<
      ForgottenPasswordFormNotifier,
      ForgottenPasswordFormState
    >((ref) {
      final requestOtpCallback = ref
          .read(authProvider.notifier)
          .requestPasswordResetOtp;
      final verifyOtpCallback = ref
          .read(authProvider.notifier)
          .verifyPasswordResetOtp;

      return ForgottenPasswordFormNotifier(
        requestOtpCallback: requestOtpCallback,
        verifyOtpCallback: verifyOtpCallback,
      );
    });

class ForgottenPasswordFormNotifier
    extends StateNotifier<ForgottenPasswordFormState> {
  final Future<void> Function(String email) requestOtpCallback;
  final Future<void> Function(String email, String otp) verifyOtpCallback;

  ForgottenPasswordFormNotifier({
    required this.requestOtpCallback,
    required this.verifyOtpCallback,
  }) : super(ForgottenPasswordFormState());

  void onEmailChange(String value) {
    final email = Email.dirty(value);
    state = state.copyWith(
      email: email,
      isEmailValid: Formz.validate([email]),
      errorMessages: const [],
    );
  }

  void onOtpChange(String value) {
    final otp = Otp.dirty(value);
    state = state.copyWith(
      otp: otp,
      isOtpValid: Formz.validate([otp]),
      errorMessages: const [],
    );
  }

  Future<bool> requestOtp() async {
    _touchEmailField();
    if (!state.isEmailValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      final email = state.email.value.trim();
      await requestOtpCallback(email);
      if (!mounted) return false;

      state = state.copyWith(
        isPosting: false,
        submittedEmail: email,
        isEmailFormPosted: false,
      );
      return true;
    } on CustomError catch (e) {
      if (!mounted) return false;
      state = state.copyWith(isPosting: false, errorMessages: e.messages);
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible enviar el codigo OTP'],
      );
      return false;
    }
  }

  Future<bool> verifyOtp() async {
    _touchOtpField();
    if (!state.isOtpValid || state.submittedEmail.isEmpty) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await verifyOtpCallback(state.submittedEmail, state.otp.value.trim());
      if (!mounted) return false;

      state = state.copyWith(isPosting: false);
      return true;
    } on CustomError catch (e) {
      if (!mounted) return false;
      state = state.copyWith(isPosting: false, errorMessages: e.messages);
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible verificar el codigo OTP'],
      );
      return false;
    }
  }

  void reset() {
    state = ForgottenPasswordFormState();
  }

  void _touchEmailField() {
    final email = Email.dirty(state.email.value);
    state = state.copyWith(
      email: email,
      isEmailFormPosted: true,
      isEmailValid: Formz.validate([email]),
    );
  }

  void _touchOtpField() {
    final otp = Otp.dirty(state.otp.value);
    state = state.copyWith(
      otp: otp,
      isOtpFormPosted: true,
      isOtpValid: Formz.validate([otp]),
    );
  }
}

class ForgottenPasswordFormState {
  final bool isPosting;
  final bool isEmailFormPosted;
  final bool isOtpFormPosted;
  final Email email;
  final Otp otp;
  final bool isEmailValid;
  final bool isOtpValid;
  final String submittedEmail;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  bool get canRequestOtp => !isPosting && isEmailValid;
  bool get canVerifyOtp =>
      !isPosting && isOtpValid && submittedEmail.isNotEmpty;

  ForgottenPasswordFormState({
    this.isPosting = false,
    this.isEmailFormPosted = false,
    this.isOtpFormPosted = false,
    this.email = const Email.pure(),
    this.otp = const Otp.pure(),
    this.isEmailValid = false,
    this.isOtpValid = false,
    this.submittedEmail = '',
    this.errorMessages = const [],
  });

  ForgottenPasswordFormState copyWith({
    bool? isPosting,
    bool? isEmailFormPosted,
    bool? isOtpFormPosted,
    Email? email,
    Otp? otp,
    bool? isEmailValid,
    bool? isOtpValid,
    String? submittedEmail,
    List<String>? errorMessages,
  }) => ForgottenPasswordFormState(
    isPosting: isPosting ?? this.isPosting,
    isEmailFormPosted: isEmailFormPosted ?? this.isEmailFormPosted,
    isOtpFormPosted: isOtpFormPosted ?? this.isOtpFormPosted,
    email: email ?? this.email,
    otp: otp ?? this.otp,
    isEmailValid: isEmailValid ?? this.isEmailValid,
    isOtpValid: isOtpValid ?? this.isOtpValid,
    submittedEmail: submittedEmail ?? this.submittedEmail,
    errorMessages: errorMessages ?? this.errorMessages,
  );
}
