import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/auth/auth.dart';

final goRouterNotifierProvider = Provider((ref) {
  final authNotifier = ref.read(authProvider.notifier);
  return GoRouterNotifier(authNotifier);
});

class GoRouterNotifier extends ChangeNotifier {
  final AuthNotifier _authNotifier;
  AuthStatus _authStatus = AuthStatus.checking;
  String? _userRole;

  GoRouterNotifier(this._authNotifier) {
    _authNotifier.addListener((state) {
      _authStatus = state.authStatus;
      _userRole = state.user?.role;
      notifyListeners();
    });
  }

  AuthStatus get authStatus => _authStatus;
  String? get userRole => _userRole;
}
