"""
Main entry point for the PanelPal toolkit, which provides functionalities
for querying and generating BED files for genomic panels.

The script offers two primary subcommands:

1. **check-panel**:
    This subcommand allows users to check panel information based on the panel ID.
    It queries panel details, such as name and version, from the PanelApp API.

2. **generate-bed**:
    This subcommand generates a BED file for a specified genomic panel.
    It requires the panel ID, version, and genome build to generate the appropriate BED file.

Usage examples:
    - To check panel information for a specific panel ID:
        $ PanelPal check-panel --panel_id R59

    - To generate a BED file for a specific panel, version, and genome build:
        $ PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38
"""

import argparse
from check_panel import main as check_panel_main
from generate_bed import main as generate_bed_main
from gene_to_panels import main as gene_to_panels_main


def main():
    """Main function which gathers arguments and passes them to the relevant PanelPal command"""
    parser = argparse.ArgumentParser(
        description="panelpal: A toolkit for panelapp queries"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
    )

    # Subcommand: check-panel
    parser_check = subparsers.add_parser(
        "check-panel",
        help="Check panel information for a given panel ID.",
    )
    parser_check.add_argument(
        "--panel_id",
        type=str,
        required=True,
        help="Panel ID e.g. R59, r59, or 59.",
    )

    # Subcommand: generate-bed
    parser_bed = subparsers.add_parser(
        "generate-bed",
        help="Generate BED file for a panel.",
    )
    parser_bed.add_argument(
        "--panel_id",
        type=str,
        required=True,
        help='The ID of the panel, (e.g., "R207").',
    )
    parser_bed.add_argument(
        "--panel_version",
        type=str,
        required=True,
        help='The version of the panel (e.g., "4").',
    )
    parser_bed.add_argument(
        "--genome_build",
        type=str,
        required=True,
        help="The genome build (e.g., GRCh38).",
    )

    # Subcommand: gene-panels
    parser_gene_panels = subparsers.add_parser(
        "gene-panels",
        help="List panels containing a given gene",
    )
    parser_gene_panels.add_argument(
        "--hgnc_symbol",
        type=str,
        required=True,
        help="The HGNC symbol of the gene to query (e.g., BRCA1).",
    )

    args = parser.parse_args()

    if args.command == "check-panel":
        panel_id = args.panel_id
        check_panel_main(panel_id)
    elif args.command == "gene-panels":
        hgnc_symbol = args.hgnc_symbol
        gene_to_panels_main(hgnc_symbol)
    elif args.command == "generate-bed":
        panel_id=args.panel_id
        panel_version=args.panel_version,
        genome_build=args.genome_build
        generate_bed_main(panel_id, panel_version, genome_build)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
