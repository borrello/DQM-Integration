#! /bin/sh

export WorkDir=$(dirname $0)
YourEmail=lilopera@cern.ch
source /nfshome0/cmssw2/scripts/setup.sh

XPYTHONPATH=$PYTHONPATH
source /home/dqm/rpms/slc4_ia32_gcc345/cms/dqmgui/5.0.2/etc/profile.d/env.sh
export PYTHONPATH=$XPYTHONPATH:$PYTHONPATH
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
EXE="$WorkDir/fileTransfer.py $CFGFILE"
RUN_STAT=`ps -ef | grep "fileTransfer.py $CFGFILE"| grep -v grep | wc | awk '{print $1}'`

if [ $RUN_STAT -ne 0 ]
then
    echo fileTransfer.py is running
else
    echo fileTransfer.py stopped by unknown reason and restarted now.
    TIMETAG=$(date +"%Y%m%d_%H%M%S")
    LOG=$WorkDir/log/LOG.fileTransfer.$HOSTNAME.$TIMETAG
    $EXE >& $LOG &
    date >> $LOG
    echo fileTransfer.py stopped by unknown reason and restarted at $HOSTNAME. >> $LOG
    echo fileTransfer.py stopped by unknown reason and restarted now at $HOSTNAME. | mail mail -s "fileTransfer not Running" $YourEmail
fi