import 'dart:io';

import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class RequestServiceAttachmentsSection extends StatelessWidget {
  const RequestServiceAttachmentsSection({
    super.key,
    required this.imagePaths,
    this.onRemoveImageTap,
  });

  final List<String> imagePaths;
  final ValueChanged<int>? onRemoveImageTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Evidencia del incidente',
            style: TextStyle(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            height: 168,
            child: imagePaths.isEmpty
                ? Container(
                    decoration: BoxDecoration(
                      color: AppColors.appBgDeep,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.appAccentDeep),
                    ),
                    child: const Center(
                      child: Text(
                        'Aun no hay imagenes adjuntas.',
                        style: TextStyle(
                          color: AppColors.appTextOnDarkMuted,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  )
                : ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: imagePaths.length,
                    separatorBuilder: (_, _) => const SizedBox(width: 10),
                    itemBuilder: (_, index) {
                      return _AttachmentImageCard(
                        imagePath: imagePaths[index],
                        onRemoveTap: onRemoveImageTap == null
                            ? null
                            : () => onRemoveImageTap!(index),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _AttachmentImageCard extends StatelessWidget {
  const _AttachmentImageCard({required this.imagePath, this.onRemoveTap});

  final String imagePath;
  final VoidCallback? onRemoveTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 252,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(18),
        child: Stack(
          children: [
            Positioned.fill(
              child: Image.file(
                File(imagePath),
                fit: BoxFit.cover,
                alignment: Alignment.center,
              ),
            ),
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: AppColors.appAccentDeep),
                ),
              ),
            ),
            if (onRemoveTap != null)
              Positioned(
                top: 8,
                right: 8,
                child: Material(
                  color: AppColors.appBgBase.withValues(alpha: 0.84),
                  shape: const CircleBorder(),
                  child: InkWell(
                    onTap: onRemoveTap,
                    customBorder: const CircleBorder(),
                    child: const Padding(
                      padding: EdgeInsets.all(6),
                      child: Icon(
                        Icons.close_rounded,
                        color: AppColors.appTextOnDark,
                        size: 16,
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
