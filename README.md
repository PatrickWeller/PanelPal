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
2. Create a new conda environment with the following command:

   ```bash
   conda env create -f environment.yaml
3. Activate the environment:

    ```bash
    conda activate PanelPal
4. Using pip

    ```bash
    pip install -r requirements.txt
## Usage

Run the panel_pal.py script from your terminal.

    python panel_pal.py

The script will prompt you to enter a panel ID (e.g., R59, r59, or 59). The input will be validated to ensure it matches the correct format.

Once a valid panel ID is entered, the tool will fetch information from the PanelApp API and display details about the selected panel.

You will be asked to confirm your selection before proceeding. If confirmed, the tool will generate a BED file with gene locus information.

# Example Output
```bash
######################################################
Welcome to PanelPal!
######################################################

Please enter panel ID (e.g., R59, r59, or 59): R59

Panel ID: R59
Clinical indication: Hereditary Cancer Panel

Is this correct? (yes/no): yes

Proceeding with the selected panel.

BED file generated: R59.bed
```

License

To be confirmed.