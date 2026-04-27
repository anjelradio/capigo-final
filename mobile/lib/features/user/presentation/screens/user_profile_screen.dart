import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';
import 'package:mobile/features/user/presentation/widgets/widgets.dart';

class UserProfileScreen extends ConsumerWidget {
  const UserProfileScreen({super.key});

  Future<void> _openEditPersonalInfoDialog(
    BuildContext context,
    WidgetRef ref,
    User? user,
  ) async {
    if (user == null) {
      _showSnackbar(context, 'No hay sesion activa', isError: true);
      return;
    }

    bool? updated;
    try {
      updated = await showDialog<bool>(
        context: context,
        builder: (_) => EditPersonalInfoDialog(
          firstName: user.firstName,
          lastName: user.lastName,
          phone: user.phone,
        ),
      );
    } catch (_) {
      if (!context.mounted) return;
      _showSnackbar(
        context,
        'No fue posible abrir el formulario de informacion personal',
        isError: true,
      );
      return;
    }

    if (!context.mounted || updated != true) return;
    _showSnackbar(context, 'Informacion actualizada correctamente');
  }

  Future<void> _startEmailChangeFlow(
    BuildContext context,
    WidgetRef ref,
    User? user,
  ) async {
    if (user == null) {
      _showSnackbar(context, 'No hay sesion activa', isError: true);
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => const AppConfirmDialog(
        title: 'Cambiar correo electronico',
        description:
            'Te enviaremos un codigo OTP al correo actual para confirmar el cambio.',
        confirmText: 'Si, enviar codigo',
      ),
    );

    if (!context.mounted || confirmed != true) return;

    final emailNotifier = ref.read(emailChangeFormProvider.notifier);
    emailNotifier.resetFlow();
    final requestOk = await emailNotifier.requestOtp();
    if (!context.mounted) return;

    if (!requestOk) {
      final error = ref.read(emailChangeFormProvider).errorMessage;
      _showSnackbar(
        context,
        error.isEmpty ? 'No fue posible enviar el codigo OTP' : error,
        isError: true,
      );
      return;
    }

    _showSnackbar(context, 'Se envio un codigo OTP a tu correo actual');

    final updated = await showDialog<bool>(
      context: context,
      builder: (_) => const ChangeEmailDialog(),
    );

    if (!context.mounted || updated != true) return;
    _showSnackbar(context, 'Correo actualizado correctamente');
  }

  Future<void> _openChangePasswordDialog(
    BuildContext context,
    WidgetRef ref,
  ) async {
    ref.read(passwordChangeFormProvider.notifier).reset();

    final updated = await showDialog<bool>(
      context: context,
      builder: (_) => const ChangePasswordDialog(),
    );

    if (!context.mounted || updated != true) return;
    _showSnackbar(context, 'Contraseña actualizada correctamente');
  }

  Future<void> _openJoinShopDialog(
    BuildContext context,
    WidgetRef ref,
    User? user,
  ) async {
    if (user == null) {
      _showSnackbar(context, 'No hay sesion activa', isError: true);
      return;
    }

    if (user.role.trim().toLowerCase() != 'client') {
      _showSnackbar(context, 'Ya perteneces a un taller', isError: true);
      return;
    }

    ref.read(joinShopFormProvider.notifier).reset();

    final joined = await showDialog<bool>(
      context: context,
      builder: (_) => const JoinShopDialog(),
    );

    if (!context.mounted || joined != true) return;

    _showSnackbar(context, 'Ahora formas parte de un taller como mecanico');
    context.go('/home/mechanic');
  }

  Future<void> _unlinkFromShop(
    BuildContext context,
    WidgetRef ref,
    User? user,
  ) async {
    if (user == null) {
      _showSnackbar(context, 'No hay sesion activa', isError: true);
      return;
    }

    if (user.role.trim().toLowerCase() != 'mechanic') {
      _showSnackbar(
        context,
        'Solo usuarios mechanic pueden desvincularse del taller',
        isError: true,
      );
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => const AppConfirmDialog(
        title: 'Desvincularse del taller',
        description:
            '¿Estas seguro que quieres desvincularte de tu taller actual?',
        confirmText: 'Desvincular',
      ),
    );

    if (!context.mounted || confirmed != true) return;

    try {
      final updatedUser = await ref
          .read(userRepositoryProvider)
          .unlinkFromShop();
      ref.read(authProvider.notifier).syncUser(updatedUser);
      if (!context.mounted) return;

      _showSnackbar(context, 'Te desvinculaste de tu taller correctamente');
      context.go('/check');
    } on CustomError catch (e) {
      if (!context.mounted) return;
      final message = e.messages.isNotEmpty
          ? e.messages.first
          : 'No fue posible desvincularte del taller';
      _showSnackbar(context, message, isError: true);
    } catch (_) {
      if (!context.mounted) return;
      _showSnackbar(
        context,
        'No fue posible desvincularte del taller',
        isError: true,
      );
    }
  }

