import argparse
from check_panel import main as check_panel_main
from generate_bed import main as generate_bed_main
from compare_panel_versions import main as compare_panel_versions_main
from compare_panel_versions import validate_panel


def print_help():
    """Print custom help message for PanelPal."""
    help_message = """
PanelPal is a command-line toolkit designed for querying and generating genomic panel
BED files from PanelApp. It provides functionalities to:
  - Check panel details
  - Generate BED files for genomic panels
  - Compare versions of the same panel

Author: Team Jenkins
Version: 1.0.0

Available Commands:
  {check-panel,generate-bed,compare-panel-versions}
    check-panel         Check panel information for a given panel ID.
                        Example: PanelPal check-panel --panel_id R59

    generate-bed        Generate a BED file for a genomic panel. Requires the
                        panel ID, panel version, and genome build.
                        Example: PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38

    compare-panel-versions
                        Compare two versions of a genomic panel. Requires
                        the panel ID and two version numbers. Optionally, filter by gene status.
                        Example: PanelPal compare-panel-versions --panel R21 --versions 1.0 2.2 --status_filter green

Examples of full usage:
  - Check panel info:
      PanelPal check-panel --panel_id R59

  - Generate a BED file for a specific panel:
      PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38

  - Compare two panel versions with a status filter:
      PanelPal compare-panel-versions --panel R21 --versions 1.0 2.2 --status_filter green
    """
    print(help_message)


def main():
    """Main function which gathers arguments and passes them to the relevant PanelPal command."""
    parser = argparse.ArgumentParser(
        description="PanelPal: A toolkit for querying and generating genomic panel BED files.",
        epilog="For more details, visit https://yourprojecturl.com"
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

    # Subcommand: compare-panel-versions
    parser_versions = subparsers.add_parser(
        "compare-panel-versions",
        help="Compare two versions of a genomic panel.",
    )
    parser_versions.add_argument(
        "--panel", "-p",
        type=validate_panel,
        required=True,
        help='R number. Include the R.',
    )
    parser_versions.add_argument(
        "--versions", "-v",
        type=float,
        nargs=2,
        required=True,
        help='Two panel versions. E.g. 1.1 or 69.23',
    )
    parser_versions.add_argument(
        '--status_filter', "-f",
        choices=["green", "amber", "all"],
        default='green',
        help='Filter by gene status. Green only; green and amber; or all',
    )

    args = parser.parse_args()

    if not args.command:
        print_help()
        exit(1)

    if args.command == "check-panel":
        panel_id = args.panel_id
        check_panel_main(panel_id)
    elif args.command == "generate-bed":
        generate_bed_main(
            panel_id=args.panel_id,
            panel_version=args.panel_version,
            genome_build=args.genome_build,
        )
    elif args.command == "compare-panel-versions":
        compare_panel_versions_main(
            panel=args.panel,
            versions=args.versions,
            status_filter=args.status_filter,
        )
    else:
        print_help()


if __name__ == "__main__":
    main()
