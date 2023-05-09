#!/bin/bash
set -eou pipefail

FAMILY_DIRECTORY="$1"
SAMPLE="$2"
echo "running $SAMPLE"

cd $FAMILY_DIRECTORY

# bam -> ubam
mkdir -p tmp
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
