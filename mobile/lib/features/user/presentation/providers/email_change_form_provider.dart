import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/user_providers.dart';

enum EmailChangeStep { otp, newEmail }

final emailChangeFormProvider =
    StateNotifierProvider<EmailChangeFormNotifier, EmailChangeFormState>((ref) {
      final userRepository = ref.watch(userRepositoryProvider);
      final authNotifier = ref.read(authProvider.notifier);

      Future<void> requestOtp() async {
        await userRepository.requestEmailChangeOtp();
      }

      Future<String> verifyOtp(String otp) async {
        return userRepository.verifyEmailChangeOtp(otp);
      }

      Future<void> updateEmail(String newEmail, String changeEmailToken) async {
        final updatedUser = await userRepository.updateEmail(
          newEmail: newEmail,
          changeEmailToken: changeEmailToken,
        );

        authNotifier.syncUser(updatedUser);
      }

      return EmailChangeFormNotifier(
        requestOtpCallback: requestOtp,
        verifyOtpCallback: verifyOtp,
        updateEmailCallback: updateEmail,
      );
    });

class EmailChangeFormNotifier extends StateNotifier<EmailChangeFormState> {
  EmailChangeFormNotifier({
    required this.requestOtpCallback,
    required this.verifyOtpCallback,
    required this.updateEmailCallback,
  }) : super(EmailChangeFormState());

  final Future<void> Function() requestOtpCallback;
  final Future<String> Function(String otp) verifyOtpCallback;
  final Future<void> Function(String newEmail, String changeEmailToken)
  updateEmailCallback;

  void onOtpChange(String value) {
    final otpInput = Otp.dirty(value);
    state = state.copyWith(
      otp: otpInput,
      isOtpValid: Formz.validate([otpInput]),
      errorMessages: const [],
    );
  }

  void onNewEmailChange(String value) {
    final emailInput = Email.dirty(value);
    state = state.copyWith(
      newEmail: emailInput,
      isNewEmailValid: Formz.validate([emailInput]),
      errorMessages: const [],
    );
  }

  void resetFlow() {
    state = EmailChangeFormState();
  }

  void goToOtpStep() {
    state = state.copyWith(step: EmailChangeStep.otp, errorMessages: const []);
  }

  Future<bool> requestOtp() async {
    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await requestOtpCallback();
      if (!mounted) return false;

      state = state.copyWith(isPosting: false, step: EmailChangeStep.otp);
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
    if (!state.isOtpValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      final changeToken = await verifyOtpCallback(state.otp.value.trim());
      if (!mounted) return false;

      state = state.copyWith(
        isPosting: false,
        step: EmailChangeStep.newEmail,
        changeEmailToken: changeToken,
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
        errorMessages: const ['No fue posible verificar el codigo OTP'],
      );
      return false;
    }
  }

  Future<bool> submitNewEmail() async {
    _touchNewEmailField();
    if (!state.isNewEmailValid || state.changeEmailToken.isEmpty) {
      return false;
    }

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      final newEmailValue = state.newEmail.value.trim();
      await updateEmailCallback(newEmailValue, state.changeEmailToken);
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
        errorMessages: const ['No fue posible actualizar el correo'],
      );
      return false;
    }
  }

  void _touchOtpField() {
    final otpInput = Otp.dirty(state.otp.value);
    state = state.copyWith(
      otp: otpInput,
      isOtpFormPosted: true,
      isOtpValid: Formz.validate([otpInput]),
    );
  }

  void _touchNewEmailField() {
    final emailInput = Email.dirty(state.newEmail.value);
    state = state.copyWith(
      newEmail: emailInput,
      isNewEmailFormPosted: true,
      isNewEmailValid: Formz.validate([emailInput]),
    );
  }
}

class EmailChangeFormState {
  EmailChangeFormState({
    this.isPosting = false,
    this.step = EmailChangeStep.otp,
    this.otp = const Otp.pure(),
    this.newEmail = const Email.pure(),
    this.isOtpFormPosted = false,
    this.isNewEmailFormPosted = false,
    this.isOtpValid = false,
    this.isNewEmailValid = false,
    this.changeEmailToken = '',
    this.errorMessages = const [],
  });

  final bool isPosting;
  final EmailChangeStep step;
  final Otp otp;
  final Email newEmail;
  final bool isOtpFormPosted;
  final bool isNewEmailFormPosted;
  final bool isOtpValid;
  final bool isNewEmailValid;
  final String changeEmailToken;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  EmailChangeFormState copyWith({
    bool? isPosting,
    EmailChangeStep? step,
    Otp? otp,
    Email? newEmail,
    bool? isOtpFormPosted,
    bool? isNewEmailFormPosted,
    bool? isOtpValid,
    bool? isNewEmailValid,
    String? changeEmailToken,
    List<String>? errorMessages,
  }) {
    return EmailChangeFormState(
      isPosting: isPosting ?? this.isPosting,
      step: step ?? this.step,
      otp: otp ?? this.otp,
      newEmail: newEmail ?? this.newEmail,
      isOtpFormPosted: isOtpFormPosted ?? this.isOtpFormPosted,
      isNewEmailFormPosted: isNewEmailFormPosted ?? this.isNewEmailFormPosted,
      isOtpValid: isOtpValid ?? this.isOtpValid,
      isNewEmailValid: isNewEmailValid ?? this.isNewEmailValid,
      changeEmailToken: changeEmailToken ?? this.changeEmailToken,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
