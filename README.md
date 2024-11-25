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

Run the panel_pal.py script from your terminal.

    python panel_pal.py

The script will prompt you to enter a panel ID (e.g., R59, r59, or 59). The input will be validated to ensure it matches the correct format.

Once a valid panel ID is entered, the tool will fetch information from the PanelApp API and display details about the selected panel.

You will be asked to confirm your selection before proceeding. If confirmed, the tool will generate a BED file with gene locus information.

## Directory structure
The following structure should be used going foward to keep the project directories tidy and in preperation for package build. This will also resolve issues importing modules going forward. Note: DB directory has been ommitted from the tree for now.

```bash
.
├── env
│   ├── environment.yaml
│   └── requirements.txt
├── logging
│   └── panelpal.log
├── PanelPal
│   ├── accessories
│   │   ├── __init__.py
│   │   ├── panel_app_api_functions.py
│   │   └── variant_validator_api_functions.py
│   ├── check_panel.py
│   ├── generate_bed.py # This script will require restructuring to be called from main PanelPal function
│   ├── __init__.py
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


## Notes
When running a python script from directory PanelPal the following lines are needed if calling accessory functions
```
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from accessories import panel_app_api_functions
```
Note: this will not be an issue when the python package has been "built"