import 'package:dio/dio.dart';
import 'package:mobile/config/config.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/shared/infrastructure/errors/api_error_parser.dart';
import 'package:mobile/features/user/data/errors/vehicle_errors.dart';
import 'package:mobile/features/user/data/mappers/mappers.dart';
import 'package:mobile/features/user/domain/domain.dart';

class VehicleApi {
  late final Dio dio;
  final String accessToken;

  VehicleApi({required this.accessToken})
    : dio = Dio(
        BaseOptions(
          baseUrl: Environment.apiUrl,
          headers: {'Authorization': 'Bearer $accessToken'},
        ),
      );

  Never _throwParsedDioError(DioException error, String fallbackMessage) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.connectionError) {
      throw CustomError('Revisa tu conexion a internet');
    }

    final messages = parseApiErrors(error.response?.data);
    if (messages.isNotEmpty) {
      throw CustomError.multiple(messages);
    }

    throw CustomError(fallbackMessage);
  }

  Future<List<Vehicle>> getMyVehicles() async {
    final response = await dio.get('/user/me/vehicles');
    final List<Vehicle> vehicles = [];

    for (final vehicle in response.data ?? []) {
      vehicles.add(VehicleMapper.vehicleJsonToEntity(vehicle));
    }

    return vehicles;
  }

  Future<List<VehicleType>> getVehicleTypes() async {
    try {
      final response = await dio.get('/user/me/vehicles/types');
      final List<VehicleType> vehicleTypes = [];

      for (final vehicleType in response.data ?? []) {
        vehicleTypes.add(VehicleMapper.vehicleTypeJsonToEntity(vehicleType));
      }

      return vehicleTypes;
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible cargar los tipos de vehiculo');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible cargar los tipos de vehiculo');
    }
  }

  Future<Vehicle> getVehicleById(String id) async {
    try {
      final response = await dio.get('/user/me/vehicles/$id');
      final vehicle = VehicleMapper.vehicleJsonToEntity(response.data);
      return vehicle;
    } on DioException catch (e) {
      if (e.response!.statusCode == 404) throw VehicleNotFound();
      throw Exception();
    } catch (e) {
      throw Exception();
    }
  }

  Future<Vehicle> createUpdateVehicle(Map<String, dynamic> vehicleLike) async {
    try {
      final vehicleId = vehicleLike['id'] as String?;
      final method = (vehicleId == null || vehicleId == 'new')
          ? 'POST'
          : 'PATCH';
      final url = (vehicleId == null || vehicleId == 'new')
          ? '/user/me/vehicles'
          : '/user/me/vehicles/$vehicleId';

      final payload = Map<String, dynamic>.from(vehicleLike)..remove('id');

      final response = await dio.request(
        url,
        data: payload,
        options: Options(method: method),
      );

      return VehicleMapper.vehicleJsonToEntity(response.data);
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible guardar el vehiculo');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible guardar el vehiculo');
    }
  }

  Future<void> deleteVehicle(String id) async {
    try {
      await dio.delete('/user/me/vehicles/$id');
    } on DioException catch (e) {
      _throwParsedDioError(e, 'No fue posible eliminar el vehiculo');
    } on CustomError {
      rethrow;
    } catch (_) {
      throw CustomError('No fue posible eliminar el vehiculo');
    }
  }
}
