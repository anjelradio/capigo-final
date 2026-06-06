import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/shared/shared.dart';
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
            BoliviaDateTimeFormatter.parseServerDateTime(
              incidentJson['created_date'],
            ) ??
            DateTime.now().toUtc(),
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
              mechanicName: assignmentJson['mechanic_name'] as String?,
              mechanicPhone: assignmentJson['mechanic_phone'] as String?,
              estimatedMinutes: _asInt(assignmentJson['estimated_minutes']),
              quotedPrice: _asDouble(assignmentJson['quoted_price']),
              finalPrice: _asDouble(assignmentJson['final_price']),
            ),
    );
  }

  static PaymentCheckoutSession paymentCheckoutSessionFromJson(
    Map<String, dynamic>? json,
  ) {
    final payload = json ?? const <String, dynamic>{};
    return PaymentCheckoutSession(
      paymentId: '${payload['payment_id'] ?? ''}',
      checkoutSessionId: '${payload['checkout_session_id'] ?? ''}',
      checkoutUrl: '${payload['checkout_url'] ?? ''}',
      amount: _asDouble(payload['amount']) ?? 0,
      currency: '${payload['currency'] ?? ''}',
      status: '${payload['status'] ?? ''}',
    );
  }

  static double? _asDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    return double.tryParse('$value');
  }

  static int? _asInt(dynamic value) {
    if (value == null) return null;
    if (value is int) return value;
    if (value is num) return value.toInt();
    return int.tryParse('$value');
  }

  static List<PendingFeedbackReminder> pendingFeedbackRemindersFromJson(
    Map<String, dynamic>? json,
  ) {
    final remindersJson = (json?['reminders'] as List?) ?? const [];
    return remindersJson
        .whereType<Map>()
        .map((item) => item.cast<String, dynamic>())
        .map(
          (item) => PendingFeedbackReminder(
            incidentId: '${item['incident_id'] ?? ''}',
            description: (item['description'] as String?)?.trim() ?? '',
            problemName: item['problem_name'] as String?,
            completedAt: BoliviaDateTimeFormatter.parseServerDateTime(
              item['completed_at'],
            ),
          ),
        )
        .where((reminder) => reminder.incidentId.trim().isNotEmpty)
        .toList();
  }

  static List<ClientServiceItem> clientServiceItemsFromJson(
    Map<String, dynamic>? json,
  ) {
    final servicesJson = (json?['services'] as List?) ?? const [];
    return servicesJson
        .whereType<Map>()
        .map((item) => item.cast<String, dynamic>())
        .map(
          (item) => ClientServiceItem(
            incidentId: '${item['incident_id'] ?? ''}',
            status: '${item['status'] ?? ''}',
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
            description: item['description'] as String?,
            problemName: item['problem_name'] as String?,
            vehiclePlate: item['vehicle_plate'] as String?,
          ),
        )
        .where((item) => item.incidentId.trim().isNotEmpty)
        .toList();
  }

  static ClientServiceDetail clientServiceDetailFromJson(
    Map<String, dynamic> json,
  ) {
    final vehicleJson =
        (json['vehicle'] as Map?)?.cast<String, dynamic>() ?? {};

    return ClientServiceDetail(
      incidentId: '${json['incident_id'] ?? ''}',
      status: '${json['status'] ?? ''}',
      createdDate:
          BoliviaDateTimeFormatter.parseServerDateTime(json['created_date']) ??
          DateTime.now().toUtc(),
      updatedDate:
          BoliviaDateTimeFormatter.parseServerDateTime(json['updated_date']) ??
          DateTime.now().toUtc(),
      vehicle: Vehicle.fromJson(vehicleJson),
      description: json['description'] as String?,
      problemName: json['problem_name'] as String?,
      deliveryPrice: _asDouble(json['delivery_price']),
      distanceKm: _asDouble(json['distance_km']),
      address: json['address'] as String?,
      repairShopName: json['repair_shop_name'] as String?,
      mechanicName: json['mechanic_name'] as String?,
      reportDescription: json['report_description'] as String?,
      laborPrice: _asDouble(json['labor_price']),
    );
  }

  static List<ClientIncidentOffer> clientIncidentOffersFromJson(
    Map<String, dynamic>? json,
  ) {
    final offersJson = (json?['offers'] as List?) ?? const [];
    return offersJson
        .whereType<Map>()
        .map((item) => item.cast<String, dynamic>())
        .map(
          (item) => ClientIncidentOffer(
            assignmentId: '${item['assignment_id'] ?? ''}',
            incidentId: '${item['incident_id'] ?? ''}',
            repairShopId: '${item['repair_shop_id'] ?? ''}',
            repairShopName: item['repair_shop_name'] as String?,
            quotedPrice: _asDouble(item['quoted_price']),
            deliveryPrice: _asDouble(item['delivery_price']),
            estimatedMinutes: _asInt(item['estimated_minutes']),
            distanceKm: _asDouble(item['distance_km']),
            mechanicId: item['mechanic_id']?.toString(),
            mechanicName: item['mechanic_name'] as String?,
            offeredAt: BoliviaDateTimeFormatter.parseServerDateTime(
              item['offered_at'],
            ),
          ),
        )
        .where(
          (offer) =>
              offer.assignmentId.trim().isNotEmpty &&
              offer.incidentId.trim().isNotEmpty,
        )
        .toList();
  }

  static ClientOfferActionResult clientOfferActionResultFromJson(
    Map<String, dynamic>? json,
  ) {
    final payload = json ?? const <String, dynamic>{};
    return ClientOfferActionResult(
      assignmentId: '${payload['assignment_id'] ?? ''}',
      incidentId: '${payload['incident_id'] ?? ''}',
      assignmentStatus: '${payload['assignment_status'] ?? ''}',
      incidentStatus: '${payload['incident_status'] ?? ''}',
      detail: '${payload['detail'] ?? ''}',
    );
  }
}
