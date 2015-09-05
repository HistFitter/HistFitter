# setup ROOT
# check Root environment setup. Allow for external setup script.

export BUILD="x86_64-slc6-gcc49-opt"
export ROOTVERSION="6.04.00"
#export CERNPREFIX="/afs/cern.ch/"
export HF_CERNPREFIX="cvmfs/atlas.cern.ch/repo"
export PYTHONVERSION="2.7.3"
export GCCVERSION="4.9"

# check Root environment setup 
if [ ! $ROOTSYS ]; then
  echo "Warning: No valid Root environment (ROOTSYS) defined. Please do so first!"
  return
fi

if [ ! $LD_LIBRARY_PATH ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi

# setup HistFitter package
#if [ "x${BASH_ARGV[0]}" == "x" ]; then
if [ "$(dirname ${BASH_ARGV[0]})" == "." ]; then
  if [ ! -f setup.sh ]; then
    echo ERROR: must "cd where/HistFitter/is" before calling "source setup.sh" for this version of bash!
    HF=; export HF
    return 1
  fi
  HF=$(pwd); export HF
else
  # get param to "."
  thishistfitter=$(dirname ${BASH_ARGV[0]})
  HF=${thishistfitter}; export HF
fi
HISTFITTER=$HF; export HISTFITTER
SUSYFITTER=$HF; export SUSYFITTER # for backwards compatibility

# put root & python stuff into PATH, LD_LIBRARY_PATH
export PATH=$HISTFITTER/bin:$HISTFITTER/scripts:${PATH}
export LD_LIBRARY_PATH=$HISTFITTER/lib:${LD_LIBRARY_PATH}
# PYTHONPATH contains all directories that are used for 'import bla' commands
export PYTHONPATH=$HISTFITTER/python:$HISTFITTER/scripts:$HISTFITTER/macros:$HISTFITTER/lib:$PYTHONPATH
export ROOT_INCLUDE_PATH=$HISTFITTER/include:${ROOT_INCLUDE_PATH}

# set SVN path to defaults
export SVNTEST="svn+ssh://svn.cern.ch/reps/atlastest"
export SVNROOT="svn+ssh://svn.cern.ch/reps/atlasoff"
export SVNPHYS="svn+ssh://svn.cern.ch/reps/atlasphys"

# Hack for ssh from mac 
export LC_ALL=C 

