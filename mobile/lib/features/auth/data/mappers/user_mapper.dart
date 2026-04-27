import 'package:mobile/features/auth/auth.dart';

class UserMapper {
  static Map<String, dynamic> _resolveUserJson(Map<String, dynamic> json) {
    final userData = json['user'];
    if (userData is Map<String, dynamic>) return userData;
    return json;
  }

  static User userJsonToEntity(Map<String, dynamic> json) {
    final userJson = _resolveUserJson(json);

    return User(
      id: userJson['id'],
      firstName: userJson['first_name'],
      lastName: userJson['last_name'],
      email: userJson['email'],
      phone: userJson['phone'],
      role: userJson['role'],
      token: json['access_token'],
    );
  }

  static User userJsonWithoutTokenToEntity(
    Map<String, dynamic> json, {
    required String token,
  }) {
    final userJson = _resolveUserJson(json);

    return User(
      id: userJson['id'],
      firstName: userJson['first_name'],
      lastName: userJson['last_name'],
      email: userJson['email'],
      phone: userJson['phone'],
      role: userJson['role'],
      token: token,
    );
  }
}
