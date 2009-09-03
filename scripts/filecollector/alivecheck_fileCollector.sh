#! /bin/sh

WorkDir=$(dirname $0)
YourEmail=lilopera@cern.ch
source $WorkDir/env.sh
if [[ $1 == "" ]]
then
  echo No config file specifyed
  exit
fi
if [[ $(dirname $1) == "." ]]
then
  CFGFILE=$WorkDir/$1
else
  CFGFILE=$1
fi
#set ROOT environment
#export ROOTSYS=/nfshome0/cmssw2/slc4_ia32_gcc345/lcg/root/5.18.00a-cms11/
#export ROOT_DIR=${ROOTSYS}
#export LD_LIBRARY_PATH=${ROOTSYS}/lib
#export PATH=${ROOTSYS}/bin:${PATH}

EXE="$WorkDir/fileCollector.py $CFGFILE"
RUN_STAT=`ps -ef | grep fileCollector.py | grep -v grep | wc | awk '{print $1}'`
#DOG_STAT=`ps -ef | grep alivecheck_filesave.sh | grep -v grep | wc | awk '{print $1}'`

#if [ $DOG_STAT -gt 10 ]
#then
#    echo watchdog script seems to have some trouble at $HOSTNAME. | mail Hyunkwan.Seo@cern.ch
#    exit 0
#fi

if [ $RUN_STAT -ne 0 ]
then
    echo fileCollector.py is running at $HOSTNAME.
else
    echo fileCollector.py stopped by unknown reason and restarted now.
    LOG=$WorkDir/log/LOG.filesave.$HOSTNAME.$$
    date >& $LOG
    echo fileCollector.py stopped by unknown reason and restarted at $HOSTNAME. >> $LOG
    $EXE >> $LOG 2>&1 & 
    echo fileCollector.py stopped by unknown reason and restarted now at $HOSTNAME. | mail -s "fileCollector not Running" $YourEmail
fi
