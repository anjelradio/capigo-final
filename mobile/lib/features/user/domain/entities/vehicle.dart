class Vehicle {
  final String id;
  final String make;
  final String model;
  final String plate;
  final String color;
  final int year;
  final VehicleType type;

  Vehicle({
    required this.id,
    required this.make,
    required this.model,
    required this.plate,
    required this.color,
    required this.year,
    required this.type,
  });

  factory Vehicle.fromJson(Map<String, dynamic> json) => Vehicle(
    id: json['id'],
    make: json['make'],
    model: json['model'],
    plate: json['plate'],
    color: json['color'],
    year: json['year'],
    type: VehicleType.fromJson(json['type']),
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'make': make,
    'model': model,
    'plate': plate,
    'color': color,
    'year': year,
    'type': type.toJson(),
  };
}

class VehicleType {
  final String id;
  final String name;

  VehicleType({required this.id, required this.name});

  factory VehicleType.fromJson(Map<String, dynamic> json) =>
      VehicleType(id: json['id'], name: json['name']);

  Map<String, dynamic> toJson() => {'id': id, 'name': name};
}
