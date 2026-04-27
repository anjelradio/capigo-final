import 'package:formz/formz.dart';

enum VehicleModelError { empty, length }

class VehicleModel extends FormzInput<String, VehicleModelError> {
  const VehicleModel.pure() : super.pure('');

  const VehicleModel.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == VehicleModelError.empty)
      return 'El modelo es requerido';
    if (displayError == VehicleModelError.length) {
      return 'El modelo debe tener entre 1 y 80 caracteres';
    }
    return null;
  }

  @override
  VehicleModelError? validator(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) return VehicleModelError.empty;
    if (trimmed.length > 80) return VehicleModelError.length;
    return null;
  }
}
