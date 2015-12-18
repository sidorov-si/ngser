#!/usr/bin/env python

"""
Filter out all 'partial=true' records from GFF file.

Usage:
  filter_partial.py -i <input_GFF_file> -o <output_GFF_file>

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
    with open(input_gff_filename, 'r') as input_gff_file:
        mrna_processed = 0
        mrna_filtered = 0
        mrna_id_to_exclude = set()
        gene_id_to_exclude = set()
        tmp_output_filename = output_gff_filename + '.tmp'
        with open(tmp_output_filename, 'w') as tmp_output_file:
            for record in input_gff_file:
                if record.startswith('#') or record == '\n':
                    tmp_output_file.write(record)
                    continue
                record_fields = record.split()
                record_type = record_fields[2]
                record_comment = ''.join(record_fields[8:])
                if record_type == 'mRNA' or record_type == 'mrna':
                    mrna_processed += 1
                    if mrna_processed % 100 == 0:
                        print mrna_processed, 'mRNA processed.'
                    if 'partial=true' in record_comment:
                        mrna_id = search(r'ID=([a-zA-Z0-9]*)', record_comment).group(1)
                        mrna_id_to_exclude.add(mrna_id)
                        gene_id = search(r'Parent=([a-zA-Z0-9]*)', record_comment).group(1)
                        gene_id_to_exclude.add(gene_id)
                        mrna_filtered += 1
                        continue
                elif record_type == 'exon' or record_type == 'CDS' or record_type == 'cds':
                    mrna_id = search(r'Parent=([a-zA-z0-9]*)', record_comment).group(1) 
                    if mrna_id in mrna_id_to_exclude:
                        continue
                tmp_output_file.write(record)
                
        print 'Exclude "gene" records corresponding to the excluded mRNA records...',

        with open(output_gff_filename, 'w') as output_gff_file, \
             open(tmp_output_filename, 'r') as tmp_output_file:
            for record in tmp_output_file:
                if record.startswith('#') or record == '\n':
                    output_gff_file.write(record)
                    continue
                record_fields = record.split()
                record_type = record_fields[2]
                record_comment = ''.join(record_fields[8:])
                if record_type == 'gene':
                    gene_id = search(r'ID=([a-zA-Z0-9]*)', record_comment).group(1)
                    if gene_id in gene_id_to_exclude:
                        continue
                output_gff_file.write(record)
        remove(tmp_output_filename)
        print 'Finished.\n'
 
        print 'Finished filtering.'
        print mrna_processed, 'mRNA records were processed.'
        print mrna_filtered, 'of them were filtered out.'
        print str(mrna_processed - mrna_filtered), 'records remain.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='filter_partial 0.1')
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

