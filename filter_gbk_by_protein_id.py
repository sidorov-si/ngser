#!/usr/bin/env python
"""
Filter GBK file by protein_id value (a ref ID of protein).
Retain only those locuses which product_id is contained in a ref_IDs_list.
There must be one ID per line in ref_IDs_list file.

Usage:
  filter_gbk_by_protein_id.py -i <input_GBK_file> -f <ref_IDs_list> -o <output_GBK_file>

Options:
  -h --help             Show this screen.
  --version             Show version.
  -i <input_GBK_file>   Input GBK file.
  -f <ref_IDs_list>     List of protein ref IDs by which to filter the GBK file (one ID per line).
  -o <output_GBK_file>  Output GBK file.
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


def filter_gbk(input_gbk_filename, ref_list_filename, output_gbk_filename):
    print 'Input GBK file:   ', input_gbk_filename
    print 'File with ref IDs:', ref_list_filename
    print 'Output GBK file:  ', output_gbk_filename
    with open(ref_list_filename, 'r') as ref_list_file:
        ref_list = [ref[:-1] for ref in ref_list_file] # read all IDs without '\n'
        ref_set = set(ref_list)
    with open(input_gbk_filename, 'r') as infile, open(output_gbk_filename, 'w') as outfile:
        print 'Start filtering.'
        locus = []
        skip_locus = False
        loci_count = 0
        protein_id = ''
        while True:
            line = infile.readline().rstrip('\n')
            if not line:
                break # EOF is reached
            if 'LOCUS' in line: # begin to read a new locus
                if loci_count != 0 and loci_count % 100 == 0:
                    print loci_count, 'loci are processed.'
                loci_count += 1
            if not skip_locus:
                locus.append(line)
                if 'protein_id' in line:
                    protein_id = (line.split('"'))[1]
                    if protein_id not in ref_set:
                        skip_locus = True
                if line == '//': # end of the locus is reached (locus isn't skipped)
                    if protein_id != '': # the locus is protein coding
                        for line in locus:
                            outfile.write(line + '\n')
                        protein_id = ''
                    del locus[:]
            elif line == '//': # end of the locus is reached (locus is skipped)
                skip_locus = False
                protein_id = ''
                del locus[:]
            else:
                continue # skipping lines of the locus
        print 'Finished filtering.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='filter_gbk_by_protein_id 0.1')
    input_gbk_filename = arguments["-i"]
    if not exists(input_gbk_filename):
        print "Error: Can't find an input GBK file: no such file '" + \
              input_gbk_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_gbk_filename):
        print "Error: Input GBK file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    ref_list_filename = arguments["-f"]
    if not exists(ref_list_filename):
        print "Error: Can't find a file with ref IDs list: no such file '" + \
              ref_list_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(ref_list_filename):
        print "Error: File with ref IDs list be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)

    output_gbk_filename = arguments["-o"].rstrip('/')

    filter_gbk(input_gbk_filename, ref_list_filename, output_gbk_filename)

