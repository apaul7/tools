#!/bin/bash
set -eou pipefail

USAGE="script.sh vcf"
if [ "$#" -ne 1 ]; then
    echo "Error in inputs"
    echo "USAGE: $USAGE"
    exit 1
fi
VCF="$1"

FINAL_PREFIX="${VCF}_AnnoOut"
HG38="/storage1/fs1/bga/Active/gmsroot/gc2560/core/model_data/2887491634/build21f22873ebe0486c8e6f69c15435aa96/all_sequences.fa"
ANNOVAR_HOME="/storage1/fs1/fcole/Active/annotations/annovar/annovar/"
OMIM_XREF="/storage1/fs1/fcole/Active/annotations/omim/20230221/gene_xref.annovar.txt"


${ANNOVAR_HOME}/convert2annovar.pl \
  -format vcf4 \
  ${VCF} \
  -outfile anno.avinput \
  --includeinfo

mkdir humandb
ln -s ${ANNOVAR_HOME}/humandb/*.txt ./humandb
ln -s ${ANNOVAR_HOME}/humandb/*.txt.idx ./humandb
ln -s ${ANNOVAR_HOME}/humandb/*.fa ./humandb


echo "***00*** Running variants_reduction.pl"
${ANNOVAR_HOME}/variants_reduction.pl \
  anno.avinput ./humandb \
  --buildver hg38 \
  --protocol gnomad211_exome,gnomad312_genome \
  --operation f,f \
  --aaf_threshold 0.01 \
  --remove \
  --outfile anno.reduced.avinput

echo "***06*** Running table_annovar.pl"
${ANNOVAR_HOME}/table_annovar.pl \
  anno.reduced.avinput.step2.varlist ./humandb/ \
  --buildVer hg38 \
  --out $FINAL_PREFIX \
  --remove \
  --protocol refGene,genomicSuperDups,1000g2015aug_all,gnomad211_exome,gnomad312_genome,gme,dbnsfp42a,dbscsnv11,clinvar_20230218,gene4denovo201907,varity \
  --operation gx,r,f,f,f,f,f,f,f,f,f \
  --nastring . \
  --otherinfo \
  --polish \
  -xref $OMIM_XREF


