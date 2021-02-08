import argparse
import csv
import sys
import operator
import os

## version 1.0.0
## email: alex.paul@wustl.edu

# ------------------
# ------------------
# start support functions
# ------------------
# ------------------
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
# ------------------
# ------------------
# end support functions
# ------------------
# ------------------

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', dest="input", help='input tsv file', required=True, action="store")
parser.add_argument('--output', '-o', dest="output", help='output tsv file', required=True, action="store")
parser.add_argument('--gnomad_tag_filter', dest="gnomad_filter", help="gnomAD filter tag, to remove 1.00 that bcftools fails to filter out..", required=False, action="store")
parser.add_argument('--proband_filter', dest="proband_filter", help="sample name to filter out hom ref calls", required=False, action="store")
parser.add_argument('--add_zygosity', dest="add_zygosity", help="add zygosity column for each sample", action="store_true")
parser.add_argument('--add_vaf', dest="add_vaf", help="add vaf column for each sample", action="store_true")
parser.add_argument('--pop_max_af_fields', dest="add_pop_max_src", help="comma separated list(no spaces!) of columns to compare to add max population field to result", required=False, action="store")
parser.add_argument('--make_excel', dest="make_excel", help="also make an excel(.xlsx) formatted file", action="store_true")
parser.add_argument('--drop_id', dest="drop_id", help="drop the ID column", action="store_true")
parser.add_argument('move_columns', type=str, nargs='*', help='list of columns to move to front')

args = parser.parse_args()
input_file_name  = args.input
output_file_name = args.output
move_to_front_columns = args.move_columns
gnomad_filter = args.gnomad_filter
add_zygosity = args.add_zygosity
add_vaf = args.add_vaf
proband_sample = args.proband_filter
add_pop_max_src = args.add_pop_max_src
make_excel = args.make_excel
drop_id = args.drop_id

if(add_pop_max_src):
    add_pop_max_src = add_pop_max_src.split(",")

# check if can export excel file:
if make_excel:
    try:
        import xlsxwriter
        print("**INFO** Creating Excel output file")
    except ImportError as e:
        print("**ERROR** unable to export as Excel file, only exporting as TSV")
        print("**INFO** install the `xlsxwriter` package to export as Excel")
        make_excel = False

# check out file extension
file_name, extension = os.path.splitext(output_file_name)
# change to xlsx or tsv depending on the options..
if(not(make_excel) and (extension != ".tsv")):
    print("**INFO** output file name not tsv extension, changing to: " + file_name + ".tsv")
    tsv_output_file_name = file_name + ".tsv"
elif(make_excel):
    print("**INFO** tsv output file name: " + file_name + ".tsv")
    print("**INFO** Excel output file name: " + file_name + ".xlsx")
    excel_output_file_name = file_name + ".xlsx"
    tsv_output_file_name = file_name + ".tsv"
else:
    tsv_output_file_name = output_file_name

# get new order:
file_in = open(input_file_name, 'r')
file_in_check = csv.DictReader(file_in, delimiter='\t')
in_column_names = file_in_check.fieldnames
start_index = in_column_names.index("ALT") + 1
out_column_names = in_column_names
insert_index = start_index
for item in move_to_front_columns:
    if item in in_column_names:
        item_index = in_column_names.index(item)
        out_column_names = move_column(insert_index, out_column_names, item_index)
        insert_index = insert_index + 1
    else:
        print("**ERROR**   " + item + " not found in the input TSV file. Unable to move.")
file_in.close()

if(drop_id):
    out_column_names.remove('ID')

# get samples..
samples = []
for item in out_column_names:
    if item.endswith(".GT"):
        samples.append(item[:-3])
if(add_zygosity):
     for sample in samples:
        out_column_names.append(sample +".zygosity")
if(add_vaf):
    for sample in samples:
        out_column_names.append(sample +".vaf")
if(add_pop_max_src):
    out_column_names.append("db_pop_freq_max")
    out_column_names.append("db_pop_freq_max_AF")


# reorder actual rows
with open(input_file_name, 'r') as file_in, open(tsv_output_file_name, 'w') as file_out:
    writer = csv.DictWriter(file_out, fieldnames=out_column_names,  delimiter='\t', dialect='excel')
    # reorder the header first
    writer.writeheader()
    for row in csv.DictReader(file_in, delimiter='\t'):
        # check if gnomad should be filtered and what tag..
        skip_row = False
        # previous filtering tool passes gnomad freq of 1.0, this step removes those calls
        if(gnomad_filter):
            gnomad_value = row[gnomad_filter]
            if(gnomad_value == ''):
                continue
            try:
                gnomad_value = float(gnomad_value)
                if(gnomad_value == 1):
                    skip_row = True
                    continue
            except ValueError:
                if(row[gnomad_filter] == "1.00000e+00"):
                  skip_row = True
                  continue
        if(add_zygosity):
            reference = row["REF"]
            alternate = row["ALT"]
            for sample in samples:
                sample_gt = row[sample + ".GT"].split("/")
                gt_1 = sample_gt[0]
                gt_2 = sample_gt[1]
                if((gt_1 == reference) and (gt_2 == reference)):
                    if(sample == proband_sample):
                        # filter out hom ref variants
                        skip_row = True
                        break
                    row[sample + ".zygosity"] = "Hom Ref"
                elif((gt_1 == alternate) and (gt_2 == alternate)):
                    row[sample + ".zygosity"] = "Hom Alt"
                elif((gt_1 == reference) or (gt_2 == reference)):
                    row[sample + ".zygosity"] = "Het"
                elif((sample == proband_sample) and (gt_1 == reference) and (gt_2 == reference)):
                    # filter out no call proband variants
                    skip_row = True
                    break
                elif(sample == proband_sample):
                    # skip if no call
                    skip_row = True
                    break
                else:
                    row[sample + ".zygosity"] = "."
        if(add_vaf):
            for sample in samples:
                allele_depth = row[sample + ".AD"].split(",")
                reference = int(allele_depth[0])
                alternate = int(allele_depth[1])
                if (reference+alternate) == 0:
                    row[sample + ".vaf"] = '.'
                else:
                    row[sample + ".vaf"] = alternate /(alternate + reference)
        if(add_pop_max_src):
            dbs = {}
            for db in add_pop_max_src:
                dbs[db] = row[db]
            max_db = max(dbs.items(), key=operator.itemgetter(1))[0]
            if(row[max_db]):
                row["db_pop_freq_max"] = max_db
                row["db_pop_freq_max_AF"] = row[max_db]
            else:
                row["db_pop_freq_max"] = ""
                row["db_pop_freq_max_AF"] = ""

        # writes the reordered rows to the new file
        if(not(skip_row)):
            if(drop_id):
                row.pop('ID')
            #maybe switch to a while loop???
            writer.writerow(row)
        skip_row = False
    file_out.close()
    file_in.close()

# write as excel file
# check if need to write as excel file..
# and how to do that.
if(make_excel):
    # read in tsv
    # output using the xlsx package..
    workbook = xlsxwriter.Workbook(excel_output_file_name)
    worksheet = workbook.add_worksheet()
    row_number = 0
    with open(output_file_name, 'r') as file_out:
        for row in csv.reader(file_out, delimiter='\t'):
            new_row = []
            for element in row:
                try:
                    new_row.append(float(element))
                except ValueError:
                    new_row.append(element)
            worksheet.write_row(row_number, 0, new_row)
            row_number += 1
    workbook.close()
