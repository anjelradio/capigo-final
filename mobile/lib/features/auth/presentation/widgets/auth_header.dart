import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';

class AuthHeader extends StatelessWidget {
  final double imageHeight;
  final String imagePath;
  final String title;
  final String description;

  const AuthHeader({
    super.key,
    required this.imageHeight,
    required this.imagePath,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    const logoPath = 'assets/images/logo/logo_header.png';

    return SizedBox(
      width: double.infinity,
      height: imageHeight,
      child: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              imagePath,
              fit: BoxFit.cover,
              errorBuilder: (_, _, _) => Container(color: Colors.black12),
            ),
          ),
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0xAA161B21),
                    Color(0xB31F242B),
                    Color(0xCC24303E),
                  ],
                  stops: [0.0, 0.58, 1.0],
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 18, 10, 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Align(
                        alignment: Alignment.centerLeft,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Image.asset(
                              logoPath,
                              height: 44,
                              width: 44,
                              fit: BoxFit.contain,
                              semanticLabel: title,
                              errorBuilder: (_, _, _) => const Icon(
                                Icons.hexagon_rounded,
                                color: AppColors.appAccent,
                                size: 28,
                              ),
                            ),
                            const SizedBox(width: 8),
                            RichText(
                              text: TextSpan(
                                style: textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.2,
                                ),
                                children: const [
                                  TextSpan(
                                    text: 'CAPI',
                                    style: TextStyle(
                                      color: AppColors.appAccent,
                                    ),
                                  ),
                                  TextSpan(
                                    text: 'GO',
                                    style: TextStyle(
                                      color: AppColors.appCardBg,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    if (context.canPop())
                      IconButton(
                        onPressed: context.pop,
                        icon: const Icon(
                          Icons.close_rounded,
                          size: 30,
                          color: AppColors.appCardBg,
                        ),
                      ),
                  ],
                ),
                const Spacer(),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 300),
                  child: Text(
                    description,
                    style: textTheme.bodyMedium?.copyWith(
                      color: AppColors.appTextOnDark,
                      fontSize: 20,
                      height: 1.35,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                const SizedBox(height: 90),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
