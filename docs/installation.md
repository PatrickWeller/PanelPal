# Installation Guide

## Prerequisites

#### Operating System:
PanelPal has been developed on Ubuntu linux systems.<br>
We cannot guarantee it's compatibility with other operating systems.

#### Docker:
PanelPal is configured to run using a docker container, and thus it is necessary that docker is installed on your system as a prerequisite.
```bash
sudo apt update
sudo apt install docker.io
docker --version
```
#### SQL:
A working knowledge of SQL and SQL queries could be required to interact with PanelPal's integrated database in ways not specified in this documentation.

## Installation

#### 1. Clone or download this repository:

   ```
   git clone https://github.com/PatrickWeller/PanelPal.git
   ```

#### 2. Build the docker image:
This can take a few minutes.

```
cd PanelPal
docker build -t panelpal .
```
#### 3. Run the docker container:

```
docker run -it panelpal
```

#### 4. Test PanelPal is installed:

```
PanelPal
```
This will provide you will the help message for PanelPal which explains the usage of each command.<br>
This message also tells you the version number of PanelPal.

## Further Testing

For peace of mind you can check that the functional and unit tests all pass.

Pytest is installed as a requirement for this purpose. Therefore, you can simply run the following:
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

