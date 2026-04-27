import 'package:mobile/features/user/data/api/user_api.dart';
import 'package:mobile/features/auth/auth.dart';

class UserRepository {
  UserRepository({required UserApi userApi}) : _userApi = userApi;

  final UserApi _userApi;

  Future<User> updateProfile({
    required String firstName,
    required String lastName,
    required String phone,
  }) {
    return _userApi.updateProfile(
      firstName: firstName,
      lastName: lastName,
      phone: phone,
    );
  }

  Future<void> updatePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmNewPassword,
  }) {
    return _userApi.updatePassword(
      currentPassword: currentPassword,
      newPassword: newPassword,
      confirmNewPassword: confirmNewPassword,
    );
  }

  Future<void> requestEmailChangeOtp() {
    return _userApi.requestEmailChangeOtp();
  }

  Future<String> verifyEmailChangeOtp(String otp) {
    return _userApi.verifyEmailChangeOtp(otp);
  }

  Future<User> updateEmail({
    required String newEmail,
    required String changeEmailToken,
  }) {
    return _userApi.updateEmail(
      newEmail: newEmail,
      changeEmailToken: changeEmailToken,
    );
  }

  Future<User> joinShopByCode(String code) {
    return _userApi.joinShopByCode(code);
  }

  Future<User> unlinkFromShop() {
    return _userApi.unlinkFromShop();
  }
}
