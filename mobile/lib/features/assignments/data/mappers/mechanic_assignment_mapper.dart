import 'package:mobile/features/assignments/domain/domain.dart';

class MechanicAssignmentMapper {
  static MechanicAssignment? activeAssignmentFromJson(
    Map<String, dynamic>? json,
  ) {
    if (json == null) return null;
    final assignmentJson = (json['assignment'] as Map?)
        ?.cast<String, dynamic>();
    if (assignmentJson == null) return null;
    return assignmentFromJson(assignmentJson);
  }

  static MechanicAssignment assignmentFromJson(Map<String, dynamic> json) {
    final incidentJson =
        (json['incident'] as Map?)?.cast<String, dynamic>() ??
        const <String, dynamic>{};
    final vehicleJson = (incidentJson['vehicle'] as Map?)
        ?.cast<String, dynamic>();
    final rawEvidenceUrls =
        (incidentJson['evidence_urls'] as List?) ?? const [];

    return MechanicAssignment(
      assignmentId: '${json['assignment_id'] ?? ''}',
      assignmentStatus: '${json['assignment_status'] ?? ''}',
      repairShopId: '${json['repair_shop_id'] ?? ''}',
      repairShopName: json['repair_shop_name'] as String?,
      repairShopLatitude: _asDouble(json['repair_shop_latitude']),
      repairShopLongitude: _asDouble(json['repair_shop_longitude']),
      mechanicId: '${json['mechanic_id'] ?? ''}',
      assignedAt: _asDateTime(json['assigned_at']),
      incident: MechanicAssignmentIncident(
        id: '${incidentJson['id'] ?? ''}',
        status: '${incidentJson['status'] ?? ''}',
        description: incidentJson['description'] as String?,
        address: incidentJson['address'] as String?,
        latitude: _asDouble(incidentJson['latitude']) ?? 0,
        longitude: _asDouble(incidentJson['longitude']) ?? 0,
        problemId: incidentJson['problem_id']?.toString(),
        problemName: incidentJson['problem_name'] as String?,
        distanceKm: _asDouble(incidentJson['distance_km']),
        deliveryPrice: _asDouble(incidentJson['delivery_price']),
        evidenceUrls: rawEvidenceUrls.map((item) => '$item').toList(),
        vehicle: vehicleJson == null
            ? null
            : MechanicIncidentVehicle(
                id: '${vehicleJson['id'] ?? ''}',
                make: '${vehicleJson['make'] ?? ''}',
                model: '${vehicleJson['model'] ?? ''}',
                plate: '${vehicleJson['plate'] ?? ''}',
                color: '${vehicleJson['color'] ?? ''}',
                year: _asInt(vehicleJson['year']) ?? 0,
                typeName: vehicleJson['type_name']?.toString(),
              ),
      ),
    );
  }

  static MechanicTodayStats todayStatsFromJson(Map<String, dynamic>? json) {
    final safeJson = json ?? const <String, dynamic>{};
    return MechanicTodayStats(
      completedToday: _asInt(safeJson['completed_today']) ?? 0,
      cancelledToday: _asInt(safeJson['cancelled_today']) ?? 0,
    );
  }

  static MechanicAssignmentActionResult actionResultFromJson(
    Map<String, dynamic>? json,
  ) {
    final safeJson = json ?? const <String, dynamic>{};
    return MechanicAssignmentActionResult(
      assignmentId: '${safeJson['assignment_id'] ?? ''}',
      incidentId: '${safeJson['incident_id'] ?? ''}',
      incidentStatus: '${safeJson['incident_status'] ?? ''}',
      assignmentStatus: '${safeJson['assignment_status'] ?? ''}',
      detail: '${safeJson['detail'] ?? 'Operacion completada'}',
    );
  }

  static double? _asDouble(Object? value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    return double.tryParse('$value');
  }

  static DateTime? _asDateTime(Object? value) {
    if (value == null) return null;
    final raw = '$value'.trim();
    if (raw.isEmpty) return null;
    return DateTime.tryParse(raw);
  }

  static int? _asInt(Object? value) {
    if (value == null) return null;
    if (value is int) return value;
    if (value is num) return value.toInt();
    return int.tryParse('$value');
  }
}
