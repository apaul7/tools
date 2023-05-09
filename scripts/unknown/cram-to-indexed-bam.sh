#!/bin/bash
set -eou pipefail

CRAM=$1

REF="/storage1/fs1/bga/Active/gmsroot/gc2560/core/model_data/2887491634/build21f22873ebe0486c8e6f69c15435aa96/all_sequences.fa"
BASE="${CRAM%.cram}"

samtools view -b \
-T $REF \
-o $BASE.bam \
$CRAM

samtools index $BASE.bam

ln -s $BASE.bam.bai $BASE.bai

