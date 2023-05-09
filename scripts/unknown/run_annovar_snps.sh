#!/bin/bash
set -eou pipefail

USAGE="script.sh family_name WES/WGS input_vcf"
if [ "$#" -ne 3 ]; then
    echo "Error in inputs"
    echo "USAGE: $USAGE"
    exit 1
fi
FAMILY="$1"
DATA_TYPE="$2"
IN_VCF="$3"
RUN_DATE=`date +%b%Y`
FINAL_PREFIX="${FAMILY}_${DATA_TYPE}_${RUN_DATE}_AnnoOut"
echo "*** Running $FAMILY"

HG38="/storage1/fs1/bga/Active/gmsroot/gc2560/core/model_data/2887491634/build21f22873ebe0486c8e6f69c15435aa96/all_sequences.fa"
ANNOVAR_HOME="/storage1/fs1/fcole/Active/annotations/annovar/annovar/"
OMIM_XREF="/storage1/fs1/fcole/Active/annotations/omim/20230221/gene_xref.annovar.txt"

echo "***01*** Running normalize step"
bcftools norm \
  -m-both \
  -o tmp.vcf \
  $IN_VCF
bcftools norm \
  tmp.vcf  \
  -o av.vcf \
  --fasta-ref $HG38
rm tmp.vcf

echo "***02*** Running make annovar input and split"
${ANNOVAR_HOME}/convert2annovar.pl \
  -format vcf4 \
  av.vcf \
  -outfile sample \
  --includeinfo \
  -allsample

echo "***03*** Running add sample tag, merge, concat, sort"
#SAMPLES=`ls -l  sample*avinput | awk '{print $9}' | sort| sed 's/sample.//g' | sed 's/.avinput//g' | tr '\n' ' '`
SAMPLES=`ls | tr ' ' '\n' | grep sample | sed 's/sample.//g' | sed 's/.avinput//g' | tr '\n' ' '`
for SAMPLE in $SAMPLES; do
  echo "### working on $SAMPLE"
  awk -v s=$SAMPLE '{print $0"\t"s}' sample.$SAMPLE.avinput > sample.$SAMPLE.avinput.tag
done
cat ./sample.*.avinput.tag > all_sample.tag.avinput
bedtools sort -chrThenSizeA -i all_sample.tag.avinput > all_sample.tag.sorted.avinput

echo "***04*** Running setup humandb, add CADD scores, add spliceai and squirls to avinput"
mkdir humandb
ln -s ${ANNOVAR_HOME}/humandb/*.txt ./humandb
ln -s ${ANNOVAR_HOME}/humandb/*.txt.idx ./humandb
ln -s ${ANNOVAR_HOME}/humandb/*.fa ./humandb

# need to move cadd_phred to col 5
# format:
# chr start stop ref alt score other
# for indels need to use "-" as ref or alt.
# chr2    8778635 T       TACGAAGAGGG     0.817388        9.566
# becomes
# chr2    8778635 8778635        -       ACGAAGAGGG     9.566        9.566
#zgrep -v "^#" $FAMILY.CADDv1.6.tsv.gz | awk -F"\t" '{OFS="\t"; $2=$2"\t"$2-1+length($3); $5=$6; print $0}' > hg38_CADDv1.6.txt
zgrep -v "^#" $FAMILY.CADDv1.6.tsv.gz | \
    awk -F"\t" '{OFS="\t";
$5=$6;
if(length($3)<length($4) && substr($4,1,1)==substr($3,1,1)){
  $3="-";
  $4=substr($4,2)};
if(length($3)>length($4) && substr($4,1,1)==substr($3,1,1)){
  $2=$2+1;
  $3=substr($3,2);
  $4="-"};
$2=$2"\t"$2-1+length($3);
print $0}' > hg38_CADDv1.6.txt

#zgrep -v "^#" $FAMILY.CADDv1.6.tsv.gz | awk -F"\t" '{OFS="\t"; print $0}' > hg38_CADDv1.6.txt

${ANNOVAR_HOME}/index_annovar.pl --filetype A --outfile humandb/hg38_CADDv1.6.txt hg38_CADDv1.6.txt

python3 ~/bga/scripts/annovar_parse_out_spliceai_squirls_scores.py \
  --input all_sample.tag.sorted.avinput \
  --output all_sample.tag.sorted.splice_scores.avinput

echo "***05*** Running variants_reduction.pl"
${ANNOVAR_HOME}/variants_reduction.pl \
  all_sample.tag.sorted.splice_scores.avinput ./humandb \
  --buildver hg38 \
  --protocol gnomad211_exome,gnomad312_genome \
  --operation f,f \
  --aaf_threshold 0.01 \
  --remove \
  --outfile all_sample.tag.sorted.splice_scores.reduced.avinput

echo "***06*** Running table_annovar.pl"
${ANNOVAR_HOME}/table_annovar.pl \
  all_sample.tag.sorted.splice_scores.reduced.avinput.step2.varlist ./humandb/ \
  --buildVer hg38 \
  --out $FINAL_PREFIX \
  --remove \
  --protocol refGene,genomicSuperDups,1000g2015aug_all,gnomad211_exome,gnomad312_genome,gme,dbnsfp42a,dbscsnv11,clinvar_20230218,gene4denovo201907,varity,CADDv1.6 \
  --operation gx,r,f,f,f,f,f,f,f,f,f,f \
  --nastring . \
  --otherinfo \
  --polish \
  -xref $OMIM_XREF

