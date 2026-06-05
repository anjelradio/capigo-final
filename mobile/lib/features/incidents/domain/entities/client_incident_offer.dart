class ClientIncidentOffer {
  ClientIncidentOffer({
    required this.assignmentId,
    required this.incidentId,
    required this.repairShopId,
    this.repairShopName,
    this.quotedPrice,
    this.deliveryPrice,
    this.estimatedMinutes,
    this.distanceKm,
    this.mechanicId,
    this.mechanicName,
    this.offeredAt,
  });

  final String assignmentId;
  final String incidentId;
  final String repairShopId;
  final String? repairShopName;
  final double? quotedPrice;
  final double? deliveryPrice;
  final int? estimatedMinutes;
  final double? distanceKm;
  final String? mechanicId;
  final String? mechanicName;
  final DateTime? offeredAt;
}

class ClientOfferActionResult {
  ClientOfferActionResult({
    required this.assignmentId,
    required this.incidentId,
    required this.assignmentStatus,
    required this.incidentStatus,
    required this.detail,
  });

  final String assignmentId;
  final String incidentId;
  final String assignmentStatus;
  final String incidentStatus;
  final String detail;
}
