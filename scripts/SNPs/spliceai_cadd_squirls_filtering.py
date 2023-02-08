import argparse
import csv
import sys
import vcfpy

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    "-i",
    dest="input",
    help="input spliceai, cadd, squirls, and gnomad annotated vcf file",
    required=True,
    action="store",
)
parser.add_argument(
    "--output",
    "-o",
    dest="output",
    help="output tsv file name",
    required=True,
    action="store",
)
parser.add_argument(
    "--spliceai-score",
    dest="spliceai_score",
    help="spliceai score to filter with",
    action="store",
    type=float,
    default="0.5",
)
parser.add_argument(
    "--cadd-score",
    dest="cadd_score",
    help="cadd phred score to filter with",
    action="store",
    type=float,
    default="0",
)
parser.add_argument(
    "--squirls-score",
    dest="squirls_score",
    help="squirls score to filter with",
    action="store",
    type=float,
    default="0.5",
)
parser.add_argument(
    "--gnomad-frequency",
    dest="gnomad_frequency",
    help="gnomad frequency to filter with",
    action="store",
    type=float,
    default="0.05",
)
parser.add_argument(
    "--gnomad",
    dest="gnomad",
    help="gnomad field name",
    action="store",
    default="gnomad_AF",
)

args = parser.parse_args()
input_file_name = args.input
output_file_name = args.output
spliceai_score = args.spliceai_score
cadd_score = args.cadd_score
squirls_score = args.squirls_score
gnomad_frequency = args.gnomad_frequency
gnomad_field = args.gnomad

reader = vcfpy.Reader.from_path(input_file_name)

spliceai_header = [
    "ALLELE",
    "SYMBOL",
    "DS_AG",
    "DS_AL",
    "DS_DG",
    "DS_DL",
    "DP_AG",
    "DP_AL",
    "DP_DG",
    "DP_DL",
]
header = (
    ["CHROM", "POS", "REF", "ALT"]
    + reader.header.samples.names
    + spliceai_header
    + ["max_spliceai_delta", "gnomad_freq"]
    + ["CADD_PHRED"]
    + ["SQUIRLS_ALT", "SQUIRLS_TRANSCRIPTS", "SQUIRLS_SCORES", "MAX_SQUIRLS_SCORE"]
)
with open(output_file_name, "w") as out:
    writer = csv.writer(out, delimiter="\t")
    writer.writerow(header)
    for record in reader:
        spliceai_str = record.INFO.get("SpliceAI") or -1
        spliceai_vals = spliceai_str[0].split("|") if spliceai_str != -1 else ['alt','gene',-1,-1,-1,-1]
        max_delta = max(spliceai_vals[3:6])
        if float(max_delta) < spliceai_score:
            continue

        cadd = record.INFO.get("CADD_PHRED") or -1
        if cadd < cadd_score:
            continue

        gnomad = record.INFO.get(gnomad_field) or [-1]
        gnomad = gnomad[0]
        if gnomad > gnomad_frequency:
            continue

        squirls_str = record.INFO.get("SQUIRLS_SCORE") or [-1]
        if squirls_str[0] != -1:
            squirls_list = squirls_str[0].replace("=", "|").split("|")
            squirls_alt = squirls_list[0]
            squirls_transcripts = "|".join(squirls_list[1::2])
            squirls_scores = "|".join(squirls_list[2::2])
            max_squirls_score = float(max(squirls_list[2::2]))
            if max_squirls_score < squirls_score:
                continue
        else:
            squirls_alt = "NA"
            squirls_transcripts = "NA"
            squirls_scores = "NA"
            max_squirls_score = -1
        line = [record.CHROM, record.POS, record.REF]
        line += [alt.value for alt in record.ALT]
        line += [call.data.get("GT") or "./." for call in record.calls]
        line += spliceai_vals
        line += [max_delta, gnomad]
        line += [cadd]
        line += [squirls_alt, squirls_transcripts, squirls_scores, max_squirls_score]

        writer.writerow(line)
