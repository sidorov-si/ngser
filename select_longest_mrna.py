#!/usr/bin/env python

"""
Select only the longest transcript for each gene in a GFF file.

Usage:
  select_longest_mrna.py -i <input_GFF_file> -o <output_GFF_file>

Options:
  -h --help             Show this screen.
  --version             Show version.
  -i <input_GFF_file>   Input GFF file.
  -o <output_GFF_file>  Output GFF file.
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


def filter_gff(input_gff_filename, output_gff_filename):
    print 'Input GFF file:   ', input_gff_filename
    print 'Output GFF file:  ', output_gff_filename
    print
    print 'Scan GFF to find the longest transcript for each gene...'
    with open(input_gff_filename, 'r') as input_gff_file:
        mrna_processed = 0
        max_lens = dict() # key: gene_id, value: longest mrna length
        max_mrna_id = dict() # key: gene_id, value: longest mrna id
        for record in input_gff_file:
            if record.startswith('#') or record == '\n':
                continue
            record_fields = record.split()
            record_type = record_fields[2]
            record_comment = ''.join(record_fields[8:])
            if record_type == 'mRNA' or record_type == 'mrna':
                mrna_processed += 1
                if mrna_processed % 100 == 0:
                    print mrna_processed, 'mRNA processed.'
                gene_id = search(r'Parent=([a-zA-Z0-9]*)', record_comment).group(1)
                mrna_id = search(r'ID=([a-zA-Z0-9]*)', record_comment).group(1)
                mrna_start = int(record_fields[3])
                mrna_end = int(record_fields[4])
                mrna_len = mrna_end - mrna_start + 1
                if gene_id in max_lens:
                    if mrna_len > max_lens[gene_id]:
                        max_lens[gene_id] = mrna_len
                        max_mrna_id[gene_id] = mrna_id
                else:
                    max_lens[gene_id] = mrna_len
                    max_mrna_id[gene_id] = mrna_id
    print 'Finished.'

    max_mrna_id_list = [value for key, value in max_mrna_id.items()]
    max_mrna_id_set = set(max_mrna_id_list)
    
    print 'Exclude mRNA, exon, and CDS records corresponding to the excluded mRNA ID list...',

    with open(output_gff_filename, 'w') as output_file, \
         open(input_gff_filename, 'r') as input_file:
        for record in input_file:
            if record.startswith('#') or record == '\n':
                output_file.write(record)
                continue
            record_fields = record.split()
            record_type = record_fields[2]
            record_comment = ''.join(record_fields[8:])
            if record_type == 'mRNA' or record_type == 'mrna':
                mrna_id = search(r'ID=([a-zA-Z0-9]*)', record_comment).group(1)
            elif record_type == 'CDS' or record_type == 'exon':
                mrna_id = search(r'Parent=([a-zA-Z0-9]*)', record_comment).group(1)
            else:
                output_file.write(record)
                continue
            if mrna_id not in max_mrna_id_set:
                continue 
            output_file.write(record)
    print 'Finished.\n'
 
    print 'Finished selecting.'
    print mrna_processed, 'mRNA records were processed.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='select_longest_mrna 0.1')
    input_gff_filename = arguments["-i"]
    if not exists(input_gff_filename):
        print "Error: Can't find an input GFF file: no such file '" + \
              input_gff_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(input_gff_filename):
        print "Error: Input GFF file must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    output_gff_filename = arguments["-o"].rstrip('/')

    filter_gff(input_gff_filename, output_gff_filename)

