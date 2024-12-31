# PanelPal
<img src="assets/logo.jpg" width="200" height="227" />

**Note: This piece of software is in development as a university project and as yet is not a fully functioning or tested product. Use of this software is at your own risk.**

PanelPal is a python package of command line tools for helping UK labs implement the National Test Directory for rare disease. It uses API queries to get up-to-date information regarding NGS panels for germline disease.


## Features

- Fetch information about a panel using its R number ID.
- Compare the genes on two versions of a panel. 
- Create BED files for a genomic panels with chromosomal coordinates.


## Installation

To set up a conda environment for this project, you can use the provided `environment.yaml` file.

1. Clone or download this repository:

   ```bash
   git clone https://github.com/PatrickWeller/PanelPal.git
    ```

2. Build the docker image:

   ```bash
   cd PanelPal
   docker build -t panelpal .
    ```

3. Run the docker container:

    ```bash
    docker run -it panelpal
    ```

4. Test PanelPal is installed:

    ```bash
    PanelPal
    ```

## Usage

### Check Panel
To check and retrieve panel information from the PanelApp API:

```bash
#Either
PanelPal check-panel --panel_id R207

#Or
python PanelPal/check_panel.py --panel_id R207
```

### Compare Panel Versions
To compare the genes on two versions of a given panel:

```bash
#Either
PanelPal compare-panel-versions -p R21 -v 1.0 2.0

#Or
python PanelPal/compare_panel_versions.py --panel R21 --versions 1.0 2.0
```
### Generate Bed File
To generate a bed file for a given panel:

```bash
#Either
python PanelPal/generate_bed.py --panel_id R207 --panel_version 4 --genome_build GRCh38

#Or
PanelPal generate-bed --panel_id R207 --panel_version 4 --genome_build GRCh38
```

## Directory structure
The following structure should be used going foward to keep the project directories tidy and compatible with the project build. This will also resolve issues importing modules going forward. Note: DB directory has been omitted from the tree for now.

```bash
.
├── PanelPal
│   ├── accessories
│   │   ├── __init__.py
│   │   ├── panel_app_api_functions.py
│   │   └── variant_validator_api_functions.py
│   ├── check_panel.py
│   ├── compare_panel_versions.py
│   ├── generate_bed.py
│   ├── __init__.py
│   ├── logging
│   │   └── panelpal.log
│   ├── main.py
│   └── settings.py
├── README.md
├── pyproject.toml
├── environment.yaml
├── Dockerfile
├── entrypoint.sh
├── assets
│   └── logo.jpg
└── test
    ├── __init__.py
    └── test_*.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
