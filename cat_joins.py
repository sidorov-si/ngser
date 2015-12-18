#!/usr/bin/env python


"""
Concatenate join(...) records in GenBank.

Usage:
  cat_join.py -i <input_gb_file> -o <output_gb_file>

Options:
  -h --help             Show this screen.
  --version             Show version.
  -i <input_GFF_file>   Input GenBank file.
  -o <output_GFF_file>  Output GenBank file.
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


def cat_join(input_gb_filename, output_gb_filename):
    print 'Input GenBank file:   ', input_gb_filename
    print 'Output GenBank file:  ', output_gb_filename
    print
    print 'Go through the input GenBank file and concatenate each join...'
    with open(input_gb_filename, 'r') as input_gb_file, \
         open(output_gb_filename, 'w') as output_gb_file:
        records_processed = 0
        join_list = []
        for line in input_gb_file:
            if 'join' in line or 'complement' in line:
                join_list.append(line.rstrip('\n'))
                continue
            elif ',' in line or ')' in line:
                join_list.append(line.strip(' \n'))
                continue
            elif join_list:
                output_gb_file.write(''.join(join_list) + '\n')
                del join_list[:]
                records_processed += 1
                if records_processed % 1000 == 0 and records_processed != 0:
                    print 'Processed', records_processed, 'records.'
            output_gb_file.write(line)

    print 'Finished.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='cat_join 0.1')
    input_gb_filename = arguments["-i"]
    if not exists(input_gb_filename):
        print "Error: Can't find an input GenBank file: no such file '" + \
              input_gb_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_gb_filename):
        print "Error: Input GenBank file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    output_gb_filename = arguments["-o"].rstrip('/')

    cat_join(input_gb_filename, output_gb_filename)

