import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class MechanicIncidentEvidenceGallery extends StatelessWidget {
  const MechanicIncidentEvidenceGallery({
    super.key,
    required this.evidenceUrls,
    this.showHeader = true,
  });

  final List<String> evidenceUrls;
  final bool showHeader;

  @override
  Widget build(BuildContext context) {
    if (evidenceUrls.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showHeader) ...[
          Text(
            'Evidencias (${evidenceUrls.length})',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
        ],
        SizedBox(
          height: 92,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: evidenceUrls.length,
            separatorBuilder: (_, _) => const SizedBox(width: 8),
            itemBuilder: (_, index) {
              final url = evidenceUrls[index];
              return Material(
                color: Colors.transparent,
                child: InkWell(
                  borderRadius: BorderRadius.circular(12),
                  onTap: () => _openEvidencePreview(context, url),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      width: 120,
                      decoration: BoxDecoration(
                        color: AppColors.appBgBase,
                        border: Border.all(color: AppColors.appNavBorder),
                      ),
                      child: Image.network(
                        url,
                        fit: BoxFit.cover,
                        errorBuilder: (_, _, _) => const Center(
                          child: Icon(
                            Icons.broken_image_outlined,
                            color: AppColors.appTextOnDarkMuted,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Future<void> _openEvidencePreview(BuildContext context, String url) {
    return showDialog<void>(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: AppColors.appBgBase,
        insetPadding: const EdgeInsets.all(14),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Stack(
            children: [
              Positioned.fill(
                child: InteractiveViewer(
                  minScale: 0.9,
                  maxScale: 4.0,
                  child: Image.network(
                    url,
                    fit: BoxFit.contain,
                    errorBuilder: (_, _, _) => const Center(
                      child: Icon(
                        Icons.broken_image_outlined,
                        color: AppColors.appTextOnDarkMuted,
                        size: 36,
                      ),
                    ),
                  ),
                ),
              ),
              Positioned(
                top: 8,
                right: 8,
                child: IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: IconButton.styleFrom(
                    backgroundColor: AppColors.appBgDeep.withValues(
                      alpha: 0.85,
                    ),
                    foregroundColor: AppColors.appTextOnDark,
                  ),
                  icon: const Icon(Icons.close_rounded),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
