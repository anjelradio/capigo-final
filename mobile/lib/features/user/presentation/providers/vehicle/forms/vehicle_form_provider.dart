import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/domain/domain.dart';
import 'package:mobile/features/user/presentation/providers/vehicle/vehicle_repository_provider.dart';
import 'package:mobile/features/user/presentation/providers/vehicle/vehicles_provider.dart';

final vehicleFormProvider = StateNotifierProvider.autoDispose
    .family<VehicleFormNotifier, VehicleFormState, Vehicle>((ref, vehicle) {
      final vehicleRepository = ref.watch(vehicleRepositoryProvider);
      final vehiclesNotifier = ref.read(vehiclesProvider.notifier);

      Future<Vehicle> submitVehicle(Map<String, dynamic> vehicleLike) async {
        final savedVehicle = await vehicleRepository.createUpdateVehicle(
          vehicleLike,
        );
        vehiclesNotifier.addOrUpdateVehicle(savedVehicle);
        return savedVehicle;
      }

      Future<void> deleteVehicle(String vehicleId) async {
        await vehicleRepository.deleteVehicle(vehicleId);
        vehiclesNotifier.removeVehicle(vehicleId);
      }

      return VehicleFormNotifier(
        vehicle: vehicle,
        onSubmitCallback: submitVehicle,
        onDeleteCallback: deleteVehicle,
      );
    });

class VehicleFormNotifier extends StateNotifier<VehicleFormState> {
  VehicleFormNotifier({
    required Vehicle vehicle,
    required this.onSubmitCallback,
    required this.onDeleteCallback,
  }) : super(
         VehicleFormState(
           id: vehicle.id,
           make: VehicleMake.dirty(vehicle.make),
           model: VehicleModel.dirty(vehicle.model),
           plate: VehiclePlate.dirty(vehicle.plate),
           color: VehicleColor.dirty(vehicle.color),
           year: VehicleYear.dirty(vehicle.year == 0 ? '' : '${vehicle.year}'),
           typeId: VehicleTypeId.dirty(vehicle.type.id),
           typeName: vehicle.type.name,
         ),
       ) {
    state = state.copyWith(isValid: _validateState(state));
  }

  final Future<Vehicle> Function(Map<String, dynamic> vehicleLike)
  onSubmitCallback;
  final Future<void> Function(String vehicleId) onDeleteCallback;

  void onMakeChanged(String value) {
    final make = VehicleMake.dirty(value);
    state = state.copyWith(
      make: make,
      errorMessages: const [],
      isValid: _validate(make: make),
    );
  }

  void onModelChanged(String value) {
    final model = VehicleModel.dirty(value);
    state = state.copyWith(
      model: model,
      errorMessages: const [],
      isValid: _validate(model: model),
    );
  }

  void onPlateChanged(String value) {
    final plate = VehiclePlate.dirty(value);
    state = state.copyWith(
      plate: plate,
      errorMessages: const [],
      isValid: _validate(plate: plate),
    );
  }

  void onColorChanged(String value) {
    final color = VehicleColor.dirty(value);
    state = state.copyWith(
      color: color,
      errorMessages: const [],
      isValid: _validate(color: color),
    );
  }

  void onYearChanged(String value) {
    final year = VehicleYear.dirty(value);
    state = state.copyWith(
      year: year,
      errorMessages: const [],
      isValid: _validate(year: year),
    );
  }

  void onTypeChanged({required String id, required String name}) {
    final typeId = VehicleTypeId.dirty(id);
    state = state.copyWith(
      typeId: typeId,
      typeName: name,
      errorMessages: const [],
      isValid: _validate(typeId: typeId),
    );
  }

