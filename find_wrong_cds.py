#!/usr/bin/env python


"""
Output IDs of loci with incorrect CDS from a GenBank file.
Correct CDS must contain start and stop codon, have no extra stop codon 
in frame, and its length must be a multiple of 3.

Usage:
  find_wrong_cds.py -i <input_gb_file> -o <output_gb_file>

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -i <input_GenBank_file>   Input GenBank file.
  -o <output_GenBank_file>  Output GenBank file.
"""

import sys

print

modules = ["docopt", "os", "Bio"]
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
from Bio import SeqIO
from Bio import Alphabet


def find_wrong_cds(input_gb_filename, output_gb_filename):
    print 'Input GenBank file:   ', input_gb_filename
    print 'Output GenBank file:  ', output_gb_filename
    print
    print 'Go through the input GenBank file and write out IDs of loci with incorrect CDS...'
    with open(output_gb_filename, 'w') as output_gb_file:
        records_processed = 0
        for gb_record in SeqIO.parse(open(input_gb_filename, "r"), "genbank"):
            for gb_feature in gb_record.features:
                if gb_feature.type != 'CDS':
                    continue
                extracted_seq = gb_feature.extract(gb_record.seq)
                try:
                    protein_seq = extracted_seq.translate(cds = True)
                except Exception, err:
                    output_gb_file.write(gb_record.id + '\t' + '"' + str(err) + '"\n')
                break
            records_processed += 1
            if records_processed % 1000 == 0:
                print 'Processed', records_processed, 'records.'

    print 'Finished.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='find_wrong_cds 0.2')
    input_gb_filename = arguments["-i"]
    if not exists(input_gb_filename):
        print "Error: Can't find an input GenBank file: no such file '" + \
              input_gb_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_gb_filename):
        print "Error: Input GenBank file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    output_gb_filename = arguments["-o"]

    find_wrong_cds(input_gb_filename, output_gb_filename)

