# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.


# PanelPal
**Streamline your genomic panel analysis with ease.**

PanelPal is a bioinformatics tool designed to simplify and accelerate genomic panel analysis workflows. 
It integrates filtering strategies and quality control measures to ensure reliable results.

## Key Features
- Efficient filtering for somatic variants in tumour-only and paired tumour-normal analyses.
- Flexible configuration for different pipelines and datasets.
- Comprehensive error handling and logging.
- Easy installation and usage.

## Getting Started
To install and set up PanelPal, see the [Installation Guide](installation.md).

### Quick Start
After installation, run the following to get started:
```bash
panelpal --input example.vcf --output filtered_results.vcf
