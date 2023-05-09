import argparse
import csv
import sys

def move_header_column(new_index, list, column_name):
    old_index = list.index(column_name)
    list = move_column(new_index, list, old_index)
    delta = (new_index, old_index)
    return list,delta
def move_column(new_index, list, old_index):
    move_value = list.pop(old_index)
    list.insert(new_index, move_value)
    delta = (new_index, old_index)
    return list

parser = argparse.ArgumentParser()
parser.add_argument('--indel', '-i', dest="indel", help='input rare indel annovar file', required=True, action="store")
parser.add_argument('--annovar', '-a', dest="annovar", help='input annovar file', required=True, action="store")
parser.add_argument('--out', '-o', dest="output", help='output file name', required=True, action="store")

args = parser.parse_args()
indel_file_name = args.indel
annovar_file_name = args.annovar
out_file_name = args.output

# get new order:
indel_in = open(indel_file_name, 'r')
indel_in_reader = csv.DictReader(indel_in, delimiter='\t')
annovar_in = open(annovar_file_name, 'r')
annovar_in_reader = csv.DictReader(annovar_in, delimiter='\t')


# loop through rare indel file, make dictionary
rare_indels = {}
for row in indel_in_reader:
    key = row["Chr"] + row["Start"] + row["End"] + row["Ref"] + row["Alt"] + row["Otherinfo11"]
    row["ExonicFunc.refGene"] = "rare indel"
    rare_indels[key] = row
    
final_out = open(out_file_name, 'w')
final_out_writer = csv.DictWriter(final_out,annovar_in_reader.fieldnames, delimiter="\t")
final_out_writer.writeheader()
# loop through annovar file, if match dictionary, append rare indel
for row in annovar_in_reader:
    key = row["Chr"] + row["Start"] + row["End"] + row["Ref"] + row["Alt"] + row["Otherinfo11"]
    if key in rare_indels.keys():
        rare_indels.pop(key)
        if row["ExonicFunc.refGene"] == ".":
            row["ExonicFunc.refGene"] = "rare indel"
        else:
            row["ExonicFunc.refGene"] = row["ExonicFunc.refGene"] + ";rare indel"
    try:
        final_out_writer.writerow(row)
    except Exception as exc:
        exc.args += (row,)
        raise
    #final_out_writer.writerow(row)
for row in rare_indels.values():
    print(row)
    final_out_writer.writerow(row)
