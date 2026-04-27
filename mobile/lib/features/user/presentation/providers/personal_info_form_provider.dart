import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/user_providers.dart';

final personalInfoFormProvider =
    StateNotifierProvider.autoDispose<
      PersonalInfoFormNotifier,
      PersonalInfoFormState
    >((ref) {
      final userRepository = ref.watch(userRepositoryProvider);
      final authNotifier = ref.read(authProvider.notifier);

      Future<void> submitProfile(
        String firstName,
        String lastName,
        String phone,
      ) async {
        final updatedUser = await userRepository.updateProfile(
          firstName: firstName,
          lastName: lastName,
          phone: phone,
        );

        authNotifier.syncUser(updatedUser);
      }

      return PersonalInfoFormNotifier(submitProfileCallback: submitProfile);
    });

class PersonalInfoFormNotifier extends StateNotifier<PersonalInfoFormState> {
  PersonalInfoFormNotifier({required this.submitProfileCallback})
    : super(PersonalInfoFormState());

  final Future<void> Function(String, String, String) submitProfileCallback;

  void setInitialValues({
    required String firstName,
    required String lastName,
    required String phone,
  }) {
    final firstNameInput = Name.dirty(firstName);
    final lastNameInput = Name.dirty(lastName);
    final phoneInput = Phone.dirty(phone);

    state = state.copyWith(
      firstName: firstNameInput,
      lastName: lastNameInput,
      phone: phoneInput,
      isFormPosted: false,
      errorMessages: const [],
      isValid: Formz.validate([firstNameInput, lastNameInput, phoneInput]),
    );
  }

  void onFirstNameChange(String value) {
    final firstNameInput = Name.dirty(value);

    state = state.copyWith(
      firstName: firstNameInput,
      errorMessages: const [],
      isValid: Formz.validate([firstNameInput, state.lastName, state.phone]),
    );
  }

  void onLastNameChange(String value) {
    final lastNameInput = Name.dirty(value);

    state = state.copyWith(
      lastName: lastNameInput,
      errorMessages: const [],
      isValid: Formz.validate([state.firstName, lastNameInput, state.phone]),
    );
  }

  void onPhoneChange(String value) {
    final phoneInput = Phone.dirty(value);

    state = state.copyWith(
      phone: phoneInput,
      errorMessages: const [],
      isValid: Formz.validate([state.firstName, state.lastName, phoneInput]),
    );
  }

  Future<bool> submit() async {
    _touchEveryField();
    if (!state.isValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await submitProfileCallback(
        state.firstName.value.trim(),
        state.lastName.value.trim(),
        state.phone.value.trim(),
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
        errorMessages: const ['No fue posible actualizar la informacion'],
      );
      return false;
    }
  }

  void _touchEveryField() {
    final firstNameInput = Name.dirty(state.firstName.value);
    final lastNameInput = Name.dirty(state.lastName.value);
    final phoneInput = Phone.dirty(state.phone.value);

    state = state.copyWith(
      firstName: firstNameInput,
      lastName: lastNameInput,
      phone: phoneInput,
      isFormPosted: true,
      isValid: Formz.validate([firstNameInput, lastNameInput, phoneInput]),
    );
  }
}

class PersonalInfoFormState {
  PersonalInfoFormState({
    this.isPosting = false,
    this.isFormPosted = false,
    this.isValid = false,
    this.firstName = const Name.pure(),
    this.lastName = const Name.pure(),
    this.phone = const Phone.pure(),
    this.errorMessages = const [],
  });

  final bool isPosting;
  final bool isFormPosted;
  final bool isValid;
  final Name firstName;
  final Name lastName;
  final Phone phone;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  PersonalInfoFormState copyWith({
    bool? isPosting,
    bool? isFormPosted,
    bool? isValid,
    Name? firstName,
    Name? lastName,
    Phone? phone,
    List<String>? errorMessages,
  }) {
    return PersonalInfoFormState(
      isPosting: isPosting ?? this.isPosting,
      isFormPosted: isFormPosted ?? this.isFormPosted,
      isValid: isValid ?? this.isValid,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      phone: phone ?? this.phone,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
