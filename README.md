# PanelPal
<img src="assets/logo.jpg" width="200" height="227" />

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


## Quick Start
1. [Index](docs/index.md)
2. [Installation Guide](docs/installation.md)
3. [User Manual](docs/user_manual.md)
4. [Technical Manual](docs/technical_manual.md)

## Continuous Integration
Automated unit and functional testing and continuous integration testing have been set up with GitHub Actions (see .github/workflows) and Jenkins CI (See Jenkinsfile).

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Contributing
We welcome contributions to improve PanelPal! Here's how you can get involved:

1. **Report Issues** - 
    - Found a bug or have a suggestion? Open an issue on our GitHub issues page. 
    - Add a label to describe the type of issue, e.g. bug, enhancement.
2. **Submit Changes**
    - Fork the repository and create a new branch for your changes.
    - Make your edits and a thorough suite of tests. Note that we make use of:
      - numpy style docstrings
      - `pylint` or `black` to ensure PEP-8 compliance
      - `coverage` to check test coverage
    - Submit a pull request with a clear description of your changes
3. **Provide Feedback or Ask Questions**
    - For questions or feedback, please email [Patrick.Weller@wales.nhs.uk](mailto:Patrick.Weller@wales.nhs.uk).