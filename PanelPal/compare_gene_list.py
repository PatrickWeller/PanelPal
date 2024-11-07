"""
Compare Gene Lists

Script that will compare two versions of a panel to see any gene differences between them

"""
import argparse

def main():
    panel, versions = argument_parser()
    print(panel)
    print(versions)
    
def argument_parser():
    """
    Argument parser for running Compare Gene Lists
    - Panel is a required field
    - And 2 version numbers, e.g. 1.1 are also a required field
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-p', '--panel', type=str, help='R number. Include the R', required=True)
    argument_parser.add_argument('-v', '--versions', type=str, help='Panel versions. E.g. 1.1, you must provide 2 values', nargs=2, required=True)
    args = argument_parser.parse_args()
    return args.panel, args.versions

def compare_lists(list1, list2):
    ...


if __name__ == "__main__":
    main()