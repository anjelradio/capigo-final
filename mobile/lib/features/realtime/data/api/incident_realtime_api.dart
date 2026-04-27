import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/shared/infrastructure/errors/api_error_parser.dart';

class IncidentRealtimeApi {
  IncidentRealtimeApi({required String accessToken})
    : _accessToken = accessToken,
      _dio = Dio(
        BaseOptions(
          baseUrl: Environment.apiUrl,
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

  final Dio _dio;
  final String _accessToken;

  Future<Map<String, dynamic>> getIncidentSnapshot(String incidentId) async {
    try {
      final response = await _dio.get(
        '/realtime/incidents/$incidentId/snapshot',
      );
      final data = response.data;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return data.cast<String, dynamic>();
      throw CustomError('Respuesta invalida del servidor');
    } on DioException catch (error) {
      final messages = parseApiErrors(error.response?.data);
      if (messages.isNotEmpty) {
        throw CustomError.multiple(messages);
      }
      throw CustomError('No fue posible cargar el estado en tiempo real.');
    } catch (_) {
      throw CustomError('No fue posible cargar el estado en tiempo real.');
    }
  }

  Future<WebSocket> connectIncidentChannel(String incidentId) {
    final wsUrl = _buildIncidentWsUrl(incidentId);
    return WebSocket.connect(wsUrl);
  }

  String _buildIncidentWsUrl(String incidentId) {
    final apiUri = Uri.parse(Environment.apiUrl);
    final wsScheme = apiUri.scheme == 'https' ? 'wss' : 'ws';
    final baseSegments = apiUri.pathSegments.where(
      (segment) => segment.isNotEmpty,
    );
    final wsSegments = [
      ...baseSegments,
      'realtime',
      'ws',
      'incidents',
      incidentId,
    ];

    final uri = apiUri.replace(
      scheme: wsScheme,
      pathSegments: wsSegments,
      queryParameters: {'token': _accessToken},
    );

    return uri.toString();
  }

  Map<String, dynamic>? tryDecodeSocketMessage(dynamic rawMessage) {
    if (rawMessage is! String) return null;
    try {
      final parsed = jsonDecode(rawMessage);
      if (parsed is Map<String, dynamic>) return parsed;
      if (parsed is Map) return parsed.cast<String, dynamic>();
      return null;
    } catch (_) {
      return null;
    }
  }
}
