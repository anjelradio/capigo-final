import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class ProfileActionItem extends StatelessWidget {
  const ProfileActionItem({
    super.key,
    required this.title,
    required this.subtitle,
    this.leadingIcon = Icons.chevron_right_rounded,
    this.onTap,
  });

  final String title;
  final String subtitle;
  final IconData leadingIcon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Ink(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.appCardBg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.appCardBorder),
          ),
          child: Row(
            children: [
              Container(
                height: 34,
                width: 34,
                decoration: BoxDecoration(
                  color: AppColors.appCardSoftBg,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  leadingIcon,
                  size: 18,
                  color: AppColors.appAccentDeep,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: textTheme.bodySmall?.copyWith(
                        color: AppColors.appTextPrimary,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: textTheme.bodySmall?.copyWith(
                        color: AppColors.appTextSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              const Icon(
                Icons.chevron_right_rounded,
                color: AppColors.appTextSecondary,
                size: 22,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
