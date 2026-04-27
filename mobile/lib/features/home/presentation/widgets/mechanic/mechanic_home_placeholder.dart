import 'package:flutter/material.dart';

class MechanicHomePlaceholder extends StatelessWidget {
  const MechanicHomePlaceholder({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.construction_rounded,
              size: 52,
              color: Color(0xFF0F2A45),
            ),
            const SizedBox(height: 16),
            Text(
              'Home de mecanico en construccion',
              textAlign: TextAlign.center,
              style: textTheme.titleMedium?.copyWith(
                color: const Color(0xFF0F2A45),
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
