import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', dest="input", help='input annovar tsv file', required=True, action="store")
parser.add_argument('--output', '-o', dest="output", help='output annovar file name', required=True, action="store")


args = parser.parse_args()
input_file_name  = args.input
output_file_name = args.output

with open(input_file_name, 'r') as file_in, open(output_file_name, 'w') as file_out:
    file_in = csv.reader(file_in, delimiter='\t')
    file_out = csv.writer(file_out, delimiter='\t')
    for row in file_in:
        INFO=row[12]
        d = dict(x.split("=", 1) for x in INFO.split(";"))
        if "SpliceAI" in d:
            s = d["SpliceAI"].split("|")
            #"ALLELE,SYMBOL,DS_AG,DS_AL,DS_DG,DS_DL,DP_AG,DP_AL,DP_DG,DP_DL"
            max_DS_AG = max(s[2::10])
            max_DS_AL = max(s[3::10])
            max_DS_DG = max(s[4::10])
            max_DS_DL = max(s[5::10])
        else:
            max_DS_AG = "."
            max_DS_AL = "."
            max_DS_DG = "."
            max_DS_DL = "."
        if "SQUIRLS_SCORE" in d:
            # ALT|transcript1=score1|transcript2=score2....
            s = d["SQUIRLS_SCORE"].replace("=","|").split("|")
            max_SQUIRLS = max(s[2::2])
        else:
            max_SQUIRLS = "."
        new_row = row + [max_DS_AG, max_DS_AL, max_DS_DG, max_DS_DL, max_SQUIRLS]
        file_out.writerow(new_row)

