# Panel Pal

<img src="images/logo.jpg" width="200" height="227" />

**Notice: This piece of software is in development as a university project and as yet is not a fully functioning or tested product. Additionally, ongoing maintenance and contributions to this code by the original developers will cease after 07/01/2025. Use of this software is at your own risk.**

PanelPal is a python package of command line tools aimed at NHS labs to help them implement the National Genomic Test Directory for Rare Disease for their NGS tests. It uses API queries to get up-to-date information regarding NGS panels for germline disease. Panels can be applied to patients during bedfile generation for a panel, and thus the patient can be added as an entry to an SQL database.


## Overview of Features

- Fetch a panel name when providing an R number.
- Fetch the genes in a panel; either the latest version or a specific historic version.
- Filter a panel's genes by their review status
- Compare the genes on two versions of a panel.
- Retrieve all panels a gene is present on.
- Create BED files for genomic panels with exonic chromosomal coordinates.
- Compare BED files for their unique chromosomal coordinates
- Add patient entries to an SQL database 

## Getting Started
### Installation
To install and set up PanelPal, see the [Installation Guide](installation.md).

### User Guide
To learn how to run each function in PanelPal, please see the [User Manual](user_manual.md).

### Technical Manual
For bioinformaticians and other software developers looking to learn more about, or contribute to PanelPal, please refer to the [Technical Manual](technical_manual.md)

## License
This project is licensed under the MIT License 

## Developers
- Patrick Weller - Trainee Bioinformatician, All Wales Medical Genomics Service, Cardiff and Vale University Health Board, NHS Wales 
- Ashley Sendell Price - Trainee Bioinformatician, All Wales Medical Genomics Service, Cardiff and Vale University Health Board, NHS Wales
- Madyson Colton - Trainee Bioinformatician, Manchester University NHS Foundation Trust, NHS England
- Rania Velissaris - Trainee Bioinformatician, Royal Devon University Healthcare NHS Foundation Trust, NHS England
