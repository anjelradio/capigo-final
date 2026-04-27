import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class AppHeader extends StatelessWidget {
  const AppHeader({
    super.key,
    this.onDarkBackground = false,
    this.onProfileTap,
  });

  final bool onDarkBackground;
  final VoidCallback? onProfileTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final goColor = onDarkBackground
        ? AppColors.appTextOnDark
        : AppColors.appTextOnDarkMuted;
    const logoPath = 'assets/images/logo/logo_header.png';
    final profileBackgroundColor = onDarkBackground
        ? AppColors.appBgDeep.withValues(alpha: 0.88)
        : AppColors.appBgMid;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.appBgBase,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: AppColors.appNavBorder),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Image.asset(
                  logoPath,
                  height: 30,
                  width: 30,
                  fit: BoxFit.contain,
                  semanticLabel: 'CapiGO',
                  errorBuilder: (_, _, _) => const Icon(
                    Icons.hexagon_rounded,
                    color: AppColors.appAccent,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 8),
                RichText(
                  text: TextSpan(
                    style: textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.2,
                    ),
                    children: [
                      const TextSpan(
                        text: 'CAPI',
                        style: TextStyle(color: AppColors.appAccent),
                      ),
                      TextSpan(
                        text: 'GO',
                        style: TextStyle(color: goColor),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
          IconButton(
            onPressed: onProfileTap,
            style: IconButton.styleFrom(
              backgroundColor: profileBackgroundColor,
              foregroundColor: AppColors.appAccent,
              side: const BorderSide(color: AppColors.appNavBorder),
            ),
            icon: const Icon(Icons.account_circle_rounded, size: 28),
            splashRadius: 22,
            tooltip: 'Cuenta',
          ),
        ],
      ),
    );
  }
}
