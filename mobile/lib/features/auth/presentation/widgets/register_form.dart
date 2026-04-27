import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/auth/presentation/providers/providers.dart';
import 'package:mobile/features/shared/shared.dart';

class RegisterForm extends ConsumerWidget {
  const RegisterForm({super.key});

  void showSnackbar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppColors.toastError),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final baseTextStyle = Theme.of(context).textTheme.bodyMedium;
    final registerForm = ref.watch(registerFormProvider);

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
              label: 'Nombre completo',
              onChanged: ref
                  .read(registerFormProvider.notifier)
                  .onFirstNameChange,
              errorMessage: registerForm.isFormPosted
                  ? registerForm.firstName.errorMessage
                  : null,
            ),
            CustomTextFormField(
              label: 'Apellidos completos',
              onChanged: ref
                  .read(registerFormProvider.notifier)
                  .onLastNameChange,
              errorMessage: registerForm.isFormPosted
                  ? registerForm.lastName.errorMessage
                  : null,
            ),
            CustomTextFormField(
              label: 'Correo electrónico',
              keyboardType: TextInputType.emailAddress,
              onChanged: ref.read(registerFormProvider.notifier).onEmailChange,
              errorMessage: registerForm.isFormPosted
                  ? registerForm.email.errorMessage
                  : null,
            ),
            CustomTextFormField(
              label: 'Telefono',
              keyboardType: TextInputType.phone,
              onChanged: ref.read(registerFormProvider.notifier).onPhoneChange,
              errorMessage: registerForm.isFormPosted
                  ? registerForm.phone.errorMessage
                  : null,
            ),
            CustomTextFormField(
              label: 'Contraseña',
              obscureText: true,
              onChanged: ref
                  .read(registerFormProvider.notifier)
                  .onPasswordChange,
              errorMessage: registerForm.isFormPosted
                  ? registerForm.password.errorMessage
                  : null,
            ),
          ],
          submitText: registerForm.isPosting
              ? 'Creando cuenta...'
              : 'Regístrate',
          onSubmit: registerForm.isPosting
              ? null
              : ref.read(registerFormProvider.notifier).onFormSubmit,
        ),
        const SizedBox(height: 20),
        Center(
          child: Text(
            '¿Ya tienes una cuenta?',
            style: baseTextStyle?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              fontSize: 14,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Center(
          child: TextButton(
            onPressed: () => context.pop(),
            child: Text(
              'Iniciar sesión',
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
