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

HG38="/storage1/fs1/bga/Active/gmsroot/gc2560/core/model_data/2887491634/build21f22873ebe0486c8e6f69c15435aa96/all_sequences.fa"

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
