"""
Add Analysis Record

Script that will add a patient record to a database

"""
import argparse

def argument_parser():
    
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument()
    argument_parser.add_argument()
    args = argument_parser.parse_args()
    return args

def main():
    args = argument_parser()
    print(args)

if __name__ == "__main__":
    main()
