export 'color.dart';
export 'make.dart';
export 'model.dart';
export 'plate.dart';
export 'year.dart';

import 'package:formz/formz.dart';

enum VehicleTypeIdError { empty }

class VehicleTypeId extends FormzInput<String, VehicleTypeIdError> {
  const VehicleTypeId.pure() : super.pure('');

  const VehicleTypeId.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == VehicleTypeIdError.empty) {
      return 'Selecciona un tipo de vehiculo';
    }
    return null;
  }

  @override
  VehicleTypeIdError? validator(String value) {
    if (value.trim().isEmpty) return VehicleTypeIdError.empty;
    return null;
  }
}
