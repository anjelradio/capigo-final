import 'package:flutter/material.dart';

class HomeActionButton extends StatelessWidget {
  const HomeActionButton({
    super.key,
    required this.text,
    required this.imagePath,
    this.onTap,
    this.backgroundColor = const Color(0xFFD88958),
    this.foregroundColor = const Color(0xFFF8FAFC),
    this.trailingIcon = Icons.arrow_forward_ios_rounded,
    this.imageWidth = 58,
    this.imageSlotWidth = 86,
    this.imageScale = 1,
  });

  final String text;
  final String imagePath;
  final VoidCallback? onTap;
  final Color backgroundColor;
  final Color foregroundColor;
  final IconData trailingIcon;
  final double imageWidth;
  final double imageSlotWidth;
  final double imageScale;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(26),
        child: Ink(
          height: 65,
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(26),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14),
            child: Row(
              children: [
                SizedBox(
                  width: imageSlotWidth,
                  child: OverflowBox(
                    alignment: Alignment.centerLeft,
                    minWidth: imageWidth,
                    maxWidth: imageWidth,
                    child: Transform.scale(
                      scale: imageScale,
                      alignment: Alignment.centerLeft,
                      child: SizedBox(
                        width: imageWidth,
                        child: Image.asset(imagePath, fit: BoxFit.contain),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    text,
                    textAlign: TextAlign.center,
                    style: textTheme.titleSmall?.copyWith(
                      color: foregroundColor,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.2,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(trailingIcon, size: 20, color: foregroundColor),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
