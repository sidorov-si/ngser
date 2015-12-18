#!/usr/bin/env python


"""
Filter GenBank file by locus ID.

Usage:
  filter_gb_by_id.py -i <input_gb_file> -e <file_with_IDs> -o <output_gb_file>

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -i <input_GenBank_file>   Input GenBank file.
  -e <file_with_IDs>        File with IDs of loci that must be filtered out. One ID per line.
  -o <output_GenBank_file>  Output GenBank file.
"""

import sys

print

modules = ["docopt", "os"]
exit_flag = False
for module in modules:
    try:
        __import__(module)
    except ImportError:
        exit_flag = True
        sys.stderr.write("Error: Python module " + module + " is not installed.\n")
if exit_flag:
    sys.stderr.write("You can install these modules with a command: pip install <module>\n")
    sys.stderr.write("(Administrator privileges may be required.)\n")
    sys.exit(1)


from docopt import docopt
from os.path import exists
from os.path import isfile
from re import search
from os import remove


def filter_gb_by_id(input_gb_filename, id_filename, output_gb_filename):
    print 'Input GenBank file: ', input_gb_filename
    print 'File with locus IDs:', id_filename
    print 'Output GenBank file:', output_gb_filename
    print
    print 'Store loci IDs...'
    id_set = set()
    with open(id_filename, 'r') as id_file:
        for line in id_file:
            locus_id = line.strip().split('\t')[0]
            id_set.add(locus_id)
    print 'Finished.'
    print 'Go through the input GenBank file and filter out loci with specific IDs...'
    with open(input_gb_filename, 'r') as input_gb_file, \
         open(output_gb_filename, 'w') as output_gb_file:
        records_processed = 0
        for line in input_gb_file:
            if 'LOCUS' in line:
                filter_out = False
                locus_id = line.strip().split()[1]
                if locus_id in id_set:
                    filter_out = True
                else:
                    output_gb_file.write(line)
                records_processed += 1
                if records_processed % 1000 == 0:
                    print 'Processed', records_processed, 'records.'
            elif not filter_out:
                output_gb_file.write(line)
 
    print 'Finished.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='filter_gb_by_id 0.1')
    input_gb_filename = arguments["-i"]
    if not exists(input_gb_filename):
        print "Error: Can't find an input GenBank file: no such file '" + \
              input_gb_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_gb_filename):
        print "Error: Input GenBank file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    id_filename = arguments["-e"]
    if not exists(id_filename):
        print "Error: Can't find a file with IDs: no such file '" + \
              id_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(id_filename):
        print "Error: File with IDs must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        
    
    output_gb_filename = arguments["-o"].rstrip('/')

    filter_gb_by_id(input_gb_filename, id_filename, output_gb_filename)

