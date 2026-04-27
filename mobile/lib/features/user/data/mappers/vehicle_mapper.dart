import 'package:mobile/features/user/domain/domain.dart';

class VehicleMapper {
  static Vehicle vehicleJsonToEntity(Map<String, dynamic> json) => Vehicle(
    id: json['id'],
    make: json['make'],
    model: json['model'],
    plate: json['plate'],
    color: json['color'],
    year: json['year'],
    type: VehicleType(id: json['type']['id'], name: json['type']['name']),
  );

  static VehicleType vehicleTypeJsonToEntity(Map<String, dynamic> json) =>
      VehicleType(id: json['id'], name: json['name']);
}
