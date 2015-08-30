#!/usr/bin/env python
"""
Merge forward reads from one FASTQ file with reverse reads in the other FASTQ file.
Merged reads are put in a separate FASTQ file.

Usage:
  rmerge.py -i <forwad_FASTQ_file> -j <reverse_FASTQ_file> -o <output_FASTQ_file> [-s <separator> | --forward-id]

Options:
  -h --help                Show this screen.
  --version                Show version.
  -i <forward_FASTQ_file>  FASTQ file with forward reads.
  -j <reverse_FASTQ_file>  FASTQ file with reverse reads.
  -o <output_FASTQ_file>   FASTQ file with merged reads.
  -s <separator>           A symbol or a group of symbols for reads id separation. Default: ' | '.
  --forward-id             Take an id of the forward read as an id of the merged read.
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


def rmerge(left_reads_filename, right_reads_filename, output_filename, forward_id):
    print 'Left reads:   ' + left_reads_filename
    print 'Right reads:  ' + right_reads_filename
    print 'Output reads: ' + output_filename
    with open(left_reads_filename, 'r') as left, open(right_reads_filename, 'r') as right, \
         open(output_filename, 'w') as out: 
        reads_number = 0
        print 'Started reads merging.'
        while True:
            left_id = left.readline().rstrip('\n')
            if not left_id:
                right_line = right.readline().rstrip('\n')
                if right_line:
                    print 'Error: FASTQ file ' + right_reads_filename + \
                          ' contains more lines than ' + left_reads_filename
                    sys.exit(1)
                break # EOF is reached
            reads_number += 1
            if reads_number % 1000000 == 0:
	        print reads_number, 'of reads are merged.'
            left_seq = left.readline().rstrip('\n')
            if not left_seq: # FASTQ file is incomplete
                print 'Error: FASTQ file ' + left_reads_filename + ' is incomplete.'
                print 'The last line is'
                print left_id
                right.close()
                sys.exit(1)
            left_delim = left.readline().rstrip('\n')
            if not left_delim: # FASTQ file is incomplete
                print 'Error: FASTQ file ' + left_reads_filename + ' is incomplete.'
                print 'The last lines are'
                print left_id
                print left_seq
                right.close()
                sys.exit(1)
            left_quality = left.readline().rstrip('\n')
            if not left_quality: # FASTQ file is incomplete
                print 'Error: FASTQ file ' + left_reads_filename + ' is incomplete.'
                print 'The last lines are'
                print left_id
                print left_seq
                print left_delim
                right.close()
                sys.exit(1)
            right_id = right.readline().rstrip('\n')
            if not right_id: # right_reads_filename file is incomplete
                print 'Error: FASTQ file ' + right_reads_filename + ' is incomplete.'
                print 'There is a read with ID ' + left_id + ' in ' + left_reads_filename + \
                      ' but no corresponding read in ' + right_reads_filename
                sys.exit(1)
            right_seq = right.readline().rstrip('\n')
            if not right_seq: # FASTQ file is incomplete
                print 'Error: FASTQ file' + right_reads_filename + ' is incomplete.'
                print 'The last line is'
                print right_id
                right.close()
                sys.exit(1)
            right_delim = right.readline().rstrip('\n')
            if not right_delim: # FASTQ file is incomplete
                print 'Error: FASTQ file' + right_reads_filename + ' is incomplete.'
                print 'The last lines are'
                print right_id
                print right_seq
                right.close()
                sys.exit(1)
            right_quality = right.readline().rstrip('\n')
            if not right_quality: # FASTQ file is incomplete
                print 'Error: FASTQ file' + right_reads_filename + ' is incomplete.'
                print 'The last lines are'
                print right_id
                print right_seq
                print right_delim
                right.close()
                sys.exit(1)

            if forward_id:
                out.write(left_id + '\n')
            else:
                right_id_no_at = right_id[1:]
                out.write(left_id + separator + right_id_no_at + '\n')
            out.write(left_seq + right_seq + '\n')
            if forward_id:
                out.write(left_delim + '\n')
            else:
                right_delim_no_plus = right_delim[1:]
                out.write(left_delim + separator + right_delim_no_plus + '\n')
            out.write(left_quality + right_quality + '\n')

        right.close()
        print 'Merged ' + str(reads_number) + ' read pairs.' 
        print 'Finished reads processing.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='rmerge 0.1')
    left_reads_filename = arguments["-i"]
    if not exists(left_reads_filename):
        print "Error: Can't find file with left (forward) reads: no such file '" + \
              left_reads_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(left_reads_filename):
        print "Error: File with left (forward) reads must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    right_reads_filename = arguments["-j"]
    if not exists(right_reads_filename):
        print "Error: Can't find file with right (reverse) reads: no such file '" + \
              right_reads_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(right_reads_filename):
        print "Error: File with right (reverse) reads must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)

    output_filename = arguments["-o"].rstrip('/')

    forward_id = False
    if arguments["-s"] != None:
        separator = arguments["-s"]
    elif arguments["--forward-id"]:
        forward_id = True
    else:
        separator = ' | '

    rmerge(left_reads_filename, right_reads_filename, output_filename, forward_id)

