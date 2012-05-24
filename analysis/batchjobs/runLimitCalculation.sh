 #!/bin/sh

## Check arguments
if [ $# -lt 1 ] ; then
   echo "Usage: runSusyLimitBatch.sh [-d] [-m <mode>] [-p <setupDir>] [-g <point>] [-w <workspaceDir>] [-r <resultsDir>] [-n <nToys>] [-c <calculatorType>] [-j <jobId>] <logfile> " $#
   exit 1
fi

## Intercept dryrun option if given
DRYRUN=0
if [ "$1" = "-d" ] ; then
  DRYRUN=1
  shift
fi

MODE=""
if [ "$1" = "-m" ]; then
  MODE=$2
  shift 2
fi

## SusyFitter dir
SUSYDIR="/afs/cern.ch/atlas/groups/susy/1lepton/SusyFitter"
if [ "$1" = "-p" ] ; then
  SUSYDIR=$2
  shift 2
fi

ARGS=""
if [ "$1" = "-g" ]; then
  ARGS=$2
  shift 2
fi

WSIN=""
if [ "$1" = "-w" ]; then
  WSIN=$2
  shift 2
fi

ROUT=""
if [ "$1" = "-r" ]; then
  ROUT=$2
  shift 2
fi

NTOYS=""
if [ "$1" = "-n" ]; then
  NTOYS=$2
  shift 2
fi

CTYPE=""
if [ "$1" = "-c" ]; then
  CTYPE=$2
  shift 2
fi

JOBID=""
if [ "$1" = "-j" ]; then
  JOBID=$2
  shift 2
fi


LOGFILE=$1
#rm -f ${LOGFILE} ${LOGFILE}.gz
shift 1


## setup path
echo $PWD
XCWD=$PWD
cd $SUSYDIR
source setup.sh
cd $XCWD

echo "current directory:"
pwd


if [ ! -e "results/" ]
then
        mkdir -v results
	cp ${WSIN}/*${ARGS}*_model.root results/.
fi

if [ ! -e "data/" ]
then
        mkdir -v data
fi

if [ ! -e "config/" ]
then
        mkdir -v config
	cp /afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_000208/config/HistFactorySchema.dtd config/.
fi

echo "directory contains:"
#ls -lh

#mkdir -p -v /afs/cern.ch/user/j/jlorenz/scratch0/susyresults/$ARGS_hypotestresult 2>&1


RUNCMD="python $SUSYDIR/scripts/HypoTest.py -s 5 -${MODE} -g ${ARGS} -n ${NTOYS} -c ${CTYPE}"

echo
echo ">> Now running command:"
echo ">> ===================="
echo "$RUNCMD"
echo 

if [ $DRYRUN -ne 1 ]; then
  $RUNCMD 
  # 2>&1 | tee $LOGFILE
  #gzip $LOGFILE
fi

#echo '_file0->ls(); gSystem->Exit(0);' | root -b data/MyOneLeptonKtScaleFitR17.root




OUTNAME=$(ls -1 results | grep "hypotest.root")


OUTNAME=${OUTNAME/hypotest/hypotest_${JOBID}}

cp results/*hypotest.root  $ROUT"/"$OUTNAME
cp results/*upperlimit.root  $ROUT"/"$OUTNAME

cp results/*.eps  $ROUT
cp *.eps  $ROUT

echo
echo ">> Finished command:"
echo ">> ================="
echo "$RUNCMD"
echo

#if [ $DRYRUN -ne 1 ]; then
#  echo ">> logfile stored as:"
#  echo ">> ===================="
#  echo "${LOGFILE}.gz"
#  echo
#fi
