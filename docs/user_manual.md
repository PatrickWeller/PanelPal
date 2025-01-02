# User Manual

### Installation
To install and set up PanelPal, see the [Installation Guide](installation.md).

### Boot Up PanelPal's Docker Container
If PanelPal is already installed, then run the docker container.
```bash
docker run -it panelpal
```
# Command Line Functions
The main features of PanelPal are series of python based scripts/functions that can be ran on the command line to obtained information regarding genomic panels.

The information returned by PanelPal is retrieved from the PanelApp and VariantValidator APIs and so are up-to-date.<br>
PanelPal is therefore dependent on both PanelApp and VariantValidator, their servers, and their maintenance and curation.<br>
PanelPal functions will no longer work if these other sources of data are jeopardised in any way.

PanelPal has functionality for an SQL database where patient information and bed files are linked. Note that the first time a command is run from PanelPal, an empty database will be generated in the background too. 

#### Help:
Calling a function without specifying any arguments on the command line will produce a usage message showing the available flags for that command.<br>
An error message stating which arguments are required will also be printed.<br>
E.g.
```bash
(base)~/Documents/PanelPal$ PanelPal check-panel
usage: PanelPal check-panel [-h] --panel_id PANEL_ID
PanelPal check-panel: error: the following arguments are required: --panel_id
```

## Check Panel
This function enables a user to input the R number of a genetic test, and retrieve the panel name and latest version.<br>


Unfortunately, the current version of this function retrieves the latest available version of the panel, and NOT the latest signed off version.<br>
This is a change we hope to make in a future update to PanelPal.
#### Usage:

```bash
#Either
PanelPal check-panel --panel_id R207

#Or
python PanelPal/check_panel.py --panel_id R207
```
#### Output:
```
Panel ID: R207
Clinical Indication: Inherited ovarian cancer (without breast cancer)
Latest Version: 4.3
```
##  Generate a gene list for a panel
This function enables a user to input the R number of a genetic test, and a version number, and from that generate a list of genes.<br>
The list of genes will be true for the specified version of the panel, and will be saved to a tsv file.


The function defaults to only provide genes at a green status on that version of the panel.<br>
However, a user can optionally provide a ```--confidence_status``` to capture all genes of that confidence level or greater.


Avaiable confidence status options are 'green', 'amber', 'red', 'all'.<br>
E.g. 'amber' will return all genes of amber or green status.<br>

Note: that 'red' and 'all' are functionally equivalent.

#### Usage:
```bash
#Either
python PanelPal/panel_to_genes.py --panel_id R207 --panel_version 2.2 --confidence_status green

#Or
PanelPal panel-genes --panel_id R207 --panel_version 2.2 --confidence_status green
```
#### Output: R207_v2.2_green_genes.tsv
```
BRCA1
BRCA2
BRIP1
MLH1
MSH2
MSH6
RAD51C
RAD51D
```

## Get panels containing a given gene
This function enables a user to provide a gene name (hgnc symbol), to generate a list of panels that currently containing that gene.

The function defaults to provide all panels where the inputted gene is ranked green status. However, this can be toggled with the optional ```--confidence_status``` flag to provide all panels where the inputted gene is ranked the provided status or greater.<br>
Available gene status options are 'green', 'amber', 'red', 'all'.<br>
E.g. 'amber' will return all panels  amber or green status.<br>

Note: that 'red' and 'all' are functionally equivalent.

Some panels on PanelApp do not have R numbers. For example, some panels are 100K genomes panels. <br>
By default, panels that do not have R numbers are not returned from this function.
However, the optional flag ```--show_all_panels```, which is defaulted to 'False', can be toggled to 'True' when running the script to include these panels. 
#### Usage:
```bash
#Either
PanelPal gene-panels --hgnc_symbol BRCA1

#Or
python PanelPal/gene_to_panels.py --hgnc_symbol BRCA1
```
#### Output:
```
Command executed: gene-panels --hgnc_symbol BRCA1 --confidence_status green --show_all_panels False

Panels associated with gene BRCA1:

PanelApp ID    R Code         Panel Name                                                                 Gene Status
------------------------------------------------------------------------------------------------------------------------
143            R207           Inherited ovarian cancer (without breast cancer)                           green
243            R359           Childhood solid tumours                                                    green
524            R367           Inherited pancreatic cancer                                                green
635            R208           Inherited breast cancer and ovarian cancer                                 green
559            R236           Pigmentary skin disorders                                                  green
508            R229, R258     Confirmed Fanconi anaemia or Bloom syndrome                                green
478            R21, R412      Fetal anomalies                                                            green
1223           R430           Inherited prostate cancer                                                  green
1570           R444           NICE approved PARP inhibitor treatment                                     green

Panel list saved to: panels_containing_BRCA1_green.tsv
```
## Compare Panel Versions
This function enables a user to input a genomic panel's R number, and two version numbers, to have returned a list of the gene differences between those two versions of a panel.<br>


