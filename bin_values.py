#!/usr/bin/env python
"""
Take a column of numbers as input and calc the count of each number.
Output pairs (number, count) in a tab-delimited file.

Usage:
  bin_values.py -i <input_file> -o <output_file>

Options:
  -h --help             Show this screen.
  --version             Show version.
  -i <input_filename>   Input file with a column of numbers.
  -o <output_filename>  Output file with a histogram.
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
from sys import stdout
from os.path import exists
from os.path import isfile


def bin_values(input_filename, output_filename):
    with open(input_filename, 'r') as infile:
        histo_dict = dict()
        for index, line in enumerate(infile):
            value = int(line.strip())
            if value in histo_dict:
                histo_dict[value] += 1
            else:
                histo_dict[value] = 1
            if index % 100000 == 0 and index != 0:
                print 'Processed', index, 'records.'
        with open(output_filename, 'w') as outfile:
            for key, value in sorted(histo_dict.iteritems()):
                outfile.write(str(key) + '\t' + str(value) + '\n')


if __name__ == '__main__':
    arguments = docopt(__doc__, version='bin_values 0.1')
    input_filename = arguments["-i"]
    if not exists(input_filename):
        print "Error: Can't find input file: no such file '" + \
              input_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_filename):
        print "Error: input file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)
    output_filename = arguments["-o"]

    bin_values(input_filename, output_filename)

