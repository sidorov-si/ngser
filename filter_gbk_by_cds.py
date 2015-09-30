#!/usr/bin/env python

"""
Filter GBK file by CDS: retain only those records which have correct CDS.
Correct CDS must:
1) contain a 'product' field;
2) have length that is a multiple of 3;
3) have start and stop codons.

Usage:
  filter_gbk_by_cds.py -i <input_GBK_file> -o <output_GBK_file>

Options:
  -h --help             Show this screen.
  --version             Show version.
  -i <input_GBK_file>   Input GBK file.
  -o <output_GBK_file>  Output GBK file.
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


def filter_gbk(input_gbk_filename, output_gbk_filename):
    print 'Input GBK file:   ', input_gbk_filename
    print 'Output GBK file:  ', output_gbk_filename
    with open(output_gbk_filename, 'w') as outfile:
        print 'Start filtering.'
        total_count = 0
        filtered_count = 0
        for index, record in enumerate(SeqIO.parse(open(input_gbk_filename), "genbank")):
            cds_exists = False
            for number, feature in enumerate(record.features):
                if feature.type == 'CDS' and 'product' in feature.qualifiers:
                    cds_exists = True
                    try:
                        _ = feature.extract(record.seq).translate(cds = True)
                    except Exception, e: 
                        # something is wrong with this CDS (start and/or stop codons are missing,
                        # or the lenght of CDS is not a multiple of 3)
                        print 'Record', record.id, ':', str(e), '=> Filtered out.'
                        filtered_count += 1
                        continue # just take the next locus
                    SeqIO.write(record, outfile, "genbank")
            if not cds_exists:
                print 'Record', record.id, ':', 'No CDS => Filtered out.'
                filtered_count += 1
            if index % 100 == 0 and index != 0:
                print index, 'records are processed.'
            total_count = index + 1
    print 'Finished filtering.'
    print total_count, 'records were processed.'
    print filtered_count, 'of them were filtered out.'
    print str(total_count - filtered_count), 'records remain.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='filter_gbk_by_cds 0.2')
    input_gbk_filename = arguments["-i"]
    if not exists(input_gbk_filename):
        print "Error: Can't find an input GBK file: no such file '" + \
              input_gbk_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_gbk_filename):
        print "Error: Input GBK file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    output_gbk_filename = arguments["-o"].rstrip('/')

    filter_gbk(input_gbk_filename, output_gbk_filename)

