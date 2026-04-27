import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/user_providers.dart';

final passwordChangeFormProvider =
    StateNotifierProvider.autoDispose<
      PasswordChangeFormNotifier,
      PasswordChangeFormState
    >((ref) {
      final userRepository = ref.watch(userRepositoryProvider);

      Future<void> submitPassword(
        String currentPassword,
        String newPassword,
        String confirmNewPassword,
      ) async {
        await userRepository.updatePassword(
          currentPassword: currentPassword,
          newPassword: newPassword,
          confirmNewPassword: confirmNewPassword,
        );
      }

      return PasswordChangeFormNotifier(submitPasswordCallback: submitPassword);
    });

class PasswordChangeFormNotifier
    extends StateNotifier<PasswordChangeFormState> {
  PasswordChangeFormNotifier({required this.submitPasswordCallback})
    : super(PasswordChangeFormState());

  final Future<void> Function(String, String, String) submitPasswordCallback;

  void onCurrentPasswordChange(String value) {
    state = state.copyWith(currentPassword: value, errorMessages: const []);
  }

  void onNewPasswordChange(String value) {
    state = state.copyWith(
      newPassword: value,
      errorMessages: const [],
      newPasswordInput: Password.dirty(value),
    );
  }

  void onConfirmNewPasswordChange(String value) {
    state = state.copyWith(confirmNewPassword: value, errorMessages: const []);
  }

  void reset() {
    state = PasswordChangeFormState();
  }

  Future<bool> submit() async {
    _touchEveryField();
    if (!state.isValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await submitPasswordCallback(
        state.currentPassword.trim(),
        state.newPassword.trim(),
        state.confirmNewPassword.trim(),
      );

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
        errorMessages: const ['No fue posible actualizar la contraseña'],
      );
      return false;
    }
  }

  void _touchEveryField() {
    // Validacion basica del formulario de cambio de contraseña.
    state = state.copyWith(
      isFormPosted: true,
      newPasswordInput: Password.dirty(state.newPassword),
    );
  }
}

class PasswordChangeFormState {
  PasswordChangeFormState({
    this.isPosting = false,
    this.isFormPosted = false,
    this.currentPassword = '',
    this.newPassword = '',
    this.confirmNewPassword = '',
    this.newPasswordInput = const Password.pure(),
    this.errorMessages = const [],
  });

  final bool isPosting;
  final bool isFormPosted;
  final String currentPassword;
  final String newPassword;
  final String confirmNewPassword;
  final Password newPasswordInput;
  final List<String> errorMessages;

  bool get isCurrentPasswordValid => currentPassword.trim().isNotEmpty;
  bool get isConfirmPasswordValid => confirmNewPassword.trim().isNotEmpty;
  bool get isPasswordMatch =>
      newPassword.trim().isNotEmpty &&
      newPassword.trim() == confirmNewPassword.trim();

  bool get isValid =>
      isCurrentPasswordValid &&
      Formz.validate([newPasswordInput]) &&
      isConfirmPasswordValid &&
      isPasswordMatch;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  String? get currentPasswordError {
    if (!isFormPosted || isCurrentPasswordValid) return null;
    return 'La contraseña actual es requerida';
  }

  String? get newPasswordError {
    if (!isFormPosted) return null;
    return newPasswordInput.errorMessage;
  }

  String? get confirmPasswordError {
    if (!isFormPosted || isConfirmPasswordValid && isPasswordMatch) return null;
    if (!isConfirmPasswordValid) {
      return 'La confirmacion de contraseña es requerida';
    }
    return 'La confirmacion de contraseña no coincide';
  }

  PasswordChangeFormState copyWith({
    bool? isPosting,
    bool? isFormPosted,
    String? currentPassword,
    String? newPassword,
    String? confirmNewPassword,
    Password? newPasswordInput,
    List<String>? errorMessages,
  }) {
    return PasswordChangeFormState(
      isPosting: isPosting ?? this.isPosting,
      isFormPosted: isFormPosted ?? this.isFormPosted,
      currentPassword: currentPassword ?? this.currentPassword,
      newPassword: newPassword ?? this.newPassword,
      confirmNewPassword: confirmNewPassword ?? this.confirmNewPassword,
      newPasswordInput: newPasswordInput ?? this.newPasswordInput,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
