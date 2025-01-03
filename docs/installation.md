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
This message also tells you the version number of PanelPal. E.g.:
```
PanelPal: A toolkit for panelapp queries
version: 1.0.0 

Available Commands:
    check-panel             Check panel information for a given panel ID.
                            Example: PanelPal check-panel --panel_id R59
...
```

#### 5. Start using PanelPal
Congratulations, PanelPal has been installed successfully and you can now start implementing the National Test Directory for Rare Disease for your NGS Tests.

Please refer to the [user manual](user_manual.md) for instructions on how to use PanelPal.

