#!/bin/bash
set -eou pipefail

USAGE="/bin/bash $0 \$IN_QC_FILE \$OUT_FILE DATA_DIR1 DATA_DIR2 DATA_DIR3 ..."
IN_QC_FILE=$1
shift
if [ -d "$IN_QC_FILE" ]; then
  printf "### ERROR. First input is a directory\nUSAGE: "
  echo "$USAGE"
  exit 1
fi
OUT_FILE=$1
shift
if [ -d "$OUT_FILE" ]; then
  printf "### ERROR. First input is a directory\nUSAGE: "
  echo "$USAGE"
  exit 1
fi

#printf "SAMPLE\tBUILD_ID\t$GOOD_HEADER\n" > $OUT_FILE
FIRST_FILE="true"
for BUILD in "$@"; do
  echo "## working on $BUILD"
  BUILD_ID=`echo $BUILD | sed 's|.*/build||'`
  QC_FILES=`find $BUILD/results/alignment_pipeline/ | grep "$IN_QC_FILE" | sort`
  for QC in $QC_FILES; do
    FILE_NAME=`basename $QC`
    if [[ ${FILE_NAME:0:1} == "." ]]; then
        continue
    fi
    SAMPLE=`echo $QC | sed 's|.*alignment_pipeline/||' | sed 's|-qc/.*||'`
    echo "### working on $SAMPLE"
    SAMPLE_HEADER=`head -7 $QC | tail -1`
    if [[ $FIRST_FILE == "true" ]]; then
      FIRST_FILE="false"
      printf "SAMPLE\tBUILD_ID\t$SAMPLE_HEADER\n" > $OUT_FILE
    fi
    SAMPLE_DATA=`head -8 $QC | tail -1`
    printf "$SAMPLE\t$BUILD_ID\t$SAMPLE_DATA\n" >> $OUT_FILE
  done
done
