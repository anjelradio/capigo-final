import 'package:mobile/features/user/domain/domain.dart';

class ClientServiceDetail {
  ClientServiceDetail({
    required this.incidentId,
    required this.status,
    required this.createdDate,
    required this.updatedDate,
    required this.vehicle,
    this.description,
    this.problemName,
    this.deliveryPrice,
    this.distanceKm,
    this.address,
    this.repairShopName,
    this.mechanicName,
    this.reportDescription,
    this.laborPrice,
  });

  final String incidentId;
  final String status;
  final DateTime createdDate;
  final DateTime updatedDate;
  final Vehicle vehicle;
  final String? description;
  final String? problemName;
  final double? deliveryPrice;
  final double? distanceKm;
  final String? address;
  final String? repairShopName;
  final String? mechanicName;
  final String? reportDescription;
  final double? laborPrice;
}
