#!/usr/bin/env python
"""
Remove reads with more than fraction_threshold% of low quality bases (bases with quality less than quality_threshold).
Phred+33 quality encoding is supposed by default.

Usage:
  rmlowq.py -i <input_file_1> [-j <input_file_2> -o <output_directory> -f <fraction_threshold> -q <quality_threshold> -b <quality_encoding_base>]

Options:
  -h --help                   Show this screen.
  --version                   Show version.
  -i <input_file_1>           File with reads to be filtered (the only input file in case of single-end reads and the left-reads file in case of paired-end reads).
  -j <input_file_2>           File with right reads (only for paired-end libraries).
  -o <output_directory>       Output directory name. Default: directory that contains this script.
  -f <fraction_threshold>     The threshold for percentage of low quality bases (from 0 to 99). Default: 60.
  -q <quality_threshold>      Quality threshold (minimal score that is not considered low). Default: 7.
  -b <quality_encoding_base>  It should be 33 for Phred+33 and 64 for Phred+64. Default: 33.
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


def rm_low_quality_reads(f_threshold, q_threshold, left_reads_filename, right_reads_filename, \
                         output_directory, q_base):
    left_output_name = splitext(basename(left_reads_filename))[0] + '.q' + \
                       str(q_threshold) + 'f' + str(f_threshold) + '.fastq'
    left_output = join(output_directory, left_output_name)
    with open(left_reads_filename, 'r') as left, open(left_output, 'w') as left_out:
        right_exists = False
        if right_reads_filename != None:
            right = open(right_reads_filename, 'r')
            right_output_name = splitext(basename(right_reads_filename))[0] + '.q' + \
                                str(q_threshold) + 'f' + str(f_threshold) + '.fastq'
            right_output = join(output_directory, right_output_name)
            right_out = open(right_output, 'w')
            right_exists = True
        read_num = 0
        skipped_reads_num = 0
        print 'Started reads processing.'
        while True:
            left_id = left.readline().rstrip('\n')
            if not left_id:
                right_line = right.readline().rstrip('\n')
                if right_line:
                    print 'Error: FASTQ file ' + right_reads_filename + \
                          ' contains more lines than ' + left_reads_filename
                    sys.exit(1)
                break # EOF is reached
            read_num += 1
            if read_num % 1000000 == 0:
	        print read_num, 'of reads are processed.'
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
                    print 'There is a read with ID ' + left_id + ' in ' + left_reads_filename + ' but no corresponding read in ' + right_reads_filename
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
            left_low_scores = [score for score in list(left_quality) \
                               if ord(score) < q_base + q_threshold]
            left_low_scores_count = len(left_low_scores)
            left_fraction = float(left_low_scores_count) / float(left_len)
            if left_fraction * 100 > float(f_threshold):
                continue
            elif right_exists:
                right_len = len(right_seq)
                if right_len == 0:
                    print 'Skip a read with 0 length.'
                    skipped_reads_num += 1
                    continue
                right_low_scores = [score for score in list(right_quality) \
                                    if ord(score) < q_base + q_threshold]
                right_low_scores_count = len(right_low_scores)
                right_fraction = float(right_low_scores_count) / float(right_len)
                if right_fraction * 100 > float(f_threshold):
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
            print 'Skipped ' + str(skipped_reads_num) + ' with 0 length.'

        print 'Finished reads processing.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='rmlowq 0.3')
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

    if arguments["-f"] != None:
        try:
            f_threshold = int(arguments["-f"])
        except ValueError:
            print "Error: Fraction threshold (%) must be an integer from the interval [0, 99]. Exit.\n"
            sys.exit(1)
        if f_threshold < 0 or f_threshold > 99:
            print "Error: Fraction threshold (%) must be an integer from the interval [0, 99]. Exit.\n"
            sys.exit(1)
    else:
        f_threshold = 60 

    if arguments["-q"] != None:
        try:
            q_threshold = int(arguments["-q"])
        except ValueError:
            print "Error: Quality threshold must be an integer from the interval [0, 41]. Exit.\n"
            sys.exit(1)
        if q_threshold < 0 or q_threshold > 41:
            print "Error: Quality threshold must be an integer from the interval [0, 41]. Exit.\n"
            sys.exit(1)
    else:
        q_threshold = 10 # Minimum allowed quality.

    if arguments['-b'] != None:
        try:
            q_base = int(arguments["-b"])
        except ValueError:
            print "Error1: Quality encoding threshold must be 33 or 64. Exit.\n"
            sys.exit(1)
        if q_base != 33 and q_base != 64:
            print "Error: Quality encoding threshold must be 33 or 64. Exit.\n"
            sys.exit(1)
    else:
       q_base = 33 # For Phred+33 quality encoding.

    if output_directory != '':
        if not exists(output_directory):
            makedirs(output_directory)

    rm_low_quality_reads(f_threshold, q_threshold, left_reads_filename, right_reads_filename, \
                         output_directory, q_base)

