import argparse
import pysam
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--bam', '-b', dest="bam", help='input aligned bam', required=True, action="store")
parser.add_argument('--out', '-o', dest="output", help='output file name', required=True, action="store")
parser.add_argument('--bq', '-q', dest="qual", help='min base quality for counting', action="store", default=13)
parser.add_argument('--pos', '-p', dest="pos", help='X chr position', action="store", default=12920335)

args = parser.parse_args()
bam_path = args.bam
out_file_name = args.output
min_qual = args.qual
IGV_POSITION = int(args.pos)
bam = pysam.AlignmentFile(bam_path, "rb")


fieldnames = ["READ","BASE","QUAL"]

count = 0
with open(out_file_name, 'w') as tsvfile:
    writer = csv.DictWriter(tsvfile, fieldnames = fieldnames, delimiter = "\t")
    writer.writeheader()
    for pileupcolumn in bam.pileup('chrX', IGV_POSITION-1, IGV_POSITION, truncate=True, max_depth=100000, min_base_quality=min_qual, stepper="nofilter"):
        print(f"coverage at base(0) {pileupcolumn.pos} = { pileupcolumn.n}")
        for pileupread in pileupcolumn.pileups:
            r = {}
            align = pileupread.alignment
            if align.is_supplementary:
                continue
            r["READ"] = align.query_name
            if pileupread.is_del:
                base = "del"
                qual = "-1"
            elif pileupread.indel > 0:
                base = "ins"
                qual = "-1"
            elif pileupread.is_refskip:
                base = "refskip"
                qual = "-1"
            else:
                base = align.query_sequence[pileupread.query_position]
                qual = align.query_qualities[pileupread.query_position]
            r["BASE"] = base
            r["QUAL"] = qual
            count = count + 1
            writer.writerow(r)

bam.close()
#import pdb; pdb.set_trace()
