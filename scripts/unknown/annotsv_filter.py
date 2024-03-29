import argparse
import csv
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', dest="input", help='input AnnotSV tsv file', required=True, action="store")
parser.add_argument('--output', '-o', dest="output", help='output tsv file name', required=True, action="store")
parser.add_argument('--filtering_frequency', dest="filtering_frequency", help="frequency to filter with", action="store", type=float, default="0.05")
parser.add_argument('--all-CDS', dest="CDS", help="Do not require a positive CoDing Sequence overlap", action="store_true")
parser.add_argument('--survivor-merged', dest="survivor", help="survivor merge filtering, drop the last filter step", action="store_true")
parser.add_argument('--ignore-pass-filter', dest="filter", help="Do not require calls to have a PASS filter", action="store_true")

args = parser.parse_args()
input_file_name  = args.input
output_file_name = args.output
filtering_frequency = args.filtering_frequency
all_cds = args.CDS
survivor_merged = args.survivor
ignore_pass_filter = args.filter

with open(input_file_name, 'r') as file_in, open(output_file_name, 'w') as file_out:
    file_in = csv.DictReader(file_in, delimiter='\t')
    file_out = csv.DictWriter(file_out, fieldnames=file_in.fieldnames, delimiter='\t')
    file_out.writeheader()
    total_sv_count = 0
    pass_sv_count = 0
    for row in file_in:
        total_sv_count += 1
        if(row['AnnotSV type'] == 'split' \
            and (row['FILTER'] == 'PASS' or ignore_pass_filter) \
            and (int(row['CDS length']) > 0 or all_cds) \
            and float(row['IMH_AF']) < filtering_frequency
            and float(row['1000g_max_AF']) < filtering_frequency
            and float(row['GD_AF']) < filtering_frequency
            and not(float(row['DGV_LOSS_Frequency']) > filtering_frequency and 'DEL' in row['SV type']) 
            and not(float(row['DGV_GAIN_Frequency']) > filtering_frequency and ('DUP' in row['SV type'] or 'INS' in row['SV type']))
            and (survivor_merged or not(('Manta' in row['ID'] and 'IMPRECISE' in row['INFO']) or (row['QUAL'] != '.' and 'IMPRECISE' in row['INFO']))) ):
            file_out.writerow(row)
            pass_sv_count += 1
    print("total sv count:",total_sv_count)
    print("total sv passed count:",pass_sv_count)
