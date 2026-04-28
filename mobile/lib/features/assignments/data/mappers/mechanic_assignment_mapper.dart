import 'package:mobile/features/assignments/domain/domain.dart';
import 'package:mobile/features/shared/shared.dart';

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
        clientEmail: incidentJson['client_email'] as String?,
        clientName: incidentJson['client_name'] as String?,
        clientPhone: incidentJson['client_phone'] as String?,
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
    return BoliviaDateTimeFormatter.parseServerDateTime(value);
  }

  static int? _asInt(Object? value) {
    if (value == null) return null;
    if (value is int) return value;
    if (value is num) return value.toInt();
    return int.tryParse('$value');
  }

  static List<MechanicServiceItem> serviceItemsFromJson(
    Map<String, dynamic>? json,
  ) {
    final servicesJson = (json?['services'] as List?) ?? const [];
    return servicesJson
        .whereType<Map>()
        .map((item) => item.cast<String, dynamic>())
        .map(
          (item) => MechanicServiceItem(
            assignmentId: '${item['assignment_id'] ?? ''}',
            incidentId: '${item['incident_id'] ?? ''}',
            assignmentStatus: '${item['assignment_status'] ?? ''}',
            incidentStatus: '${item['incident_status'] ?? ''}',
            createdDate:
                BoliviaDateTimeFormatter.parseServerDateTime(
                  item['created_date'],
                ) ??
                DateTime.now().toUtc(),
            updatedDate:
                BoliviaDateTimeFormatter.parseServerDateTime(
                  item['updated_date'],
                ) ??
                DateTime.now().toUtc(),
            incidentDescription: item['incident_description'] as String?,
            problemName: item['problem_name'] as String?,
            vehiclePlate: item['vehicle_plate'] as String?,
          ),
        )
        .where(
          (item) =>
              item.assignmentId.trim().isNotEmpty &&
              item.incidentId.trim().isNotEmpty,
        )
        .toList();
  }
}