  void _showSnackbar(
    BuildContext context,
    String message, {
    bool isError = false,
  }) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: isError
              ? AppColors.toastError
              : AppColors.toastSuccess,
        ),
      );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).user;

    final firstName = user?.firstName.trim();
    final lastName = user?.lastName.trim();
    final phone = user?.phone.trim();
    final email = user?.email.trim();

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      body: SafeArea(
        child: Column(
          children: [
            _ProfileHeader(onBack: () => context.pop()),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(16, 10, 16, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const _SectionTitle(title: 'Informacion personal'),
                    const SizedBox(height: 10),
                    ProfileInfoItem(
                      title: 'Nombre',
                      subtitle: _safeValue(firstName),
                    ),
                    const SizedBox(height: 10),
                    ProfileInfoItem(
                      title: 'Apellido',
                      subtitle: _safeValue(lastName),
                    ),
                    const SizedBox(height: 10),
                    ProfileInfoItem(
                      title: 'Telefono',
                      subtitle: _safeValue(phone),
                    ),
                    const SizedBox(height: 10),
                    ProfileActionItem(
                      title: 'Actualizar informacion personal',
                      subtitle: 'Edita tu nombre, apellido y telefono',
                      leadingIcon: Icons.edit_outlined,
                      onTap: () =>
                          _openEditPersonalInfoDialog(context, ref, user),
                    ),
                    const SizedBox(height: 20),
                    const _SectionTitle(title: 'Correo asociado'),
                    const SizedBox(height: 10),
                    ProfileActionItem(
                      title: _safeValue(email),
                      subtitle: 'Cambiar correo electronico',
                      leadingIcon: Icons.alternate_email_rounded,
                      onTap: () => _startEmailChangeFlow(context, ref, user),
                    ),
                    const SizedBox(height: 20),
                    const _SectionTitle(title: 'Contraseña'),
                    const SizedBox(height: 10),
                    ProfileActionItem(
                      title: 'Cambiar contraseña',
                      subtitle: 'Actualiza tu clave de acceso',
                      leadingIcon: Icons.lock_outline_rounded,
                      onTap: () => _openChangePasswordDialog(context, ref),
                    ),
                    const SizedBox(height: 20),
                    const _SectionTitle(title: 'Taller'),
                    const SizedBox(height: 10),
                    if (user?.role.trim().toLowerCase() == 'mechanic')
                      ProfileActionItem(
                        title: 'Desvincularse de tu taller',
                        subtitle: 'Dejaras de ser mecanico del taller actual',
                        leadingIcon: Icons.link_off_rounded,
                        onTap: () => _unlinkFromShop(context, ref, user),
                      )
                    else
                      ProfileActionItem(
                        title: 'Unirse a un taller',
                        subtitle: 'Puedes unirte a un taller si eres cliente',
                        leadingIcon: Icons.build_circle_outlined,
                        onTap: () => _openJoinShopDialog(context, ref, user),
                      ),
                    const SizedBox(height: 28),
                    SizedBox(
                      width: double.infinity,
                      child: CustomFilledButton(
                        text: 'Cerrar sesion',
                        buttonColor: AppColors.appAccent,
                        onPressed: () async {
                          await ref.read(authProvider.notifier).logout();
                          if (!context.mounted) return;
                          context.go('/check');
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProfileHeader extends StatelessWidget {
  const _ProfileHeader({required this.onBack});

  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        children: [
          IconButton(
            onPressed: onBack,
            icon: const Icon(Icons.arrow_back_ios_new_rounded),
            color: AppColors.appAccent,
            splashRadius: 22,
          ),
          Expanded(
            child: Center(
              child: Text(
                'Configuracion del perfil',
                style: textTheme.titleSmall?.copyWith(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
          const SizedBox(width: 44),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Text(
      title,
      style: textTheme.titleSmall?.copyWith(
        color: AppColors.appAccent,
        fontWeight: FontWeight.w800,
      ),
    );
  }
}

String _safeValue(String? value) {
  if (value == null || value.isEmpty) return 'No disponible';
  return value;
}
