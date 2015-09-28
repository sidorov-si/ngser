#!/usr/bin/env python
"""
Subtract one list of kmers from the other (both lists should be sorted).
kmers must be of the same size.

Usage:
  subkmers.py -i <minuend_list> -j <subtrahend_list> -o <output_file>

Options:
  -h --help             Show this screen.
  --version             Show version.
  -i <minuend_list>     List from which to subract.
  -j <subtrahend_list>  List which is subtracted.
  -o <output_file>      A text file with result kmers.
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


def subtract_kmers(minuend_filename, subtrahend_filename, output_filename): 
    print 'File with a minuend list of kmers:     ' + minuend_filename
    print 'File with a subtrahend list of kmers:  ' + subtrahend_filename
    print 'Output file:                           ' + output_filename

    with open(minuend_filename, 'r') as left, open(subtrahend_filename, 'r') as right, \
         open(output_filename, 'w') as out: 

        minuend_kmer_number = 1
        print 'Started subtraction.'
        read_left_record = True
        read_right_record = True

        while True:
            if read_left_record:
                left_record = left.readline().rstrip('\n')
                if not left_record:
                    break # EOF is reached
                left_kmer, left_count_str = left_record.split('\t')
                left_count = int(left_count_str)
                minuend_kmer_number += 1
                if minuend_kmer_number % 1000000 == 0:
	            print minuend_kmer_number, 'of kmers from the minuend list are processed.'

            if read_right_record:
                right_record = right.readline().rstrip('\n')
                if not right_record: # no kmers left in the subtrahend list
                    # so, write the remaining part of the minuend list into the output file
                    # using the main loop till the minued list ends
                    out.write(left_record + '\n')
                    read_left_record = True
                    continue
                right_kmer, right_count_str = right_record.split('\t')
                right_count = int(right_count_str)
            
            if left_kmer == right_kmer and left_count != right_count:
                out.write(left_kmer + ' ' + str(left_count - right_count) + '\n')
                read_left_record = True
                read_right_record = True
            elif left_kmer < right_kmer:
                out.write(left_record + '\n')
                read_left_record = True
                read_right_record = False
            elif left_kmer > right_kmer:
                read_left_record = False
                read_right_record = True

        print 'Finished kmers processing.'


if __name__ == '__main__':
    arguments = docopt(__doc__, version='subkmers 0.1')
    minuend_filename = arguments["-i"]
    if not exists(minuend_filename):
        print "Error: Can't find a file with minuend list: no such file '" + \
              minuend_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(minuend_filename):
        print "Error: File with a minuend list be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)        

    subtrahend_filename = arguments["-j"]
    if not exists(subtrahend_filename):
        print "Error: Can't find a file with a subtrahend list: no such file '" + \
              subtrahend_filename + "'. Exit.\n"
        sys.exit(1)
    if not isfile(subtrahend_filename):
        print "Error: File with a subtrahend list be a regular file. " + \
              "Something else given. Exit.\n"
        sys.exit(1)

    output_filename = arguments["-o"].rstrip('/')

    subtract_kmers(minuend_filename, subtrahend_filename, output_filename)

