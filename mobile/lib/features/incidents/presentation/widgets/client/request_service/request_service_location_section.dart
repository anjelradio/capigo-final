import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class RequestServiceLocationSection extends StatelessWidget {
  const RequestServiceLocationSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Ubicacion',
            style: TextStyle(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
              fontSize: 14,
            ),
          ),
          SizedBox(height: 10),
          _LocationRow(
            icon: Icons.my_location_rounded,
            text: 'Latitud: pendiente',
          ),
          SizedBox(height: 6),
          _LocationRow(icon: Icons.place_outlined, text: 'Longitud: pendiente'),
        ],
      ),
    );
  }
}

class _LocationRow extends StatelessWidget {
  const _LocationRow({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: AppColors.appAccent, size: 18),
        const SizedBox(width: 8),
        Text(
          text,
          style: const TextStyle(
            color: AppColors.appTextOnDark,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
