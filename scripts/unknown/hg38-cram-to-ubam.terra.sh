#!/bin/bash
set -eou pipefail

USAGE="script.sh family_directory sample_name"
if [ "$#" -ne 2 ]; then
    echo "Error in inputs"
    echo "USAGE: $USAGE"
    exit 1
fi
FAMILY_DIRECTORY="$1"
SAMPLE="$2"
echo "running $SAMPLE"

HG38="/scratch1/fs1/fcole/work/Homo_sapiens_assembly38.fasta"

cd $FAMILY_DIRECTORY
# cram -> bam
samtools view -b \
-T $HG38 \
-o bam/$SAMPLE.bam \
cram/$SAMPLE.cram

mkdir -p tmp
# bam -> ubam
/usr/bin/java -Xmx18G -Djava.io.tmpdir=./tmp -jar /opt/jars/picard.jar RevertSam \
    SANITIZE=true \
    MAX_DISCARD_FRACTION=0.005 \
    ATTRIBUTE_TO_CLEAR=XT \
    ATTRIBUTE_TO_CLEAR=XN \
    ATTRIBUTE_TO_CLEAR=AS \
    ATTRIBUTE_TO_CLEAR=OC \
    ATTRIBUTE_TO_CLEAR=OP \
    SORT_ORDER=queryname \
    RESTORE_ORIGINAL_QUALITIES=true \
    REMOVE_DUPLICATE_INFORMATION=true \
    REMOVE_ALIGNMENT_INFORMATION=true \
    I=bam/$SAMPLE.bam \
    O=ubam/$SAMPLE.unaligned.bam
