## adapted from http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec379 
from Bio import SeqIO
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--fastq', '-f', dest="fastq", help='input decompressed fastq', required=True, action="store")
parser.add_argument('--out', '-o', dest="output", help='output file name', required=True, action="store")
parser.add_argument('--stats', '-s', dest="stats", help='stats file name', required=True, action="store")
parser.add_argument('--TSO', '-t', dest="TSO", help='TSO sequence to query', action="store", default="TTTCTTATATGGG")

args = parser.parse_args()
fastq_path = args.fastq
out_file_name = args.output
stats_file_name = args.stats
TSO_seq = args.TSO

def trim_perfect_adaptors(records, stats, TSO):
    """Trims perfect R1 sequence, extracts CB and MB into query name, removes perfect TSO.
    CB=16 bases, MB=10 bases. 
    R1 - CB - MB - TSO - cDNA_insert - potential 3' primer 
    This is a generator function, the records argument should
    be a list or iterator returning SeqRecord objects.
    """
    fieldnames = ["ID", "read_length", "TSO_index", "CB", "MB"]
    with open(stats, 'w') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames = fieldnames, delimiter = "\t")
        writer.writeheader()
        

        len_TSO = len(TSO)
        len_CB = 16
        len_MB = 10
        CB_MB_exp_len = len_CB + len_MB
        for record in records:
            row = {}
            TSO_index = record.seq.find(TSO)
            row["read_length"] = len(record)
            row["ID"] = record.id
            row["TSO_index"] = TSO_index
            if TSO_index != -1:
                CB_MB_len = CB_MB_exp_len
                if CB_MB_len == CB_MB_exp_len:
                    # trim off the adaptor
                    # extract CB and MB
                    # trim off TSO
                    st = TSO_index - CB_MB_exp_len
                    CB = str(record.seq[TSO_index - len_CB - len_MB : TSO_index - len_MB])
                    MB = str(record.seq[TSO_index - len_MB : TSO_index])
                    row["CB"] = CB
                    row["MB"] = MB
                    record.id = record.id + "-CB:" +  CB + "-MB:" + MB
                    yield record[len_CB + len_MB + len_TSO :]
            writer.writerow(row)


original_reads = SeqIO.parse(fastq_path, "fastq")
trimmed_reads = trim_perfect_adaptors(original_reads, stats_file_name, TSO_seq)

count = SeqIO.write(trimmed_reads, out_file_name, "fastq")

print(f"Saved {count} reads")


