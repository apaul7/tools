import argparse
import csv
import sys
import vcfpy

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', dest="input", help='input spliceai and gnomad annotated vcf file', required=True, action="store")
parser.add_argument('--output', '-o', dest="output", help='output tsv file name', required=True, action="store")
parser.add_argument('--spliceai-frequency', dest="spliceai_frequency", help="spliceai frequency to filter with", action="store", type=float, default="0.50")
parser.add_argument('--gnomad-frequency', dest="gnomad_frequency", help="gnomad frequency to filter with", action="store", type=float, default="0.05")
parser.add_argument('--gnomad', dest="gnomad", help="gnomad field name", action="store", default="gnomad_AF")

args = parser.parse_args()
input_file_name  = args.input
output_file_name = args.output
spliceai_frequency = args.spliceai_frequency
gnomad_frequency = args.gnomad_frequency
gnomad_field = args.gnomad

reader = vcfpy.Reader.from_path(input_file_name)

spliceai_header = ['ALLELE', 'SYMBOL', 'DS_AG', 'DS_AL', 'DS_DG', 'DS_DL', 'DP_AG', 'DP_AL', 'DP_DG', 'DP_DL']
header = ['CHROM', 'POS', 'REF', 'ALT'] + reader.header.samples.names + spliceai_header + ['max_delta', 'gnomad_freq']
#print('\t'.join(header))
with open(output_file_name, 'w') as out:
    writer = csv.writer(out, delimiter='\t')
    writer.writerow(header)
    for record in reader:
        spliceai_str = record.INFO.get('SpliceAI') or "NA"
        if spliceai_str == "NA":
            continue
        gnomad = record.INFO.get(gnomad_field) or [0]
        gnomad = gnomad[0]
        #print(gnomad_frequency) 
        if gnomad > gnomad_frequency:
            continue
        spliceai_vals = spliceai_str[0].split("|")
        max_delta = max(spliceai_vals[3:6])
        if float(max_delta) < spliceai_frequency:
            continue
        line = [record.CHROM, record.POS, record.REF]
        line += [alt.value for alt in record.ALT]
        line += [call.data.get('GT') or './.' for call in record.calls]
        line += spliceai_vals
        line += [max_delta, gnomad]
        writer.writerow(line)

