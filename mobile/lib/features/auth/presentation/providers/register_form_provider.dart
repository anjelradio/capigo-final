import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/presentation/providers/auth_provider.dart';
import 'package:mobile/features/shared/shared.dart';

final registerFormProvider =
    StateNotifierProvider.autoDispose<RegisterFormNotifier, RegisterFormState>((
      ref,
    ) {
      final registerUserCallback = ref
          .watch(authProvider.notifier)
          .registerUser;
      return RegisterFormNotifier(registerUserCallback: registerUserCallback);
    });

class RegisterFormNotifier extends StateNotifier<RegisterFormState> {
  final Function(String, String, String, String, String) registerUserCallback;

  RegisterFormNotifier({required this.registerUserCallback})
    : super(RegisterFormState());

  void onFirstNameChange(String value) {
    final newFirstName = Name.dirty(value);
    state = state.copyWith(
      firstName: newFirstName,
      isValid: Formz.validate([
        newFirstName,
        state.lastName,
        state.email,
        state.password,
      ]),
    );
  }

  void onLastNameChange(String value) {
    final newLastName = Name.dirty(value);
    state = state.copyWith(
      lastName: newLastName,
      isValid: Formz.validate([
        state.firstName,
        newLastName,
        state.email,
        state.password,
      ]),
    );
  }

  void onEmailChange(String value) {
    final newEmail = Email.dirty(value);
    state = state.copyWith(
      email: newEmail,
      isValid: Formz.validate([
        state.firstName,
        state.lastName,
        newEmail,
        state.password,
      ]),
    );
  }

  void onPasswordChange(String value) {
    final newPassword = Password.dirty(value);
    state = state.copyWith(
      password: newPassword,
      isValid: Formz.validate([
        state.firstName,
        state.lastName,
        state.email,
        newPassword,
      ]),
    );
  }

  void onPhoneChange(String value) {
    final newPhone = Phone.dirty(value);

    state = state.copyWith(
      phone: newPhone,
      isValid: Formz.validate([
        state.firstName,
        state.lastName,
        state.email,
        state.password,
        newPhone,
      ]),
    );
  }

  void onFormSubmit() async {
    _touchEveryField();
    if (!state.isValid) return;

    state = state.copyWith(isPosting: true);
    await registerUserCallback(
      state.firstName.value,
      state.lastName.value,
      state.email.value,
      state.password.value,
      state.phone.value,
    );
    state = state.copyWith(isPosting: false);
  }

  void _touchEveryField() {
    final firstName = Name.dirty(state.firstName.value);
    final lastName = Name.dirty(state.lastName.value);
    final email = Email.dirty(state.email.value);
    final password = Password.dirty(state.password.value);
    final phone = Phone.dirty(state.phone.value);
    state = state.copyWith(
      isFormPosted: true,
      firstName: firstName,
      lastName: lastName,
      email: email,
      password: password,
      phone: phone,
      isValid: Formz.validate([firstName, lastName, email, password, phone]),
    );
  }
}

class RegisterFormState {
  final bool isPosting;
  final bool isFormPosted;
  final bool isValid;
  final Name firstName;
  final Name lastName;
  final Email email;
  final Password password;
  final Phone phone;

  RegisterFormState({
    this.isPosting = false,
    this.isFormPosted = false,
    this.isValid = false,
    this.firstName = const Name.pure(),
    this.lastName = const Name.pure(),
    this.email = const Email.pure(),
    this.password = const Password.pure(),
    this.phone = const Phone.pure(),
  });

  RegisterFormState copyWith({
    bool? isPosting,
    bool? isFormPosted,
    bool? isValid,
    Name? firstName,
    Name? lastName,
    Email? email,
    Password? password,
    Phone? phone,
  }) => RegisterFormState(
    isPosting: isPosting ?? this.isPosting,
    isFormPosted: isFormPosted ?? this.isFormPosted,
    isValid: isValid ?? this.isValid,
    firstName: firstName ?? this.firstName,
    lastName: lastName ?? this.lastName,
    email: email ?? this.email,
    password: password ?? this.password,
    phone: phone ?? this.phone,
  );
}
