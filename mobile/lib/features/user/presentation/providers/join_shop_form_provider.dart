import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/user_providers.dart';

final joinShopFormProvider =
    StateNotifierProvider.autoDispose<JoinShopFormNotifier, JoinShopFormState>((
      ref,
    ) {
      final userRepository = ref.watch(userRepositoryProvider);
      final authNotifier = ref.read(authProvider.notifier);

      Future<User> submitJoinCode(String code) async {
        final updatedUser = await userRepository.joinShopByCode(code);
        authNotifier.syncUser(updatedUser);
        return updatedUser;
      }

      return JoinShopFormNotifier(onSubmitCallback: submitJoinCode);
    });

class JoinShopFormNotifier extends StateNotifier<JoinShopFormState> {
  JoinShopFormNotifier({required this.onSubmitCallback})
    : super(JoinShopFormState());

  final Future<User> Function(String code) onSubmitCallback;

  void onCodeChanged(String value) {
    final code = JoinCode.dirty(value);
    state = state.copyWith(
      code: code,
      errorMessages: const [],
      isValid: code.isValid,
    );
  }

  Future<bool> submit() async {
    _touchCode();
    if (!state.isValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await onSubmitCallback(state.code.value);
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
        errorMessages: const ['No fue posible unirse al taller'],
      );
      return false;
    }
  }

  void reset() {
    state = JoinShopFormState();
  }

  void _touchCode() {
    final code = JoinCode.dirty(state.code.value);
    state = state.copyWith(
      code: code,
      isFormPosted: true,
      isValid: code.isValid,
    );
  }
}

class JoinShopFormState {
  JoinShopFormState({
    this.code = const JoinCode.pure(),
    this.isPosting = false,
    this.isFormPosted = false,
    this.isValid = false,
    this.errorMessages = const [],
  });

  final JoinCode code;
  final bool isPosting;
  final bool isFormPosted;
  final bool isValid;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  JoinShopFormState copyWith({
    JoinCode? code,
    bool? isPosting,
    bool? isFormPosted,
    bool? isValid,
    List<String>? errorMessages,
  }) {
    return JoinShopFormState(
      code: code ?? this.code,
      isPosting: isPosting ?? this.isPosting,
      isFormPosted: isFormPosted ?? this.isFormPosted,
      isValid: isValid ?? this.isValid,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
