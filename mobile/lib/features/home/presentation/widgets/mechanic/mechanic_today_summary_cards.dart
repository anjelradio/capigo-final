import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class MechanicTodaySummaryCards extends StatelessWidget {
  const MechanicTodaySummaryCards({
    super.key,
    required this.completedToday,
    required this.cancelledToday,
  });

  final int completedToday;
  final int cancelledToday;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _TodayCard(
            title: 'Completados hoy',
            value: '$completedToday',
            accentColor: Color(0xFF62C08A),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _TodayCard(
            title: 'Cancelados hoy',
            value: '$cancelledToday',
            accentColor: Color(0xFFE38A8A),
          ),
        ),
      ],
    );
  }
}

class _TodayCard extends StatelessWidget {
  const _TodayCard({
    required this.title,
    required this.value,
    required this.accentColor,
  });

  final String title;
  final String value;
  final Color accentColor;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: textTheme.titleMedium?.copyWith(
              color: accentColor,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}
