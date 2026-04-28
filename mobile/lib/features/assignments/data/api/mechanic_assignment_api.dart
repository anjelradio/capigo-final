import 'package:dio/dio.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/shared/infrastructure/errors/api_error_parser.dart';

class MechanicAssignmentApi {
  MechanicAssignmentApi({required String accessToken})
    : dio = Dio(
        BaseOptions(
          baseUrl: Environment.apiUrl,
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

  final Dio dio;

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

  Future<Map<String, dynamic>?> getMyActiveAssignment() async {
    try {
      final response = await dio.get('/assignments/me/mechanic/active');
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar tu servicio activo');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar tu servicio activo');
    }
  }

  Future<Map<String, dynamic>?> getAssignmentDetail(String assignmentId) async {
    try {
      final response = await dio.get(
        '/assignments/me/mechanic/assignments/$assignmentId',
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

  Future<Map<String, dynamic>?> updateAssignmentStatus({
    required String assignmentId,
    required String status,
  }) async {
    try {
      final response = await dio.post(
        '/assignments/me/mechanic/assignments/$assignmentId/status',
        data: {'status': status},
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(
        e,
        'No fue posible actualizar el estado del servicio',
      );
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible actualizar el estado del servicio');
    }
  }

  Future<Map<String, dynamic>?> completeAssignment({
    required String assignmentId,
    required String description,
    required double laborPrice,
  }) async {
    try {
      final response = await dio.post(
        '/assignments/me/mechanic/assignments/$assignmentId/complete',
        data: {'description': description, 'labor_price': laborPrice},
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(
        e,
        'No fue posible completar el servicio con reporte final',
      );
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError(
        'No fue posible completar el servicio con reporte final',
      );
    }
  }

  Future<Map<String, dynamic>?> updateAssignmentLocation({
    required String assignmentId,
    required double latitude,
    required double longitude,
    DateTime? recordedAt,
  }) async {
    try {
      final response = await dio.post(
        '/assignments/me/mechanic/assignments/$assignmentId/location',
        data: {
          'latitude': latitude,
          'longitude': longitude,
          if (recordedAt != null)
            'recorded_at': recordedAt.toUtc().toIso8601String(),
        },
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible actualizar tu ubicacion');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible actualizar tu ubicacion');
    }
  }

  Future<Map<String, dynamic>?> getTodayStats() async {
    try {
      final response = await dio.get('/assignments/me/mechanic/stats/today');
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar metricas de hoy');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar metricas de hoy');
    }
  }

  Future<Map<String, dynamic>?> getCompletedServices() async {
    try {
      final response = await dio.get(
        '/assignments/me/mechanic/services/completed',
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar servicios completados');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar servicios completados');
    }
  }

  Future<Map<String, dynamic>?> getServicesHistory() async {
    try {
      final response = await dio.get(
        '/assignments/me/mechanic/services/history',
      );
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

  Future<Map<String, dynamic>?> getIncidentDetail(String incidentId) async {
    try {
      final response = await dio.get(
        '/assignments/me/mechanic/incidents/$incidentId/detail',
      );
      final data = response.data;
      if (data == null) return null;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      return null;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar el detalle del incidente');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar el detalle del incidente');
    }
  }
}
