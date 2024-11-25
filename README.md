## API query function

Function to extract the relevant panel version, ID and list of genes from the PanelApp API. 

## Features

- Fetch information about a panel using its ID.
- Validate panel ID format and prompt users for input.
- Retrieve and display panel details such as name and clinical indication.
- Generate locus dictionaries for genes based on panel data.
- Create a BED file for a selected panel with chromosomal coordinates.

## Requirements

- Python 3.x
- `requests` library

## Installation

To set up a conda environment for this project, you can use the provided `environment.yaml` file.

1. Clone or download this repository.

   ```bash
   git clone https://github.com/PatrickWeller/PanelPal.git
    ```

2. Create a new conda environment with the following command:

   ```bash
   conda env create -f env/environment.yaml
    ```

3. Activate the environment:

    ```bash
    conda activate PanelPal
    ```

4. Install PanelPal via pip

    ```bash
    cd PanelPal
    pip install .
    ```

## Usage

### check panel
To check and retrieve panel information from the PanelApp API:

```bash
#either
PanelPal check-panel --panel_id R207

#or
python PanelPal/check_panel.py --panel_id R207
```

### generate bed file
To generate a bed file for a given panel:

```bash
python PanelPal/check_panel.py --panel_id R207 --panel_version 4 --genome_build GRCh38
```

## Directory structure
The following structure should be used going foward to keep the project directories tidy and in preperation for package build. This will also resolve issues importing modules going forward. Note: DB directory has been ommitted from the tree for now.

```bash
.
├── env
│   ├── environment.yaml
│   └── requirements.txt
├── PanelPal
│   ├── accessories
│   │   ├── __init__.py
│   │   ├── panel_app_api_functions.py
│   │   └── variant_validator_api_functions.py
│   ├── check_panel.py 
│   ├── generate_bed.py # This script will require restructuring to be called from main PanelPal function
│   ├── __init__.py
│   ├── logging
│   │   └── panelpal.log
│   ├── main.py
│   ├── settings.py
│   └── setup.py
├── README.md
└── test
    ├── __init__.py
    └── test_*.py
```

## License
To be confirmed.
