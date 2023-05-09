#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--bed",
    dest="bed",
    help="bed file to convert to 1 base per line",
    required=True,
    action="store",
)
parser.add_argument(
    "--output",
    dest="output",
    help="output filename",
    required=False,
    action="store",
    default="merged.bed",
)
args = parser.parse_args()

in_file = args.bed
out_file = args.output

with open(out_file, "w") as out, open(in_file, "r") as bed_file:
    for line in bed_file.readlines():
        line = line.strip()
        (chr, start, stop, cov) = line.split("\t")
        for i in range(int(start), int(stop)):
            out.write(chr + "\t" + str(i) + "\t" + str(i + 1) + "\t" + cov + "\n")