  Future<bool> onFormSubmit() async {
    _touchEveryField();
    if (!state.isValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    final normalizedPlate = state.plate.value.toUpperCase().replaceAll(' ', '');
    final vehicleLike = {
      'id': state.id,
      'make': state.make.value.trim(),
      'model': state.model.value.trim(),
      'plate': normalizedPlate,
      'color': state.color.value.trim(),
      'year': state.year.valueAsInt,
      'type_id': state.typeId.value,
    };

    try {
      final savedVehicle = await onSubmitCallback(vehicleLike);
      if (!mounted) return false;

      state = state.copyWith(
        isPosting: false,
        id: savedVehicle.id,
        typeId: VehicleTypeId.dirty(savedVehicle.type.id),
        typeName: savedVehicle.type.name,
      );
      return true;
    } on CustomError catch (e) {
      if (!mounted) return false;
      state = state.copyWith(isPosting: false, errorMessages: e.messages);
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible guardar el vehiculo'],
      );
      return false;
    }
  }

  Future<bool> onDeleteVehicle() async {
    if (state.id == 'new') return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    try {
      await onDeleteCallback(state.id);
      if (!mounted) return false;
      state = state.copyWith(isPosting: false);
      return true;
    } on CustomError catch (e) {
      if (!mounted) return false;
      state = state.copyWith(isPosting: false, errorMessages: e.messages);
      return false;
    } catch (_) {
      if (!mounted) return false;
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible eliminar el vehiculo'],
      );
      return false;
    }
  }

  void _touchEveryField() {
    final make = VehicleMake.dirty(state.make.value);
    final model = VehicleModel.dirty(state.model.value);
    final plate = VehiclePlate.dirty(state.plate.value);
    final color = VehicleColor.dirty(state.color.value);
    final year = VehicleYear.dirty(state.year.value);
    final typeId = VehicleTypeId.dirty(state.typeId.value);

    state = state.copyWith(
      make: make,
      model: model,
      plate: plate,
      color: color,
      year: year,
      typeId: typeId,
      isFormPosted: true,
      isValid: Formz.validate([make, model, plate, color, year, typeId]),
    );
  }

  bool _validate({
    VehicleMake? make,
    VehicleModel? model,
    VehiclePlate? plate,
    VehicleColor? color,
    VehicleYear? year,
    VehicleTypeId? typeId,
  }) {
    return Formz.validate([
      make ?? state.make,
      model ?? state.model,
      plate ?? state.plate,
      color ?? state.color,
      year ?? state.year,
      typeId ?? state.typeId,
    ]);
  }

  bool _validateState(VehicleFormState current) {
    return Formz.validate([
      current.make,
      current.model,
      current.plate,
      current.color,
      current.year,
      current.typeId,
    ]);
  }
}

class VehicleFormState {
  VehicleFormState({
    this.id = 'new',
    this.make = const VehicleMake.pure(),
    this.model = const VehicleModel.pure(),
    this.plate = const VehiclePlate.pure(),
    this.color = const VehicleColor.pure(),
    this.year = const VehicleYear.pure(),
    this.typeId = const VehicleTypeId.pure(),
    this.typeName = '',
    this.isPosting = false,
    this.isFormPosted = false,
    this.isValid = false,
    this.errorMessages = const [],
  });

  final String id;
  final VehicleMake make;
  final VehicleModel model;
  final VehiclePlate plate;
  final VehicleColor color;
  final VehicleYear year;
  final VehicleTypeId typeId;
  final String typeName;
  final bool isPosting;
  final bool isFormPosted;
  final bool isValid;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  VehicleFormState copyWith({
    String? id,
    VehicleMake? make,
    VehicleModel? model,
    VehiclePlate? plate,
    VehicleColor? color,
    VehicleYear? year,
    VehicleTypeId? typeId,
    String? typeName,
    bool? isPosting,
    bool? isFormPosted,
    bool? isValid,
    List<String>? errorMessages,
  }) {
    return VehicleFormState(
      id: id ?? this.id,
      make: make ?? this.make,
      model: model ?? this.model,
      plate: plate ?? this.plate,
      color: color ?? this.color,
      year: year ?? this.year,
      typeId: typeId ?? this.typeId,
      typeName: typeName ?? this.typeName,
      isPosting: isPosting ?? this.isPosting,
      isFormPosted: isFormPosted ?? this.isFormPosted,
      isValid: isValid ?? this.isValid,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}
