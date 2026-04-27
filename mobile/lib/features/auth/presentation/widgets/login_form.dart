import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';

class LoginForm extends ConsumerWidget {
  const LoginForm({super.key});
  void showSnackbar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppColors.toastError),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final baseTextStyle = Theme.of(context).textTheme.bodyMedium;
    final loginForm = ref.watch(loginFormProvider);
    ref.listen(authProvider, (previous, next) {
      if (next.errorMessage.isEmpty) return;
      showSnackbar(context, next.errorMessage);
    });
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AppFormLayout(
          fields: [
            CustomTextFormField(
              label: 'Correo',
              keyboardType: TextInputType.emailAddress,
              onChanged: ref.read(loginFormProvider.notifier).onEmailChange,
              errorMessage: loginForm.isFormPosted
                  ? loginForm.email.errorMessage
                  : null,
            ),
            CustomTextFormField(
              label: 'Contraseña',
              obscureText: true,
              onChanged: ref.read(loginFormProvider.notifier).onPasswordChange,
              errorMessage: loginForm.isFormPosted
                  ? loginForm.password.errorMessage
                  : null,
            ),
          ],
          submitText: loginForm.isPosting ? 'Ingresando...' : 'Iniciar Sesión',
          onSubmit: loginForm.isPosting
              ? null
              : ref.read(loginFormProvider.notifier).onFormSubmit,
        ),
        const SizedBox(height: 18),
        Center(
          child: ForgottenPasswordForm(
            textStyle: baseTextStyle?.copyWith(
              color: AppColors.authLink,
              fontSize: 14,
            ),
          ),
        ),
        const SizedBox(height: 12),
        Stack(
          alignment: Alignment.center,
          children: [
            const Divider(
              height: 32,
              thickness: 1,
              color: AppColors.appNavBorder,
            ),
            Container(
              color: AppColors.appBgBase,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(
                '¿No tienes una cuenta?',
                style: baseTextStyle?.copyWith(
                  color: AppColors.appTextOnDarkMuted,
                  fontSize: 14,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Center(
          child: TextButton(
            onPressed: () => context.push('/register'),
            child: Text(
              'Crear una Cuenta',
              style: baseTextStyle?.copyWith(
                color: AppColors.authLink,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
      ],
    );
  }
}
