# Technical Manual

This is the technical manual for PanelPal. The intended audience is bioinformaticians or software developers with technical knowledge and experience of python that may wish to:
- Better understand the source code behind PanelPal.
- Tweak the source code of PanelPal for their own customisation.
- Contribute to making PanelPal a better product for all users. 

## GitHub
The source code for PanelPal can be found here: [Panel Pal Repository](https://github.com/PatrickWeller/PanelPal).

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
    - Push up to GitHub and check that automated tests still all pass OK
    - Submit a pull request with a clear description of your changes
      - Please make use of the pull request template as appropriate. Small code changes may not require the full checklist to be fulfilled.
3. **Provide Feedback or Ask Questions**
    - For questions or feedback, please email [Patrick.Weller@wales.nhs.uk](mailto:Patrick.Weller@wales.nhs.uk).

## Project Architecture
```
├── PanelPal
│   ├── accessories
│   │   ├── bedfile_functions.py
│   │   ├── panel_app_api_functions.py
│   │   └── variant_validator_api_functions.py
│   ├── check_panel.py
│   ├── compare_bedfiles.py
│   ├── compare_panel_versions.py
│   ├── generate_bed.py
│   ├── gene_to_panels.py
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
│   │   └── logo.jpg
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

## Tweaking PanelPal
Several decisions have been made about default values for running some commands. Your needs may be different to ours and so you may want to modify the default values.
### Gene Status Filtering
By default, all functions have been configured to use a green confidence status as the default level to filter genes on panels by. This will omit amber and red graded genes. This decision was made based on the practices of our labs only running panels with the best evidence of a gene's association with a clinical phenotype. 

Every relevant function has a flag that can be utilised to specify the lowest gene status that you want returned/processed. However, you may wish to modify the source code so that if your default is amber or red, you don't need to enter this flag every time you run a function.

The relevant functions to be modified will be found in the following:
p
Change 'default = "green"' to 'default = "amber"' or 'default = "red"'.
However, please don't include this change in a pull request if making one to the PanelPal repository.
## Exon padding
