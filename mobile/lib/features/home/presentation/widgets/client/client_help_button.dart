import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/home/presentation/widgets/shared/shared_widgets.dart';

class ClientHelpButton extends StatelessWidget {
  const ClientHelpButton({super.key});

  @override
  Widget build(BuildContext context) {
    const helpImageWidth = 85.0;
    const helpImageSlotWidth = 140.0;
    const helpImageScale = 2.0;

    return HomeActionButton(
      text: 'Solicitar ayuda',
      imagePath: 'assets/images/buttons/client/help.png',
      backgroundColor: AppColors.appAccent,
      foregroundColor: AppColors.appAccentText,
      imageWidth: helpImageWidth,
      imageSlotWidth: helpImageSlotWidth,
      imageScale: helpImageScale,
      onTap: () => context.push('/incidents/request-service'),
    );
  }
}
