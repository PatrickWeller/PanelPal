"""
Main entry point for the PanelPal toolkit, which provides functionalities
for querying and generating BED files for genomic panels.

The script offers several primary subcommands:

1. **check-panel**:
   This subcommand allows users to check panel information based on the panel ID.
   It queries panel details, such as name and version, from the PanelApp API.

2. **generate-bed**:
   This subcommand generates a BED file for a specified genomic panel.
   It requires the panel ID, version, and genome build to generate the appropriate BED file.

3. **compare-panel-versions**:
   This subcommand allows users to compare two versions of the same panel ID.
   It requires the panel ID, two version numbers, and can take a filter for gene status.

Parameters
----------
None (this is an entry point for the script, which processes commands and arguments via argparse).

Subcommands
-----------
- **check-panel**: Check panel information for a given panel ID.
- **generate-bed**: Generate a BED file for a genomic panel.
- **compare-panel-versions**: Compare two versions of a genomic panel.

Examples
--------
To check panel information for a specific panel ID:
    $ PanelPal check-panel --panel_id R59

To generate a BED file for a specific panel, version, and genome build:
    $ PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38

To query the gene differences between two versions of a panel:
    $ PanelPal compare-panel-versions --panel_id R21 --versions 1.0 2.2 --status_filter green
"""

import argparse
from .check_panel import main as check_panel_main
from .generate_bed import main as generate_bed_main
from .compare_panel_versions import main as compare_panel_versions_main
from .compare_panel_versions import validate_panel
from .query_db import setup_db, query_patient


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
                            Example: PanelPal generate-bed --panel_id R59 --panel_version 4 --genome_build GRCh38

    compare-panel-versions  Compare two versions of a genomic panel. Requires
                            the panel ID and two version numbers. Optionally, filter by gene status.
                            Example: PanelPal compare-panel-versions --panel R21 --versions 1.0 2.2 --status_filter green
    --help, -h              Prints this help message

Database Operations:
    db query-patient        Query a patient's data by name from the database

    db setup-db             Set up the database (if not already set up)

    """
    print(help_message)


def setup_db_subcommands(parser_db):
    """
    Set up subcommands related to database functionality.
    """
    db_subparsers = parser_db.add_subparsers(dest='db_command')

    # Add a command for setting up the database
    setup_parser = db_subparsers.add_parser(
        'setup-db', help="Set up the database")
    setup_parser.add_argument(
        '--force', action='store_true', help='Force setup even if database exists')

    # Add a command for querying the database
    query_parser = db_subparsers.add_parser(
        'query-patient', help="Query the database")
    query_parser.add_argument(
        '--name', type=str, nargs='+', required=True, help='Patient name to search for')


def main():
    """Main function which gathers arguments and passes them to the relevant PanelPal command."""
    parser = argparse.ArgumentParser(
        description="PanelPal: A toolkit for helping UK labs implement the National Test Directory for rare disease",
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
        choices=["green", "amber", "all"],
        default="green",
        help="Filter by gene status. Green only; green and amber; or all",
    )

    # subcommand group: Database-related operations
    parser_db = subparsers.add_parser(
        "db",
        help="Database operations that query different information.",
    )

    # subcommand: query patient
    db_subparsers = parser_db.add_subparsers(
        dest="db_command",  # destination
        title="DB Subcommands",
    )

    # subcommand for setup-db and query-patient
    parser_setup_db = db_subparsers.add_parser(
        "setup-db", help="Set up the database")
    parser_setup_db.add_argument(
        '--force', action='store_true', help="Force setup even if database exists"
    )

    parser_query_patient = db_subparsers.add_parser(
        "query-patient",
        help="Query patient information from the database by name."
    )
    parser_query_patient.add_argument(
        "--patient_name",
        type=str,
        required=True,
        help="Patient name to query, e.g., 'John Doe'."
    )

    args = parser.parse_args()

    if not args.command:
        print_help()
        exit(1)

    # Execute corresponding subcommands
    if args.command == "check-panel":
        check_panel_main(args.panel_id)
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
    elif args.command == "db":
        if args.db_command == "setup-db":
            force = args.force
            setup_db(force=force)
        elif args.db_command == "query-patient":
            patient_name = args.patient_name
            setup_db()  # Ensure the DB is set up before querying
            query_patient(patient_name)
    else:
        print_help()


if __name__ == "__main__":
    main()
