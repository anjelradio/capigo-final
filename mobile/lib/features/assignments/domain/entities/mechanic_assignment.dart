class MechanicAssignment {
  MechanicAssignment({
    required this.assignmentId,
    required this.assignmentStatus,
    required this.repairShopId,
    required this.mechanicId,
    required this.incident,
    this.repairShopName,
    this.repairShopLatitude,
    this.repairShopLongitude,
    this.assignedAt,
  });

  final String assignmentId;
  final String assignmentStatus;
  final String repairShopId;
  final String? repairShopName;
  final double? repairShopLatitude;
  final double? repairShopLongitude;
  final String mechanicId;
  final MechanicAssignmentIncident incident;
  final DateTime? assignedAt;

  bool get canReportLocation {
    return incident.status == 'assigned' ||
        incident.status == 'on_the_way' ||
        incident.status == 'arrived';
  }
}

class MechanicAssignmentIncident {
  MechanicAssignmentIncident({
    required this.id,
    required this.status,
    required this.latitude,
    required this.longitude,
    this.description,
    this.address,
    this.problemId,
    this.problemName,
    this.distanceKm,
    this.deliveryPrice,
    this.clientEmail,
    this.clientName,
    this.clientPhone,
    this.evidenceUrls = const [],
    this.vehicle,
  });

  final String id;
  final String status;
  final String? description;
  final String? address;
  final double latitude;
  final double longitude;
  final String? problemId;
  final String? problemName;
  final double? distanceKm;
  final double? deliveryPrice;
  final String? clientEmail;
  final String? clientName;
  final String? clientPhone;
  final List<String> evidenceUrls;
  final MechanicIncidentVehicle? vehicle;
}

class MechanicServiceItem {
  MechanicServiceItem({
    required this.assignmentId,
    required this.incidentId,
    required this.assignmentStatus,
    required this.incidentStatus,
    required this.createdDate,
    required this.updatedDate,
    this.incidentDescription,
    this.problemName,
    this.vehiclePlate,
  });

  final String assignmentId;
  final String incidentId;
  final String assignmentStatus;
  final String incidentStatus;
  final DateTime createdDate;
  final DateTime updatedDate;
  final String? incidentDescription;
  final String? problemName;
  final String? vehiclePlate;
}

class MechanicIncidentVehicle {
  MechanicIncidentVehicle({
    required this.id,
    required this.make,
    required this.model,
    required this.plate,
    required this.color,
    required this.year,
    this.typeName,
  });

  final String id;
  final String make;
  final String model;
  final String plate;
  final String color;
  final int year;
  final String? typeName;
}

class MechanicAssignmentActionResult {
  MechanicAssignmentActionResult({
    required this.assignmentId,
    required this.incidentId,
    required this.incidentStatus,
    required this.assignmentStatus,
    required this.detail,
  });

  final String assignmentId;
  final String incidentId;
  final String incidentStatus;
  final String assignmentStatus;
  final String detail;
}

class MechanicTodayStats {
  MechanicTodayStats({
    required this.completedToday,
    required this.cancelledToday,
  });

  final int completedToday;
  final int cancelledToday;
}