Two lists are returned:
- A list of genes removed from the later version of the panel that were in the earlier version
- A list of genes that were not in the earlier version of the panel, but are in the later version.

This function defaults to only show genes that have a green confidence status. However, this can be toggled with the optional ```--status_filter``` flag to only return genes ranked at the provided status or greater.<br>
Available gene status options are 'green', 'amber', 'red', 'all'.<br>
E.g. 'amber' will compare all genes in the panel versions that are of amber or green status.<br>

Note: that 'red' and 'all' are functionally equivalent.

The terms 'Removed genes' and 'Added genes' are not 100% accurate.  A gene may have been on a panel at amber status since v1.0 of the panel.  However, it may only be in v5.1 that the gene is upgraded to green status.  Therefore, the gene was arguably not added between versions 1.0 and 5.1, just upgraded.  Likewise a gene may not have been removed from the panel, just downgraded to a lower status. 

#### Usage: 
```bash
#Either
PanelPal compare-panel-versions -p R21 -v 1.0 2.0 -f green

#Or
python PanelPal/compare_panel_versions.py --panel R21 --versions 1.0 2.0 --status_filter green
```
#### Output:
```
Removed genes: ['TUBA8']
Added genes: ['ABL1', 'ACVR2B', 'ADAMTS3', 'AHCY', 'AKT2', 'ALG2', 'ALG9', 'ALOX12B', 'ALOXE3', 'AMACR', 'AMMECR1', 'ANKS6', 'ANTXR2', 'ARFGEF2', 'ARHGAP29', 'ATP1A2', 'ATR', 'B3GALNT2', 'B4GAT1', 'B9D2', 'BNC2', 'C21orf59', 'C2CD3', 'CACNA1G', 'CANT1', 'CASR', 'CCDC151', 'CCDC8', 'CCDC88C', 'CDK5RAP2', 'CDK8', 'CELSR1', 'CENPF', 'CEP120', 'CEP135', 'CEP55', 'CEP63', 'CERS3', 'CFAP53', 'CFL2', 'CHMP1A', 'CHRNA3', 'CHRNB1', 'CHRNE', 'CIT', 'CLP1', 'COG5', 'COG6', 'COL12A1', 'COL13A1', 'COL3A1', 'COLEC10', 'COLQ', 'CRADD', 'CREB3L1', 'CRIPT', 'CSF1R', 'CTNND1', 'CTU2', 'CYP26B1', 'CYP4F22', 'DDX59', 'DENND5A', 'DIAPH1', 'DISP1', 'DLX5', 'DNAAF2', 'DNAAF5', 'DNAI2', 'DNAJB11', 'DNAL1', 'DNM1L', 'DNM2', 'DONSON', 'DPM2', 'DPM3', 'DYNC2LI1', 'DZIP1L', 'EED', 'EIF2S3', 'EIF5A', 'EML1', 'EMX2', 'ENPP1', 'EXOC3L2', 'EXTL3', 'FAM46A', 'FANCL', 'FIG4', 'FKBP10', 'FLNC', 'FUT8', 'FZD2', 'GALNT2', 'GANAB', 'GATA3', 'GDF1', 'GFPT1', 'GLI1', 'GMNN', 'GPC6', 'GREB1L', 'GSC', 'GZF1', 'HADHB', 'HESX1', 'HIST1H1E', 'HMGA2', 'ICK', 'IDH1', 'IFT52', 'IFT81', 'ITGA8', 'KATNB1', 'KIAA0753', 'KIF14', 'KIF2A', 'KIF5C', 'KLHL7', 'KNL1', 'LAMB1', 'LMNB1', 'LMNB2', 'LONP1', 'LRRC56', 'MACF1', 'MAP3K20', 'MAP3K7', 'MEIS2', 'MEOX1', 'MESD', 'MN1', 'MOGS', 'MRAS', 'MSMO1', 'MSTO1', 'MYH11', 'MYH2', 'MYH7', 'MYL1', 'MYMK', 'MYO18B', 'MYO9A', 'MYOCD', 'MYPN', 'NADSYN1', 'NECTIN1', 'NEDD4L', 'NEK8', 'NEK9', 'NIPAL4', 'NXN', 'OSGEP', 'P4HB', 'PAX7', 'PBX1', 'PFKM', 'PGM3', 'PIBF1', 'PIGN', 'PIH1D3', 'PIK3C2A', 'PITX1', 'PLAG1', 'PLG', 'PNPLA1', 'POLE', 'POLG2', 'POLR1A', 'POLR1B', 'POP1', 'PRIM1', 'PRKAG2', 'PRRX1', 'PRUNE1', 'PSAT1', 'PTPN14', 'PYGM', 'RAB33B', 'RBBP8', 'RBM10', 'RFT1', 'ROBO3', 'RPL10', 'RPL35A', 'RPS24', 'RPS7', 'RRAS2', 'RSPH4A', 'RSPH9', 'SCLT1', 'SCN1A', 'SDR9C7', 'SEC24D', 'SERPINF1', 'SERPINH1', 'SGCG', 'SHANK3', 'SIX6', 'SLC18A3', 'SLC25A19', 'SLC29A3', 'SLC5A7', 'SLC6A9', 'SMARCC1', 'SMARCE1', 'SMG9', 'SMPD4', 'SMS', 'SNX10', 'SOX18', 'SOX6', 'SP7', 'SPARC', 'SPECC1L', 'ST14', 'STAC3', 'STIL', 'STRADA', 'SUFU', 'SULT2B1', 'TBC1D32', 'TCTEX1D2', 'TELO2', 'TENM3', 'TMEM107', 'TMEM216', 'TMEM38B', 'TMEM94', 'TMEM98', 'TMX2', 'TNNT3', 'TOE1', 'TOR1A', 'TRAF3IP1', 'TRAIP', 'TRAP1', 'TRAPPC12', 'TRMT10A', 'TSEN2', 'TSEN34', 'TSFM', 'TUBB3', 'TUBG1', 'TUBGCP4', 'TXNDC15', 'UBE2T', 'USP18', 'USP9X', 'VAMP1', 'VEGFC', 'VRK1', 'WDR73', 'WDR81', 'XYLT2', 'ZMYND10', 'ZSWIM6']
```
## Generate Bed File
This function allows users to provide the R number of a genomic panel, the panel version, and a genome build, to generate a BED file. The generated BED file contains the exonic coordinates for the genes within a specific panel for the MANE select transcript. The coordinates include padding of 10 bases around each exon.

