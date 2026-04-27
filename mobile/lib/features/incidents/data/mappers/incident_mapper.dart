import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/user/domain/domain.dart';

class IncidentMapper {
  static ActiveIncidentDetail activeIncidentJsonToEntity(
    Map<String, dynamic> json,
  ) {
    final incidentJson =
        (json['incident'] as Map?)?.cast<String, dynamic>() ?? {};
    final vehicleJson =
        (json['vehicle'] as Map?)?.cast<String, dynamic>() ?? {};
    final evidenceJsonList = (json['evidences'] as List?) ?? const [];
    final assignmentJson = (json['assignment'] as Map?)
        ?.cast<String, dynamic>();

    return ActiveIncidentDetail(
      incident: ActiveIncidentCore(
        id: '${incidentJson['id'] ?? ''}',
        description: incidentJson['description'] as String?,
        status: '${incidentJson['status'] ?? ''}',
        priority: '${incidentJson['priority'] ?? ''}',
        latitude: _asDouble(incidentJson['latitude']) ?? 0,
        longitude: _asDouble(incidentJson['longitude']) ?? 0,
        deliveryPrice: _asDouble(incidentJson['delivery_price']),
        distanceKm: _asDouble(incidentJson['distance_km']),
        createdDate:
            DateTime.tryParse('${incidentJson['created_date'] ?? ''}') ??
            DateTime.now(),
      ),
      vehicle: Vehicle.fromJson(vehicleJson),
      evidences: evidenceJsonList
          .whereType<Map>()
          .map((item) => item.cast<String, dynamic>())
          .map(
            (item) => IncidentEvidence(
              id: '${item['id'] ?? ''}',
              url: '${item['url'] ?? ''}',
            ),
          )
          .toList(),
      assignment: assignmentJson == null
          ? null
          : ActiveIncidentAssignment(
              requestAssignmentId:
                  '${assignmentJson['request_assignment_id'] ?? ''}',
              status: '${assignmentJson['status'] ?? ''}',
              repairShopId: '${assignmentJson['repair_shop_id'] ?? ''}',
              repairShopName: assignmentJson['repair_shop_name'] as String?,
              repairShopLatitude: _asDouble(
                assignmentJson['repair_shop_latitude'],
              ),
              repairShopLongitude: _asDouble(
                assignmentJson['repair_shop_longitude'],
              ),
              mechanicId: assignmentJson['mechanic_id']?.toString(),
            ),
    );
  }

  static double? _asDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    return double.tryParse('$value');
  }
}
