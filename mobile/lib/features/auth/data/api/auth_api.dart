import 'package:dio/dio.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';

class AuthApi {
  AuthApi({Dio? dio})
    : _dio = dio ?? Dio(BaseOptions(baseUrl: Environment.apiUrl));

  final Dio _dio;

  Never _throwParsedDioError(DioException error, String fallbackMessage) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.connectionError) {
      throw CustomError('Revisa tu conexion a internet');
    }

    final messages = parseApiErrors(error.response?.data);
    if (messages.isNotEmpty) {
      throw CustomError.multiple(messages);
    }

    throw CustomError(fallbackMessage);
  }

  Future<User> checkAuthStatus(String token) async {
    try {
      final response = await _dio.post(
        '/auth/check-status',
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );

      return UserMapper.userJsonToEntity(response.data);
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible validar la sesion');
    } catch (_) {
      throw CustomError('No fue posible validar la sesion');
    }
  }

  Future<User> login(String email, String password) async {
    try {
      final response = await _dio.post(
        'auth/login',
        data: {'email': email, 'password': password},
      );
      return UserMapper.userJsonToEntity(response.data);
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible iniciar sesion');
    } catch (_) {
      throw CustomError('No fue posible iniciar sesion');
    }
  }

  Future<User> register(
    String firstName,
    String lastName,
    String email,
    String password,
    String phone,
  ) async {
    try {
      final response = await _dio.post(
        'auth/register',
        data: {
          'first_name': firstName,
          'last_name': lastName,
          'email': email,
          'password': password,
          'phone': phone,
        },
      );
      return UserMapper.userJsonToEntity(response.data);
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible registrarse');
    } catch (_) {
      throw CustomError('No fue posible registrarse');
    }
  }

  Future<void> requestPasswordResetOtp(String email) async {
    try {
      await _dio.post('/auth/password/request-otp', data: {'email': email});
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible enviar el codigo OTP');
    } catch (_) {
      throw CustomError('No fue posible enviar el codigo OTP');
    }
  }

  Future<void> verifyPasswordResetOtp(String email, String otp) async {
    try {
      await _dio.post(
        '/auth/password/verify-otp',
        data: {'email': email, 'otp': otp},
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible verificar el codigo OTP');
    } catch (_) {
      throw CustomError('No fue posible verificar el codigo OTP');
    }
  }
}
