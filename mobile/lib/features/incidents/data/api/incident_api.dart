import 'package:dio/dio.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/shared/infrastructure/errors/api_error_parser.dart';

class IncidentApi {
  late final Dio dio;

  IncidentApi({required String accessToken})
    : dio = Dio(
        BaseOptions(
          baseUrl: Environment.apiUrl,
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

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

  Future<void> createIncident({
    required String vehicleId,
    String? description,
    String? audioPath,
    required double latitude,
    required double longitude,
    required List<String> imagePaths,
  }) async {
    try {
      final photos = <MultipartFile>[];
      for (final path in imagePaths) {
        photos.add(await MultipartFile.fromFile(path));
      }

      final payload = FormData.fromMap({
        'vehicle_id': vehicleId,
        if ((description ?? '').trim().isNotEmpty) 'description': description,
        if ((audioPath ?? '').trim().isNotEmpty)
          'audio': await MultipartFile.fromFile(audioPath!),
        'latitude': latitude,
        'longitude': longitude,
        'photos': photos,
      });

      await dio.post('/incidents', data: payload);
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible enviar el incidente');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible enviar el incidente');
    }
  }

  Future<Map<String, dynamic>?> getActiveIncidentDetail() async {
    try {
      final response = await dio.get('/incidents/me/active');
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar el servicio activo');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar el servicio activo');
    }
  }

  Future<Map<String, dynamic>?> submitIncidentFeedback({
    required String incidentId,
    required int rating,
    String? comment,
  }) async {
    try {
      final response = await dio.post(
        '/incidents/$incidentId/feedback',
        data: {
          'rating': rating,
          'comment': comment?.trim().isEmpty == true ? null : comment?.trim(),
        },
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(
        e,
        'No fue posible enviar la calificacion del servicio',
      );
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible enviar la calificacion del servicio');
    }
  }

  Future<Map<String, dynamic>?> getPendingFeedbackReminders() async {
    try {
      final response = await dio.get('/incidents/me/feedback/pending');
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(
        e,
        'No fue posible cargar recordatorios de calificacion',
      );
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar recordatorios de calificacion');
    }
  }

  Future<Map<String, dynamic>?> getCompletedServices() async {
    try {
      final response = await dio.get('/incidents/me/services/completed');
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar servicios realizados');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar servicios realizados');
    }
  }

  Future<Map<String, dynamic>?> getServicesHistory() async {
    try {
      final response = await dio.get('/incidents/me/services/history');
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar historial de servicios');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar historial de servicios');
    }
  }

  Future<Map<String, dynamic>?> getServiceDetail({
    required String incidentId,
  }) async {
    try {
      final response = await dio.get(
        '/incidents/me/services/$incidentId/detail',
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar el detalle del servicio');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar el detalle del servicio');
    }
  }
}
