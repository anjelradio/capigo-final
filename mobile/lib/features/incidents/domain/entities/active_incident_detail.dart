import 'package:mobile/features/user/domain/domain.dart';

class ActiveIncidentDetail {
  ActiveIncidentDetail({
    required this.incident,
    required this.vehicle,
    required this.evidences,
    this.assignment,
  });

  final ActiveIncidentCore incident;
  final Vehicle vehicle;
  final List<IncidentEvidence> evidences;
  final ActiveIncidentAssignment? assignment;
}

class ActiveIncidentCore {
  ActiveIncidentCore({
    required this.id,
    required this.status,
    required this.priority,
    required this.latitude,
    required this.longitude,
    required this.createdDate,
    this.description,
    this.deliveryPrice,
    this.distanceKm,
  });

  final String id;
  final String? description;
  final String status;
  final String priority;
  final double latitude;
  final double longitude;
  final double? deliveryPrice;
  final double? distanceKm;
  final DateTime createdDate;
}

class IncidentEvidence {
  IncidentEvidence({required this.id, required this.url});

  final String id;
  final String url;
}

class ActiveIncidentAssignment {
  ActiveIncidentAssignment({
    required this.requestAssignmentId,
    required this.status,
    required this.repairShopId,
    this.repairShopName,
    this.repairShopLatitude,
    this.repairShopLongitude,
    this.mechanicId,
  });

  final String requestAssignmentId;
  final String status;
  final String repairShopId;
  final String? repairShopName;
  final double? repairShopLatitude;
  final double? repairShopLongitude;
  final String? mechanicId;
}
