"""
PanelPal toolkit: Query and generate BED files for genomic panels.

Main entry point for the PanelPal toolkit, which provides functionalities
for querying and generating BED files for genomic panels.

The script offers several primary subcommands:

1. **check-panel**:
   This subcommand allows users to check panel information based on the panel ID.
   It queries panel details, such as name and version, from the PanelApp API.

2. **generate-bed**:
   This subcommand generates a BED file for a specified genomic panel.
   It requires the panel ID, version, and genome build to generate the appropriate BED file.
   It can also accept a gene status for filtering.

3. **compare-panel-versions**:
   This subcommand allows users to compare two versions of the same panel ID.
   It requires the panel ID and two version numbers.
   It can also accept a gene status for filtering.

4. **compare-bed-files**:
    This subcommand compares two BED files and identifies the differences between them.
    It takes two BED files as input and writes the differences to an output file within the
    'bedfile_comparisons' directory.

5. **gene-panels**:
    This subcommand lists panels containing a given gene.
    It requires the HGNC symbol of the gene to query.
    Users can filter panels by confidence status and include panels without R codes.

6. **panel-genes**:
    This subcommand lists genes in a panel.
    It requires the panel ID and version.
    Users can filter genes by confidence status (default is 'green').

Parameters
----------
None (this is an entry point for the script, which processes commands and arguments via argparse).

Subcommands
-----------
- **check-panel**: Check panel information for a given panel ID.
- **generate-bed**: Generate a BED file for a genomic panel.
- **compare-panel-versions**: Compare two versions of a genomic panel.
- **compare-bed-files**: Compare two BED files and find the differences between them.
- **gene-panels**: List panels containing a given gene.
- **panel-genes**: List genes in a panel.

Examples
--------
To check panel information for a specific panel ID:
    $ PanelPal check-panel --panel_id R59

To generate a BED file for a specific panel, version, and genome build:
    $ PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38 
        --status_filter amber

To query the gene differences between two versions of a panel:
    $ PanelPal compare-panel-versions --panel R21 --versions 1.0 2.2 --status_filter green

To compare two BED files and identify the differences:
    $ PanelPal compare-bed-files file1.bed file2.bed

To list panels containing a specific gene:
    $ PanelPal gene-panels --hgnc_symbol BRCA1 --confidence_status green --show_all_panels

To list genes in a specific panel:
    $ PanelPal panel-genes --panel_id R207 --panel_version 1.2 --confidence_status green

"""
import sys
import argparse
import sys
from .check_panel import main as check_panel_main
from .generate_bed import main as generate_bed_main
from .gene_to_panels import main as gene_to_panels_main
from .compare_panel_versions import main as compare_panel_versions_main
from .compare_panel_versions import validate_panel
from .compare_bedfiles import main as compare_bed_files_main
from .panel_to_genes import main as panel_to_genes_main


def print_help():
    """Print custom help message for PanelPal."""
    help_message = """
PanelPal: A toolkit for panelapp queries
version: 1.0.0 

Available Commands:
    check-panel             Check panel information for a given panel ID.
                            Example: PanelPal check-panel --panel_id R59

    generate-bed            Generate a BED file for a genomic panel. Requires the
                            panel ID, panel version, and genome build.
                            Example: PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38 --status_filter red

    compare-panel-versions  Compare two versions of a genomic panel. Requires the panel ID and two version numbers. 
                            Optionally, filter by gene status.
                            Example: PanelPal compare-panel-versions --panel R21 --versions 1.0 2.2 --status_filter green

    gene-panels             List panels containing a given gene. Requires the HGNC symbol of the gene.
                            Default confidence status is 'green'. Optional arguments include 'confidence_status' 
                            (green, amber, red, green & amber). Use 'show_all_panels' to include panels without R codes.
                            Example: PanelPal gene-panels --hgnc_symbol BRCA1 --confidence_status green --show_all_panels
    
    compare-bed-files       Compare two BED files and find the differences between them.
                            Example: PanelPal compare-bed-files file1.bed file2.bed

    panel-genes             List genes in a panel. Requires the panel ID and version.
                            Default confidence status is 'green'. Optional arguments include 'confidence_status'

    --help, -h              Prints this help message
    """
    print(help_message)


