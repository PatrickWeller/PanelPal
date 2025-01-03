# Technical Manual

This is the technical manual for PanelPal. The intended audience is bioinformaticians or software developers with technical knowledge and experience of python that may wish to:
- Better understand the source code behind PanelPal.
- Tweak the source code of PanelPal for their own customisation.
- Contribute to making PanelPal a better product for all users. 

## GitHub
The source code for PanelPal can be found here: [Panel Pal Repository](https://github.com/PatrickWeller/PanelPal).


## Project Architecture
Some files have been omitted for readability.
```
├── PanelPal
│   ├── accessories
│   │   ├── bedfile_functions.py
│   │   ├── panel_app_api_functions.py
│   │   └── variant_validator_api_functions.py
│   ├── check_panel.py
│   ├── panel-to-genes.py
│   ├── compare_panel_versions.py
│   ├── gene_to_panels.py
│   ├── generate_bed.py
│   ├── compare_bedfiles.py
│   ├── logging
│   │   └── panelpal.log
│   ├── main.py
│   └── settings.py
├── DB
│   ├── create_db.py
│   └── panelpal_db.py
├── panelpal.db
├── pyproject.toml
├── environment.yaml
├── Dockerfile
├── entrypoint.sh
├── README.md
├── CHANGELOG.md
├── LICENSE
├── mkdocs.yaml
├── docs
│   ├── images
│   │   ├── logo.jpg
│   │   └── schema.jpg
│   ├── index.md
│   ├── installation.md
│   ├── technical_manual.md
│   └── user_manual.md
├── assets
│   └── logo.jpg
└── test
    ├── db_tests
    │   └── test_db.py
    ├── test_bedfile_functions.py
    ├── test_check_panel.py
    ├── test_compare_bedfiles.py
    ├── test_compare_panel_versions.py
    ├── test_generate_bed.py
    ├── test_gene_to_panels.py
    ├── test_panelapp.py
    └── test_variantvalidator.py
```
## Running Tests

For peace of mind after installation or modifying the code, you can check that the functional and unit tests all pass.

Pytest is installed as a requirement during installation for this purpose. Therefore, you can simply run the following command and observe if all tests pass:
```
pytest
```
#### Output:
```
(base) root@37a505720376:/app# pytest
==================================== test session starts =======================================
platform linux -- Python 3.12.4, pytest-8.3.3, pluggy-1.5.0
rootdir: /app
configfile: pyproject.toml
collected 144 items                                                                                                                                                                                   

test/db_tests/test_db.py ...                                                              [  2%]
test/test_bedfile_functions.py .....................                                      [ 16%]
test/test_check_panel.py ...........                                                      [ 24%]
test/test_compare_bedfiles.py .....                                                       [ 27%]
test/test_compare_panel_versions.py ...............                                       [ 38%]
test/test_gene_to_panels.py ........................................                      [ 65%]
test/test_generate_bed.py ...............                                                 [ 76%]
test/test_panelapp.py .....................                                               [ 90%]
test/test_variantvalidator.py .............                                               [100%]

=============================== 144 passed in 75.38s (0:01:15) =================================
```
## API Usage in PanelPal
The majority of PanelPal functions work by making use of two APIs. The [PanelApp API](https://panelapp.genomicsengland.co.uk/) by Genomics England, and the [Variant Validator REST API](https://rest.variantvalidator.org/) developed by the University of Leeds and University of Manchester. 

If you wish to know more about either API and how they work, please refer to their individual documentation or repositories. 
- [PanelApp repository available here](https://gitlab.com/genomicsengland/panelapp)
- [Variant Validator repository available here](https://github.com/openvar/rest_variantValidator)

The PanelPal package directory contains the 'accessories' subdirectory. This subdirectory exists to hold modules of functions that are often reused by several PanelPal modules in the package directory. This 'accessories' directory contains the functions that interact with both APIs.

An important thing to note for those wanting to learn how PanelPal works is a quirk of the PanelApp API. The PanelApp API has several endpoints, one of which can be accessed by providing the R number for the panel, which most end users will be familiar with. However, the majority of the end points are accessed in some way using the 'panel_pk' (panel primary key). The documentation requires updating to provide clarity, as some other endpoints refer to 'id' or 'panel_pk' interchangeably, which can cause some confusion. 

As a result of this setup with the PanelApp API, the PanelPal functions have been set up so that a user may provide a panel's R number, and then PanelPal may have to perform multiple requests to PanelApp, firstly inputting the R number to output a panel primary key, and secondly to input the retrieved primary key, to then output whatever data the user was requesting. 

## Reconfiguration of PanelPal
Several decisions have been made about default values for running some commands. Your needs may be different to ours and so you may want to modify the default values.
### Gene Status Filtering
By default, all functions have been configured to use a green confidence status as the default level to filter genes on panels by. This will omit amber and red graded genes. This decision was made based on the practices of our labs only running panels with the best evidence of a gene's association with a clinical phenotype. 

Every relevant function has a flag that can be utilised to specify the lowest gene status that you want returned/processed. However, you may wish to modify the source code so that if your default is amber or red, you don't need to enter this flag every time you run a function.

The relevant functions to be modified will be found in the following:
- PanelPal/panel_to_genes.py::parse_arguments
- PanelPal/gene_to_panels.py::parse_arguments
- PanelPal/compare_panel_versions.py::argument_parser
- PanelPal/generate_bed.py::parse_arguments

Change 'default = "green"' to 'default = "amber"' or 'default = "red"'.

Please don't make this change and then include it in a pull request if making one to the PanelPal repository.

### Exon padding
Another decision made by the development team was to incorporate some padding around exons when generating bed files. This is so that some intronic variants (and also some 3'UTR and 5'UTR variants) could be captured in downstream analyses. These variants have a potential to be clinically significant, but the current ability of genomics labs to interpret such variation is limited.

Therefore, by default, PanelPal has been configured to include just 10 base pairs worth of padding around each exon. 10 base pairs may not be sufficient for the purposes of some users; 50 or 100 bases would be valid padding for many labs. In contrast, some users may wish to remove the padding altogether.

This can be modified by tweaking the source code.<br>
Within PanelPal/accessories/variant_validator_api_functions.py modify the following code in the generate_bed_file() function:
```
def generate_bed_file(...):
    ...
                    # Add padding of 10bp on either side
                    # Avoid negative start positions
                    exon["exon_start"] = max(0, exon["exon_start"] - 10)
                    exon["exon_end"] += 10
    ...
```
## Changelog
Please see CHANGELOG.md for the newest features, changes and bug fixes.

## Contributing
We welcome contributions to improve [PanelPal](https://github.com/PatrickWeller/PanelPal)! Here's how you can get involved:

1. **Report Issues** - 
    - Found a bug or have a suggestion? Open an issue on our GitHub issues page. 
    - Add a label to describe the type of issue, e.g. bug, enhancement.
    - State whether you will be contributing code to fix the issue
2. **Submit Changes**
    - Fork the repository and create a new branch for your changes.
    - Make your edits and a thorough suite of tests. Note that we make use of:
      - numpy style docstrings
      - `pylint` or `black` to ensure PEP-8 compliance
      - `coverage` to check test coverage, and a .coveragerc to pass over code not requiring tests. 
    - Push up to GitHub and check that automated tests still all pass OK
    - Submit a pull request with a clear description of your changes
      - Please make use of the pull request template as appropriate. Minor code changes may not require the full checklist to be fulfilled.
3. **Provide Feedback or Ask Questions**
    - For questions or feedback, please email [Patrick.Weller@wales.nhs.uk](mailto:Patrick.Weller@wales.nhs.uk).