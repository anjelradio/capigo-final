import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/auth/auth.dart';

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final imageHeight = size.height * 0.38;
    final imagePath = 'assets/images/headers/auth_header.jpg';

    return GestureDetector(
      onTap: () => FocusManager.instance.primaryFocus?.unfocus(),
      child: Scaffold(
        backgroundColor: AppColors.appBgBase,
        body: SafeArea(
          child: SingleChildScrollView(
            physics: const ClampingScrollPhysics(),
            child: Column(
              children: [
                AuthHeader(
                  imageHeight: imageHeight,
                  imagePath: imagePath,
                  title: 'CapiGO',
                  description:
                      'Crea tu cuenta para pedir auxilio mecánico y seguimiento de tus servicios vehiculares.',
                ),
                Transform.translate(
                  offset: const Offset(0, -270),
                  child: const _RegisterContent(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RegisterContent extends StatelessWidget {
  const _RegisterContent();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        color: AppColors.appBgBase,
        borderRadius: BorderRadius.only(topLeft: Radius.circular(85)),
      ),
      padding: const EdgeInsets.fromLTRB(24, 32, 24, 32),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _RegisterWelcomeSection(),
          SizedBox(height: 25),
          RegisterForm(),
        ],
      ),
    );
  }
}

class _RegisterWelcomeSection extends StatelessWidget {
  const _RegisterWelcomeSection();

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '¡Regístrate!',
          style: textTheme.titleMedium?.copyWith(
            color: AppColors.appTextOnDark,
            height: 1.2,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Completa tus datos para crear tu cuenta.',
          style: textTheme.bodyMedium?.copyWith(
            color: AppColors.appTextOnDarkMuted,
          ),
        ),
      ],
    );
  }
}
