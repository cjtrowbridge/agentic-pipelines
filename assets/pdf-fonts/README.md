# Bundled PDF fonts

The portable renderer loads these files directly and verifies `manifest.json` SHA-256 hashes. No system font installation or runtime font downloads are required.

- Noto Sans Regular/Bold/Italic/BoldItalic and Noto Sans Mono Regular: downloaded from `https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf` on 2026-10-04. Exact distributed bytes are identified by the manifest; licenses and copyright notices are in `OFL-text.txt`.
- Noto COLRv1 color emoji: fixed upstream release `v2.051`, `https://github.com/googlefonts/noto-emoji/blob/v2.051/fonts/Noto-COLRv1.ttf`. Font license and copyright notices are in `OFL-emoji.txt`.

Both font distributions use SIL OFL 1.1. Retain the notices when redistributing these font files. Fonts are unmodified. The emoji font provides the coverage of its fixed release, not every future Unicode emoji. Text coverage is primarily Latin, Greek and Cyrillic; additional scripts need explicitly bundled compatible fonts and validation.

Color glyphs are rendered from the font by fpdf2, without rewriting Markdown emoji into image tags. PDF copy/search behavior must be tested separately from visual appearance.
