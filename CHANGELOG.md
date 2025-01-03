# Changelog

## [2.0.0] - 02-01-2025
### Added
- New Core Functions:
  - compare_bedfiles
  - gene_to_panels function
- New accessory functions:
  - bedfile_functions
- Installation and Documentation
  - New Dockerfile for containerized deployment.
  - Coverage.rc file
  - Attempt at setting up Read the Docs
  - MIT License
- Tests for new functions

### Changed
- Replacement of setup.py with pyproject.toml
- Updated `get_genes` function in `panel_app_api_functions.py` to filter by gene status.
  - Functionality for this then works in generate_bed and compare_panel_versions
- generate_bed creates a header to the file

## [1.0.0] - 20-12-2024
### Added
- Initial release with core functionality
  - check_panel
  - compare_panel_versions
  - generate_bed
- Accessory Functions
  - api functions for PanelApp and VariantValidator
- Rotating Log File
- Automated tests with GitHub Actions
