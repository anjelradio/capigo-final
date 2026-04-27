import 'package:dio/dio.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';

class UserApi {
  UserApi({required KeyValueStorageService keyValueStorageService, Dio? dio})
    : _keyValueStorageService = keyValueStorageService,
      _dio = dio ?? Dio(BaseOptions(baseUrl: Environment.apiUrl));

  final Dio _dio;
  final KeyValueStorageService _keyValueStorageService;

  Future<String> _getToken() async {
    final token = await _keyValueStorageService.getValue<String>('token');
    if (token == null || token.isEmpty) {
      throw CustomError('No hay sesion activa');
    }
    return token;
  }

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

  Options _authorized(String token, {ResponseType? responseType}) {
    return Options(
      headers: {'Authorization': 'Bearer $token'},
      responseType: responseType,
    );
  }

  Future<User> updateProfile({
    required String firstName,
    required String lastName,
    required String phone,
  }) async {
    final token = await _getToken();

    try {
      final response = await _dio.patch(
        '/user/me/profile',
        data: {'first_name': firstName, 'last_name': lastName, 'phone': phone},
        options: _authorized(token),
      );

      if (response.data is! Map<String, dynamic>) {
        throw CustomError('Respuesta invalida del servidor');
      }

      return UserMapper.userJsonWithoutTokenToEntity(
        response.data as Map<String, dynamic>,
        token: token,
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible actualizar la informacion');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible actualizar la informacion');
    }
  }

  Future<void> updatePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmNewPassword,
  }) async {
    final token = await _getToken();

    try {
      await _dio.patch(
        '/user/me/password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
          'confirm_new_password': confirmNewPassword,
        },
        options: _authorized(token, responseType: ResponseType.plain),
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible actualizar la contraseña');
    } catch (_) {
      throw CustomError('No fue posible actualizar la contraseña');
    }
  }

  Future<void> requestEmailChangeOtp() async {
    final token = await _getToken();

    try {
      await _dio.post(
        '/user/me/email/change/request-otp',
        data: const {},
        options: _authorized(token, responseType: ResponseType.plain),
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible enviar el codigo OTP');
    } catch (_) {
      throw CustomError('No fue posible enviar el codigo OTP');
    }
  }

  Future<String> verifyEmailChangeOtp(String otp) async {
    final token = await _getToken();

    try {
      final response = await _dio.post(
        '/user/me/email/change/verify-otp',
        data: {'otp': otp},
        options: _authorized(token),
      );

      final responseData = response.data;
      if (responseData is Map && responseData['change_email_token'] is String) {
        return responseData['change_email_token'] as String;
      }

      throw CustomError('Respuesta invalida del servidor');
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible verificar el codigo OTP');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible verificar el codigo OTP');
    }
  }

  Future<User> updateEmail({
    required String newEmail,
    required String changeEmailToken,
  }) async {
    final token = await _getToken();

    try {
      final response = await _dio.patch(
        '/user/me/email',
        data: {'new_email': newEmail, 'change_email_token': changeEmailToken},
        options: _authorized(token),
      );

      if (response.data is! Map<String, dynamic>) {
        throw CustomError('Respuesta invalida del servidor');
      }

      return UserMapper.userJsonWithoutTokenToEntity(
        response.data as Map<String, dynamic>,
        token: token,
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible actualizar el correo');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible actualizar el correo');
    }
  }

  Future<User> joinShopByCode(String code) async {
    final token = await _getToken();

    try {
      final response = await _dio.post(
        '/repair-shop/me/join',
        data: {'code': code.trim().toUpperCase()},
        options: _authorized(token),
      );

      if (response.data is! Map<String, dynamic>) {
        throw CustomError('Respuesta invalida del servidor');
      }

      return UserMapper.userJsonWithoutTokenToEntity(
        response.data as Map<String, dynamic>,
        token: token,
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible unirse al taller');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible unirse al taller');
    }
  }

  Future<User> unlinkFromShop() async {
    final token = await _getToken();

    try {
      final response = await _dio.post(
        '/repair-shop/me/unlink',
        data: const {},
        options: _authorized(token),
      );

      if (response.data is! Map<String, dynamic>) {
        throw CustomError('Respuesta invalida del servidor');
      }

      return UserMapper.userJsonWithoutTokenToEntity(
        response.data as Map<String, dynamic>,
        token: token,
      );
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible desvincularte del taller');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible desvincularte del taller');
    }
  }
}
