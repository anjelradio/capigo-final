import 'package:formz/formz.dart';

enum VehicleMakeError { empty, length }

class VehicleMake extends FormzInput<String, VehicleMakeError> {
  const VehicleMake.pure() : super.pure('');

  const VehicleMake.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == VehicleMakeError.empty) return 'La marca es requerida';
    if (displayError == VehicleMakeError.length) {
      return 'La marca debe tener entre 2 y 60 caracteres';
    }
    return null;
  }

  @override
  VehicleMakeError? validator(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) return VehicleMakeError.empty;
    if (trimmed.length < 2 || trimmed.length > 60) {
      return VehicleMakeError.length;
    }
    return null;
  }
}