Acceptable genome builds are 'GRCh37' or 'GRCh38'.

By default, only regions associated with genes of green status are included. Users can customize this behavior by providing the optional ```--status_filter``` flag to include genes of a given status or greater.<br>
Available gene status options are 'green', 'amber', 'red', 'all'.<br>
E.g. 'amber' will compare all genes in the panel versions that are of amber or green status.

Note: that 'red' and 'all' are functionally equivalent.

The BED file has a header section with useful information about the generation of the bed file.<br>
The bed file output is compliant with standard formats, ensuring compatibility with other tools used in genomics workflows.<br>
The function will use the command line arguments to create an informative name for the bed file.<br>
If a bed file with the same name already exists, then the function will catch this before file generation and notify the user that this file already exists to prevent wasted resources.

This function also generates a collapsed/merged bed file, though this currently has little utility. In a future update to PanelPal we would like to incorporate the option to specify which transcripts to include in generated bed files. E.g. MANE select and MANE plus clinical, or even all transcripts. This would lead to bloated bed files with regions that overlap. Therefore this creation of collapsed bed files was implemented in the hope that should this new utility be implemented, bed files with overlapping regions could be collapsed to save space.

It is assumed that when a user generates a bed file, they may be doing so as they are going to apply that panel to a patient, and therfore run the patient data through a pipelien with that bed file. Therefore, this function also provides an option for the user to enter patient information into the PanelPal database. The user can accept or decline the option to enter information into the database. More information on this is feature is found later on this page. See [Database](#Database)
#### Usage:
```bash
#Either
python PanelPal/generate_bed.py --panel_id R415 --panel_version 1.6 --genome_build GRCh38 --status_filter green

#Or
PanelPal generate-bed --panel_id R415 --panel_version 1.6 --genome_build GRCh38 --status_filter green
```
#### Output: R415_v1.6_GRCh38.bed
```
# BED file generated for panel: R415 (Version: 1.6). Date of creation: 2025-01-02 11:17:31.
# Genome build: GRCh38. Number of genes: 2.
# BED file: R415_v1.6_GRCh38.bed
# Columns: chrom, chromStart, chromEnd, exon_number|transcript|gene symbol
16      67029138        67029495        exon1|NM_022845.3|CBFB
16      67029716        67029823        exon2|NM_022845.3|CBFB
16      67036628        67036765        exon3|NM_022845.3|CBFB
16      67066671        67066808        exon4|NM_022845.3|CBFB
16      67082202        67082318        exon5|NM_022845.3|CBFB
16      67098699        67101068        exon6|NM_022845.3|CBFB
6       45328319        45328470        exon1|NM_001024630.4|RUNX2
6       45328650        45328794        exon2|NM_001024630.4|RUNX2
6       45422582        45422967        exon3|NM_001024630.4|RUNX2
6       45431852        45432029        exon4|NM_001024630.4|RUNX2
6       45437936        45438061        exon5|NM_001024630.4|RUNX2
6       45491930        45492124        exon6|NM_001024630.4|RUNX2
6       45512235        45512417        exon7|NM_001024630.4|RUNX2
6       45545206        45545292        exon8|NM_001024630.4|RUNX2
6       45546816        45551092        exon9|NM_001024630.4|RUNX2
```
## Compare Bed Files
This function enables a user to provide 2 bed file paths in order to compare them, generating a txt file containing all coordinates that differ between them.

This can be useful when seeing which regions would be missed if a patient was ran on two different panels. 

The output file is put into a folder called 'bedfile_comparisons'.
#### Usage:
```bash
#Either
python PanelPal/compare_bedfile.py R415_v1.0_GRCh38.bed R415_v1.6_GRCh38.bed

#Or
PanelPal compare-bed-files R415_v1.0_GRCh38.bed R415_v1.6_GRCh38.bed
```
#### Output: bedfile_comparisons/comparisons_R415_V1.0_GRCh38.bed_R415_V1.6_GRCh38.bed.txt
```
Entry                                                       Comment                                 
====================================================================================================
16_67029138_67029495_exon1|NM_022845.3|CBFB                 # Present in R415_v1.6_GRCh38.bed only
16_67029716_67029823_exon2|NM_022845.3|CBFB                 # Present in R415_v1.6_GRCh38.bed only
16_67036628_67036765_exon3|NM_022845.3|CBFB                 # Present in R415_v1.6_GRCh38.bed only
16_67066671_67066808_exon4|NM_022845.3|CBFB                 # Present in R415_v1.6_GRCh38.bed only
16_67082202_67082318_exon5|NM_022845.3|CBFB                 # Present in R415_v1.6_GRCh38.bed only
16_67098699_67101068_exon6|NM_022845.3|CBFB                 # Present in R415_v1.6_GRCh38.bed only
```

# Database

PanelPal comes with an integrated database that is automatically created on startup and persists on the user's local computer or server. The database uses SQLAlchemy's Object-Relational Mapping (ORM) framework to store and manage patient information, BED file metadata, and panel data.

The schema consists of three main tables:

<img src="(images/schema.jpg)" width="552" height="654">

## Usage:
As well as manually adding records using SQL queries, PanelPal provides a convenient way to insert data via its built-in `generate-bed` function. During this process, users are prompted to optionally enter patient information, which is then stored in the database.

#### Example prompt:
```bash
>>> patient_info = patient_info_prompt()
Add patient to database? (Default = 'yes', type 'n' to skip): yes
Patient ID (NHS number, 10 digits): 1234567890
Patient name: John Doe
Patient's date of birth (DD-MM-YYYY): 01-01-1990
>>> patient_info
{'patient_id': '1234567890', 'patient_name': 'John Doe', 'dob': datetime.date(1990, 1, 1)}
```
If the user chooses to skip entering patient information (by typing n), the system will proceed with generating the BED file without adding the patient record to the database.