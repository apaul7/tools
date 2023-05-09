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
GOOD_HEADER="GENOME_TERRITORY	MEAN_COVERAGE	SD_COVERAGE	MEDIAN_COVERAGE	MAD_COVERAGE	PCT_EXC_MAPQ	PCT_EXC_DUPE	PCT_EXC_UNPAIRED	PCT_EXC_BASEQ	PCT_EXC_OVERLAP	PCT_EXC_CAPPED	PCT_EXC_TOTAL	PCT_1X	PCT_5X	PCT_10X	PCT_15X	PCT_20X	PCT_25X	PCT_30X	PCT_40X	PCT_50X	PCT_60X	PCT_70X	PCT_80X	PCT_90X	PCT_100X	HET_SNP_SENSITIVITY	HET_SNP_Q"
printf "SAMPLE\tBUILD_ID\t$GOOD_HEADER\n" > $OUT_FILE

for BUILD in "$@"; do
  echo "## working on $BUILD"
  BUILD_ID=`echo $BUILD | sed 's|.*/build||'`
  QC_FILES=`find $BUILD/results/alignment_pipeline/ | grep "WgsMetrics.txt$" | sort`
  echo $QC_FILES
  for QC in $QC_FILES; do
    FILE_NAME=`basename $QC`
    if [[ ${FILE_NAME:0:1} == "." ]]; then
        continue
    fi
    SAMPLE=`echo $QC | sed 's|.*alignment_pipeline/||' | sed 's|-qc/.*WgsMetrics.txt||'`
    echo "### working on $SAMPLE"
    SAMPLE_HEADER=`head -7 $QC | tail -1`
    if [ "$SAMPLE_HEADER" != "$GOOD_HEADER" ]; then
        printf "### ERROR headers mismatch, file has:\n$SAMPLE_HEADER\nexpected:\n$GOOD_HEADER\n"
        exit 1
    fi
    SAMPLE_DATA=`head -8 $QC | tail -1`
    printf "$SAMPLE\t$BUILD_ID\t$SAMPLE_DATA\n" >> $OUT_FILE
  done
done
