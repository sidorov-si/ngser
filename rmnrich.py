#!/usr/bin/env python
"""
Remove reads with more than X% of 'N' bases.

Usage:
  rmnrich.py -i <input_file_1> [-j <input_file_2> -o <output_directory> -x <X_threshold>]

Options:
  -h --help              Show this screen.
  --version              Show version.
  -i <input_file_1>      File with reads to be filtered (the only input file in case of single-end reads and the left-reads file in case of paired-end reads).
  -j <input_file_2>      File with right reads (only for paired-end libraries).
  -o <output_directory>  Output directory name. Default: directory that contains this script.
  -x <X_threshold>       'N' base % threshold for reads removing (from 0 to 99). Default: 10.
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
from os.path import basename
from os.path import splitext
from os.path import join
from os import makedirs


def remove_n_rich(n_threshold, left_reads_filename, right_reads_filename, output_directory):
    left_output_name = splitext(basename(left_reads_filename))[0] + '.Nleq' + \
                       str(n_threshold) + '.fastq'
    left_output = join(output_directory, left_output_name)
    print 'Left (forward or single) reads file: ' + left_reads_filename
    print 'Left (forward or single) reads output file: ' + left_output
    with open(left_reads_filename, 'r') as left, open(left_output, 'w') as left_out:
        right_exists = False
        if right_reads_filename != None:
            right = open(right_reads_filename, 'r')
            right_output_name = splitext(basename(right_reads_filename))[0] + '.Nleq' + \
                                str(n_threshold) + '.fastq'
            right_output = join(output_directory, right_output_name)
            right_out = open(right_output, 'w')
            right_exists = True
            print 'Right (reverse) reads file: ' + right_reads_filename
            print 'Right (reverse) reads output file: ' + right_output
        reads_number = 0
        skipped_reads_num = 0
        print 'Started reads processing.'
        while True:
            left_id = left.readline().rstrip('\n')
            if not left_id:
                if right_exists:
                    right_line = right.readline().rstrip('\n')
                    if right_line:
                        print 'Error: FASTQ file ' + right_reads_filename + \
                              ' contains more lines than ' + left_reads_filename
                        sys.exit(1)
                break # EOF is reached
            reads_number += 1
            if reads_number % 1000000 == 0:
	        print reads_number, 'of reads are processed.'
            left_seq = left.readline().rstrip('\n')
            if not left_seq: # FASTQ file is incomplete
                print 'Error: FASTQ file ' + left_reads_filename + ' is incomplete.'
                print 'The last line is'
                print left_id
                if right_exists:
                    right.close()
                sys.exit(1)
            left_delim = left.readline().rstrip('\n')
            if not left_delim: # FASTQ file is incomplete
                print 'Error: FASTQ file ' + left_reads_filename + ' is incomplete.'
                print 'The last lines are'
                print left_id
                print left_seq
                if right_exists:
                    right.close()
                sys.exit(1)
            left_quality = left.readline().rstrip('\n')
            if not left_quality: # FASTQ file is incomplete
                print 'Error: FASTQ file ' + left_reads_filename + ' is incomplete.'
                print 'The last lines are'
                print left_id
                print left_seq
                print left_delim
                if right_exists:
                    right.close()
                sys.exit(1)
            if right_exists:
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

            left_len = len(left_seq)
            if left_len == 0:
                print 'Skip a read with 0 length.'
                skipped_reads_num += 1
                continue
            left_n_content = left_seq.count('N')
            left_fraction = float(left_n_content) / float(left_len)
            if left_fraction * 100 > float(n_threshold):
                continue
            elif right_exists:
                right_len = len(right_seq)
                if right_len == 0:
                    print 'Skip a read with 0 length'
                    continue
                right_n_content = right_seq.count('N')
                right_fraction = float(right_n_content) / float(right_len)
                if right_fraction * 100 > float(n_threshold):
                    continue
            left_out.write(left_id + '\n')
            left_out.write(left_seq + '\n')
            left_out.write(left_delim + '\n')
            left_out.write(left_quality + '\n')
            if right_exists:
                right_out.write(right_id + '\n')
                right_out.write(right_seq + '\n')
                right_out.write(right_delim + '\n')
                right_out.write(right_quality + '\n')

        if right_exists:
            right.close()

        if skipped_reads_num != 0:
            print 'Skipped ' + str(skipped_reads_num) + ' reads with 0 length.'

        print 'Finished reads processing.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='rmnrich 0.2')
    left_reads_filename = arguments["-i"]

    if not exists(left_reads_filename):
        print "Error: Can't find file with left (or single) reads: no such file '" + \
              left_reads_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(left_reads_filename):
        print "Error: File with left (or single) reads must be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    if arguments["-j"] != None: # reads are paired-end
        right_reads_filename = arguments["-j"]
        if not exists(right_reads_filename):
            print "Error: Can't find file with right reads: no such file '" + \
                  right_reads_filename + "'. Exit.\n"
            sys.exit(1)
        if not isfile(right_reads_filename):
            print "Error: File with right reads must be a regular file. " + \
                  "Something else given. Exit.\n"
            sys.exit(1)
    else:
       right_reads_filename = None

    if arguments["-o"] != None:
        output_directory = arguments["-o"].rstrip('/')
    else:
        output_directory = ''

    if arguments["-x"] != None:
        try:
            n_threshold = int(arguments["-x"])
        except ValueError:
            print "Error: N percentage must be an integer from the interval [0, 99]. Exit.\n"
            sys.exit(1)
        if n_threshold < 0 or n_threshold > 99:
            print "Error: N percentage must be an integer from the interval [0, 99]. Exit.\n"
            sys.exit(1)
    else:
        n_threshold = 10 # remove all reads with 'N' percentage grater than 10.

    if output_directory != '':
        if not exists(output_directory):
            makedirs(output_directory)
    
    remove_n_rich(n_threshold, left_reads_filename, right_reads_filename, output_directory)