def main():
    """Main function which gathers arguments and passes them to the relevant PanelPal command."""
    parser = argparse.ArgumentParser(
        description="PanelPal: A toolkit for helping UK labs "
        "implement the National Test Directory for rare disease",

        epilog="For more details, visit https://github.com/PatrickWeller/PanelPal",
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
        help="Generate a BED file for a genomic panel.",
    )
    parser_bed.add_argument(
        "--panel_id",
        type=str,
        required=True,
        help='The ID of the panel, (e.g., "R207").',
    )
    parser_bed.add_argument(
        "--panel_version",
        type=float,
        required=True,
        help='The version of the panel (e.g., "4").',
    )
    parser_bed.add_argument(
        "--genome_build",
        type=str,
        required=True,
        help="The genome build (e.g., GRCh38).",
    )
    parser_bed.add_argument(
        "--status_filter",
        "-f",
        choices=["green", "amber", "red", "all"],
        default="green",
        help="Filter by gene status. Green only; green and amber; or red / all",
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
    parser_gene_panels.add_argument(
        "--confidence_status",
        type=str,
        default="green",
        choices=["red", "amber", "green", "all", "green,amber"],
        help="Filter panels by confidence status. Defaults to 'green'.",
    )
    parser_gene_panels.add_argument(
        "--show_all_panels",
        action="store_true",
        help="Include panels without R codes in the output.",
    )

    # Subcommand: compare-panel-versions
    parser_versions = subparsers.add_parser(
        "compare-panel-versions",
        help="Compare two versions of a genomic panel.",
    )
    parser_versions.add_argument(
        "--panel",
        "-p",
        type=validate_panel,
        required=True,
        help="R number. Include the R.",
    )
    parser_versions.add_argument(
        "--versions",
        "-v",
        type=float,
        nargs=2,
        required=True,
        help="Two panel versions. E.g. 1.1 or 69.23",
    )
    parser_versions.add_argument(
        "--status_filter",
        "-f",
        choices=["green", "amber", "red", "all"],
        default="green",
        help="Filter by gene status. Green only; green and amber; or red / all",
    )

    # Subcommand: compare-bed-files
    parser_bed_files = subparsers.add_parser(
        "compare-bed-files",
        help="Compare two BED files and find the differences between them.",
    )
    parser_bed_files.add_argument(
        "file1",
        type=str,
        help="Path to the first BED file.",
    )
    parser_bed_files.add_argument(
        "file2",
        type=str,
        help="Path to the second BED file.",
    )

    # Subcommand: panel-genes
    parser_panel_genes = subparsers.add_parser(
        "panel-genes",
        help="List genes in a panel",
    )
    parser_panel_genes.add_argument(
        "--panel_id",
        type=str,
        required=True,
        help='The ID of the panel, (e.g., "R207").',
    )
    parser_panel_genes.add_argument(
        "--panel_version",
        type=float,
        required=True,
        help='The version of the panel (e.g., "4.0").',
    )
    parser_panel_genes.add_argument(
        "--confidence_status",
        type=str,
        default="green",
        choices=["red", "amber", "green", "all"],
        help=(
            "Filter panels by confidence status. Choices are 'green', 'amber', or 'red'. "
            "Defaults to 'green'."
        ),
    )
    
    # Parse the arguments
    args = parser.parse_args()

    if not args.command:
        print_help()
        sys.exit(1)

    if args.command == "check-panel":
        panel_id = args.panel_id
        check_panel_main(panel_id)
    elif args.command == "generate-bed":
        generate_bed_main(
            panel_id=args.panel_id,
            panel_version=args.panel_version,
            genome_build=args.genome_build,
            status_filter=args.status_filter,
        )
    elif args.command == "compare-panel-versions":
        compare_panel_versions_main(
            panel=args.panel,
            versions=args.versions,
            status_filter=args.status_filter,
        )
    elif args.command == "gene-panels":
        gene_to_panels_main(
            hgnc_symbol=args.hgnc_symbol,
            confidence_status=args.confidence_status,
            show_all_panels=args.show_all_panels,
        )
    elif args.command == "compare-bed-files":
        compare_bed_files_main(args.file1, args.file2)
    elif args.command == "panel-genes":
        panel_to_genes_main(args.panel_id, args.panel_version, args.confidence_status)
    else:
        print_help()


if __name__ == "__main__":
    main()
