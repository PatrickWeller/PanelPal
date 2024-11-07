"""
Add Analysis Record

Script that will add a patient record to a database

"""
import argparse

def main():
    args = argument_parser()
    sample = args.sample
    panel = args.panel
    version = args.version

def argument_parser():
    """
    Argument parser for running AddAnalysis Record.
    - Sample and panel are required fields.
    - Panel Version is optional
    
    To recall variables use:
    args = argument_parser.parse_args()
    sample = args.sample
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-s', '--sample', type=str, help='Sample identifier or a CSV of sample identifiers', required=True)
    argument_parser.add_argument('-p', '--panel', help='R number. Include the R', required=True)
    argument_parser.add_argument('-v', '--version', help='Panel version. E.g. 1.1', required=False)
    args = argument_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
