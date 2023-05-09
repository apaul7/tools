## adapted from http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec379 
from Bio import SeqIO
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--fastq', '-f', dest="fastq", help='input decompressed fastq', required=True, action="store")
parser.add_argument('--out', '-o', dest="output", help='output file name', required=True, action="store")
parser.add_argument('--stats', '-s', dest="stats", help='stats file name', required=True, action="store")
parser.add_argument('--trimmed', dest="trimmed", help='trimmed seq file name', required=True, action="store")
parser.add_argument('--R1', '-r', dest="R1", help='R1 sequence to query', action="store", default="CTACACGACGCTCTTCCGATCT")
parser.add_argument('--TSO', '-t', dest="TSO", help='TSO sequence to query', action="store", default="TTTCTTATATGGG")

args = parser.parse_args()
fastq_path = args.fastq
out_file_name = args.output
trimmed_file_name = args.trimmed
stats_file_name = args.stats
R1_seq = args.R1
TSO_seq = args.TSO

def trim_perfect_adaptors(records, stats, trimmed_bases, R1, TSO):
    """Trims perfect R1 sequence, extracts CB and MB into query name, removes perfect TSO.
    CB=16 bases, MB=10 bases. 
    R1 - CB - MB - TSO - cDNA_insert - potential 3' primer 
    This is a generator function, the records argument should
    be a list or iterator returning SeqRecord objects.
    """
    fieldnames = ["ID", "read_length", "R1_index", "TSO_index", "CB", "MB"]
    with open(stats, 'w') as tsvfile, open(trimmed_bases, 'w') as trimfile, open("reverse-" + trimmed_bases, 'w') as r_trimfile:
        writer = csv.DictWriter(tsvfile, fieldnames = fieldnames, delimiter = "\t")
        writer.writeheader()
        

        len_R1 = len(R1)
        len_TSO = len(TSO)
        len_CB = 16
        len_MB = 10
        CB_MB_exp_len = len_CB + len_MB
        for record in records:
            row = {}
            R1_index = record.seq.find(R1)
            TSO_index = record.seq.find(TSO)
            row["read_length"] = len(record)
            row["ID"] = record.id
            row["R1_index"] = R1_index
            row["TSO_index"] = TSO_index
            if R1_index != -1 and TSO_index != -1:
                CB_MB_len = TSO_index - (len(R1) + R1_index)
                if CB_MB_len == CB_MB_exp_len:
                    # trim off the adaptor
                    # extract CB and MB
                    # trim off TSO
                    CB = str(record.seq[R1_index + len_R1 : R1_index + len_R1 + len_CB])
                    MB = str(record.seq[R1_index + len_R1 + len_CB : R1_index + len_R1 + len_CB + len_MB])
                    row["CB"] = CB
                    row["MB"] = MB
                    record.id = record.id + "-CB:" +  CB + "-MB:" + MB
                    trimmmed_seq = str(record.seq[:R1_index])
                    trimfile.write(">" + record.id + "\n")
                    r_trimfile.write(">" + record.id + "\n")
                    trimfile.write(trimmmed_seq + "\n")
                    r_trimfile.write(trimmmed_seq[::-1] + "\n")
                    yield record[R1_index + len_R1 + len_CB + len_MB + len_TSO :]
            writer.writerow(row)


original_reads = SeqIO.parse(fastq_path, "fastq")
trimmed_reads = trim_perfect_adaptors(original_reads, stats_file_name, trimmed_file_name, R1_seq, TSO_seq)

count = SeqIO.write(trimmed_reads, out_file_name, "fastq")

print(f"Saved {count} reads")


