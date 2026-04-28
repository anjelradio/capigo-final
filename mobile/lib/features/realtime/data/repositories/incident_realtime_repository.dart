import 'dart:io';

import 'package:mobile/features/realtime/data/api/incident_realtime_api.dart';
import 'package:mobile/features/realtime/domain/domain.dart';
import 'package:mobile/features/shared/shared.dart';

class IncidentRealtimeRepository {
  IncidentRealtimeRepository({required IncidentRealtimeApi realtimeApi})
    : _realtimeApi = realtimeApi;

  final IncidentRealtimeApi _realtimeApi;

  Future<IncidentRealtimeSnapshot> getIncidentSnapshot(
    String incidentId,
  ) async {
    final json = await _realtimeApi.getIncidentSnapshot(incidentId);
    final snapshotJson =
        (json['snapshot'] as Map?)?.cast<String, dynamic>() ?? const {};

    return IncidentRealtimeSnapshot(
      incidentId: '${json['incident_id'] ?? incidentId}',
      status: '${snapshotJson['status'] ?? 'pending'}',
      assignmentId: snapshotJson['assignment_id']?.toString(),
      repairShopId: snapshotJson['repair_shop_id']?.toString(),
      mechanicId: snapshotJson['mechanic_id']?.toString(),
      mechanicLatitude: _asDouble(snapshotJson['mechanic_latitude']),
      mechanicLongitude: _asDouble(snapshotJson['mechanic_longitude']),
      mechanicLocationUpdatedAt: _asDateTime(
        snapshotJson['mechanic_location_updated_at'],
      ),
      lastEventAt: _asDateTime(snapshotJson['last_event_at']),
    );
  }

  Future<WebSocket> connectIncidentChannel(String incidentId) {
    return _realtimeApi.connectIncidentChannel(incidentId);
  }

  IncidentRealtimeSnapshot? mapSnapshotFromSocket(dynamic rawMessage) {
    final json = _realtimeApi.tryDecodeSocketMessage(rawMessage);
    if (json == null) return null;
    if ('${json['type'] ?? ''}' != 'incident.snapshot') return null;

    final payload = (json['payload'] as Map?)?.cast<String, dynamic>();
    if (payload == null) return null;
    final snapshotJson =
        (payload['snapshot'] as Map?)?.cast<String, dynamic>() ?? const {};

    return IncidentRealtimeSnapshot(
      incidentId: '${payload['incident_id'] ?? ''}',
      status: '${snapshotJson['status'] ?? 'pending'}',
      assignmentId: snapshotJson['assignment_id']?.toString(),
      repairShopId: snapshotJson['repair_shop_id']?.toString(),
      mechanicId: snapshotJson['mechanic_id']?.toString(),
      mechanicLatitude: _asDouble(snapshotJson['mechanic_latitude']),
      mechanicLongitude: _asDouble(snapshotJson['mechanic_longitude']),
      mechanicLocationUpdatedAt: _asDateTime(
        snapshotJson['mechanic_location_updated_at'],
      ),
      lastEventAt: _asDateTime(snapshotJson['last_event_at']),
    );
  }

  IncidentRealtimeEvent? mapRealtimeEvent(dynamic rawMessage) {
    final json = _realtimeApi.tryDecodeSocketMessage(rawMessage);
    if (json == null) return null;

    final type = '${json['type'] ?? ''}'.trim();
    if (type.isEmpty || type == 'incident.snapshot') return null;

    final meta = (json['meta'] as Map?)?.cast<String, dynamic>();
    if (meta == null) return null;

    final payload =
        (json['payload'] as Map?)?.cast<String, dynamic>() ?? const {};

    return IncidentRealtimeEvent(
      id: '${meta['event_id'] ?? ''}',
      type: type,
      createdAt: _asDateTime(meta['created_at']) ?? DateTime.now(),
      payload: payload,
    );
  }

  static double? _asDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    return double.tryParse('$value');
  }

  static DateTime? _asDateTime(dynamic value) {
    return BoliviaDateTimeFormatter.parseServerDateTime(value);
  }
}
