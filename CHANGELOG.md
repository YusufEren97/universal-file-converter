# Changelog

All notable changes to Universal Converter will be documented in this file.

## [3.0.0] - 2026-01-20

### 🎨 Major UI/UX Overhaul
- Complete CSS rewrite with CSS Variables for consistent theming
- **Light Mode fully fixed** - all elements now visible and styled properly
- Gradient text headings work correctly in both themes
- New button system with `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-success`
- Improved file card design with semantic CSS classes

### 🔧 Technical Improvements
- Removed inline styles from JavaScript - using CSS classes for theme support
- Fixed "groups.common" translation issue in batch dropdown
- Batch dropdown now shows only formats applicable to loaded files
- Custom select dropdown adapts to light/dark theme automatically
- Added `addSelectStyles()` function for dynamic CSS injection

### 📦 Backend Enhancements
- All converters refactored with consistent architecture
- Added `.tar.gz`, `.tar.bz2`, `.tar.xz` support
- Fixed double extension detection in `main.py`
- Port changed to 1453
- PyMuPDF used instead of pdf2image (no Poppler required)

### 🌐 New Format Support
- Video: MOV, WMV, FLV, M4V, 3GP, MPEG, TS
- Audio: AIFF, OPUS, AC3, AMR, M4R (iPhone ringtone)
- Image: AVIF, HEIF, TIFF improvements
- Archive: TAR.GZ, TAR.BZ2, TAR.XZ, TGZ

### 🐛 Bug Fixes
- Fixed theme toggle not updating select dropdowns
- Fixed hero title invisible in light mode
- Fixed batch dropdown showing "groups.common"
- Fixed file cards not appearing in correct container

---

## [2.0.0] - 2026-01-19

### ✨ New Features
- Complete UI redesign with Apple-inspired aesthetics
- Multi-language support (EN, TR, DE, ZH)
- Batch processing with progress tracking
- Theme persistence (Light/Dark mode saved)
- Drag & drop file upload
- Enhanced PDF to DOCX conversion with formatting
- PPTX to PDF/Image conversion

### 🔧 Technical
- FastAPI backend
- Async file processing
- Automatic browser launch on startup
- File cleanup on shutdown

---

## [1.0.0] - Initial Release
- Basic file conversion support
- Simple UI
- Image and video conversion
