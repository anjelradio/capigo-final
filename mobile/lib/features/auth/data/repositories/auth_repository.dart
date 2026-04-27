import 'package:mobile/features/auth/auth.dart';

class AuthRepository {
  AuthRepository({required AuthApi authApi}) : _authApi = authApi;
  final AuthApi _authApi;

  Future<User> login(String email, String password) {
    return _authApi.login(email, password);
  }

  Future<User> register(
    String firstName,
    String lastName,
    String email,
    String password,
    String phone,
  ) {
    return _authApi.register(firstName, lastName, email, password, phone);
  }

  Future<User> checkAuthStatus(String token) {
    return _authApi.checkAuthStatus(token);
  }

  Future<void> requestPasswordResetOtp(String email) {
    return _authApi.requestPasswordResetOtp(email);
  }

  Future<void> verifyPasswordResetOtp(String email, String otp) {
    return _authApi.verifyPasswordResetOtp(email, otp);
  }
}
