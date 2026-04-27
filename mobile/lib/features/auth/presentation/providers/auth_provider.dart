import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';

// 3
final keyValueStorageProvider = Provider<KeyValueStorageService>((ref) {
  return KeyValueStorageServiceImpl();
});

final authApiProvider = Provider<AuthApi>((ref) {
  return AuthApi();
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final authApi = ref.watch(authApiProvider);
  return AuthRepository(authApi: authApi);
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  final keyValueStorageService = ref.watch(keyValueStorageProvider);
  return AuthNotifier(
    authRepository: authRepository,
    keyValueStorageService: keyValueStorageService,
  );
});

// 2 - Notifier

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository authRepository;
  final KeyValueStorageService keyValueStorageService;
  AuthNotifier({
    required this.authRepository,
    required this.keyValueStorageService,
  }) : super(AuthState()) {
    checkAuthStatus();
  }
  void checkAuthStatus() async {
    final token = await keyValueStorageService.getValue<String>('token');

    if (token == null) return logout();

    try {
      final user = await authRepository.checkAuthStatus(token);
      _setLoggedUser(user);
    } catch (e) {
      logout();
    }
  }

  Future<void> loginUser(String email, String password) async {
    try {
      final user = await authRepository.login(email, password);

      if (_isWebOnlyRole(user.role)) {
        await logoutWithErrors([
          'Este usuario debe ingresar desde la pagina web.',
        ]);
        return;
      }

      _setLoggedUser(user);
    } on CustomError catch (e) {
      logoutWithErrors(e.messages);
    } catch (e) {
      logout('Error al iniciar sesion');
    }
  }

  Future<void> registerUser(
    String firstName,
    String lastName,
    String email,
    String password,
    String phone,
  ) async {
    await Future.delayed(const Duration(milliseconds: 500));

    try {
      final user = await authRepository.register(
        firstName,
        lastName,
        email,
        password,
        phone,
      );
      _setLoggedUser(user);
    } on CustomError catch (e) {
      logoutWithErrors(e.messages);
    } catch (e) {
      logout('Error al registrarse');
    }
  }

  Future<void> requestPasswordResetOtp(String email) {
    return authRepository.requestPasswordResetOtp(email);
  }

  Future<void> verifyPasswordResetOtp(String email, String otp) {
    return authRepository.verifyPasswordResetOtp(email, otp);
  }

  void syncUser(User updatedUser) {
    state = state.copyWith(user: updatedUser, errorMessages: const []);
  }

  void updateProfileData({
    required String firstName,
    required String lastName,
    required String phone,
  }) {
    final currentUser = state.user;
    if (currentUser == null) return;

    state = state.copyWith(
      user: currentUser.copyWith(
        firstName: firstName,
        lastName: lastName,
        phone: phone,
      ),
    );
  }

  void updateUserEmail(String email) {
    final currentUser = state.user;
    if (currentUser == null) return;

    state = state.copyWith(user: currentUser.copyWith(email: email));
  }

  void _setLoggedUser(User user) async {
    if (_isWebOnlyRole(user.role)) {
      await logoutWithErrors([
        'Este usuario debe ingresar desde la pagina web.',
      ]);
      return;
    }

    await keyValueStorageService.setKeyValue('token', user.token);
    state = state.copyWith(
      user: user,
      authStatus: AuthStatus.authenticated,
      errorMessages: const [],
    );
  }

  Future<void> logoutWithErrors(List<String> errorMessages) async {
    await keyValueStorageService.removeKey('token');
    state = state.copyWith(
      authStatus: AuthStatus.notAuthenticated,
      user: null,
      errorMessages: errorMessages,
    );
  }

  Future<void> logout([String? errorMessage]) async {
    await keyValueStorageService.removeKey('token');
    state = state.copyWith(
      authStatus: AuthStatus.notAuthenticated,

      user: null,
      errorMessages: errorMessage == null ? const [] : [errorMessage],
    );
  }

  bool _isWebOnlyRole(String role) {
    final normalizedRole = role.trim().toLowerCase();
    return normalizedRole == 'admin' || normalizedRole == 'owner';
  }
}
// 1 - State del provider

enum AuthStatus { checking, authenticated, notAuthenticated }

class AuthState {
  final AuthStatus authStatus;
  final User? user;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  AuthState({
    this.authStatus = AuthStatus.checking,
    this.user,
    this.errorMessages = const [],
  });

  AuthState copyWith({
    AuthStatus? authStatus,
    User? user,
    List<String>? errorMessages,
  }) => AuthState(
    authStatus: authStatus ?? this.authStatus,
    user: user ?? this.user,
    errorMessages: errorMessages ?? this.errorMessages,
  );
}
