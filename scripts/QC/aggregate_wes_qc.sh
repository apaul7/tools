#!/bin/bash
set -eou pipefail

USAGE="/bin/bash $0 \$OUT_FILE DATA_DIR1 DATA_DIR2 DATA_DIR3 ..."
OUT_FILE=$1
shift
if [ -d "$OUT_FILE" ]; then
  printf "### ERROR. First input is a directory\nUSAGE: "
  echo "$USAGE"
  exit 1
fi

GOOD_HEADER="BAIT_SET	TOTAL_READS	PCT_PF_UQ_READS	PF_UQ_READS_ALIGNED	PCT_PF_UQ_READS_ALIGNED	MEAN_TARGET_COVERAGE	MAX_TARGET_COVERAGE	ZERO_CVG_TARGETS_PCT	PCT_TARGET_BASES_10X	PCT_TARGET_BASES_30X	PCT_TARGET_BASES_50X"
printf "SAMPLE\tBUILD_ID\t$GOOD_HEADER\n" > $OUT_FILE

for BUILD in "$@"; do
  echo "## working on $BUILD"
  BUILD_ID=`echo $BUILD | sed 's|.*/build||'`
  QC_FILES=`find $BUILD/results/alignment_pipeline/ | grep "final.roi-HsMetrics.txt$" | sort`
  for QC in $QC_FILES; do
    SAMPLE=`echo $QC | sed 's|.*alignment_pipeline/||' | sed 's|-qc/final.roi-HsMetrics.txt||'`
    echo "### working on $SAMPLE"
    SAMPLE_HEADER=`head -7 $QC | tail -1 | awk '{OFS="\t"; print $1,$6,$10,$11,$12,$23,$25,$29,$38,$40,$42}'`
    if [ "$SAMPLE_HEADER" != "$GOOD_HEADER" ]; then
        printf "### ERROR headers mismatch, HsMetrics file has:\n$SAMPLE_HEADER\nexpected:\n$GOOD_HEADER"
        exit 1
    fi
    SAMPLE_DATA=`head -8 $QC | tail -1 | awk '{OFS="\t"; print $1,$6,$10,$11,$12,$23,$25,$29,$38,$40,$42}'`
    printf "$SAMPLE\t$BUILD_ID\t$SAMPLE_DATA\n" >> $OUT_FILE
  done
done
