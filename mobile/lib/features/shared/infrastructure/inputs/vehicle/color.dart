import 'package:formz/formz.dart';

enum VehicleColorError { empty, length }

class VehicleColor extends FormzInput<String, VehicleColorError> {
  const VehicleColor.pure() : super.pure('');

  const VehicleColor.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == VehicleColorError.empty) return 'El color es requerido';
    if (displayError == VehicleColorError.length) {
      return 'El color debe tener entre 2 y 30 caracteres';
    }
    return null;
  }

  @override
  VehicleColorError? validator(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) return VehicleColorError.empty;
    if (trimmed.length < 2 || trimmed.length > 30) {
      return VehicleColorError.length;
    }
    return null;
  }
}
