import 'package:mobile/features/user/data/api/vehicle_api.dart';
import 'package:mobile/features/user/domain/domain.dart';

class VehicleRepository {
  VehicleRepository({required VehicleApi vehicleApi})
    : _vehicleApi = vehicleApi;

  final VehicleApi _vehicleApi;

  Future<List<Vehicle>> getMyVehicles() {
    return _vehicleApi.getMyVehicles();
  }

  Future<List<VehicleType>> getVehicleTypes() {
    return _vehicleApi.getVehicleTypes();
  }

  Future<Vehicle> getVehicleById(String id) {
    return _vehicleApi.getVehicleById(id);
  }

  Future<Vehicle> createUpdateVehicle(Map<String, dynamic> vehicleLike) {
    return _vehicleApi.createUpdateVehicle(vehicleLike);
  }

  Future<void> deleteVehicle(String id) {
    return _vehicleApi.deleteVehicle(id);
  }
}
