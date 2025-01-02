# User Manual

### Installation
To install and set up PanelPal, see the [Installation Guide](installation.md).

### Boot Up PanelPal's Docker Container
If PanelPal is already installed, then run the docker container.
```bash
docker run -it panelpal
```
# Command Line Functions

## Check Panel
To check and retrieve panel information from the PanelApp API:

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

## Get panels containing a given gene
To generate a list of panels containing a specific gene (e.g. BRCA1):

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
To compare the genes on two versions of a given panel:

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
To generate a bed file for a given panel:

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
To compare the content of two bed files:

```bash
#Either
python PanelPal/compare_bedfile.py bedfile1.bed bedfile2.bed

#Or
PanelPal compare-bed-files bedfile1.bed bedfile2.bed
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