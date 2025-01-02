# Panel-Pal

<img src="images/logo.jpg" width="200" height="227" />

**Note: This piece of software is in development as a university project and as yet is not a fully functioning or tested product. Use of this software is at your own risk.**

PanelPal is a python package of command line tools for helping UK labs implement the National Test Directory for rare disease. It uses API queries to get up-to-date information regarding NGS panels for germline disease.


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
To install and set up PanelPal, see the [Installation Guide](installation.md).

## User Guide
To learn how to run each function in PanelPal, please see the [User Manual](docs/user_manual.md).

## Technical Manual
For bioinformaticians and other software developers looking to learn more about PanelPal, please refer to the [Technical Manual](docs/technical_manual.md)

## Developers
- Patrick Weller - Trainee Bioinformatician, All Wales Medical Genomics Service, Cardiff and Vale University Health Board, NHS Wales 
- Ashley Sendell Price - Trainee Bioinformatician, All Wales Medical Genomics Service, Cardiff and Vale University Health Board, NHS Wales
- Madyson Colton - Trainee Bioinformatician, Manchester University NHS Foundation Trust, NHS England
- Rania Velissaris - Trainee Bioinformatician, Royal Devon University Healthcare NHS Foundation Trust, NHS England
