import variant_validator_api_functions

gene_list = ["KCNQ1 ","CDKN1C"]
panel_name = "KCNQ1"
panel_version = "test"
genome_build = "GRCh38"

variant_validator_api_functions.generate_bed_file(gene_list, panel_name, panel_version, genome_build)
variant_validator_api_functions.bedtools_merge(panel_name, panel_version, genome_build)


