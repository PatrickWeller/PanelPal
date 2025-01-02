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

## Installation

#### 1. Clone or download this repository:

   ```bash
   git clone https://github.com/PatrickWeller/PanelPal.git
   ```

#### 2. Build the docker image:
This can take a few minutes.

```bash
cd PanelPal
docker build -t panelpal .
```
#### 3. Run the docker container:

```bash
docker run -it panelpal
```

#### 4. Test PanelPal is installed:

```bash
PanelPal
```
This will provide you will the help message for PanelPal which explains the usage of each command.<br>
This message also tells you the version number of PanelPal.

## Further Testing


