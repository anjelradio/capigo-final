import 'package:formz/formz.dart';

enum VehiclePlateError { empty, length, format }

class VehiclePlate extends FormzInput<String, VehiclePlateError> {
  static final RegExp _plateRegExp = RegExp(r'^[A-Z0-9-]+$');

  const VehiclePlate.pure() : super.pure('');

  const VehiclePlate.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == VehiclePlateError.empty) return 'La placa es requerida';
    if (displayError == VehiclePlateError.length) {
      return 'La placa debe tener entre 5 y 12 caracteres';
    }
    if (displayError == VehiclePlateError.format) {
      return 'La placa solo permite letras, numeros y guion';
    }
    return null;
  }

  @override
  VehiclePlateError? validator(String value) {
    final normalized = value.toUpperCase().replaceAll(' ', '');
    if (normalized.isEmpty) return VehiclePlateError.empty;
    if (normalized.length < 5 || normalized.length > 12) {
      return VehiclePlateError.length;
    }
    if (!_plateRegExp.hasMatch(normalized)) return VehiclePlateError.format;
    return null;
  }
}
