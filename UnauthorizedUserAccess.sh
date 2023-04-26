#!/bin/bash

function ShowUsage {
   echo "-------------------------------------------------------------------------------------------------------------------------------"
   echo "Usage:"
   echo "      -u  User Name"
   echo "      -h  database_host"
   echo "      -p  port"
   echo "      -P  passwd"
   echo "Example:"
   echo "  []$ /bin/bash UnauthorizedUserAccess.sh -u=root -h=10.10.10.10 -p=3060 -P=passwd"
   echo "  "
   echo ""
   exit 1
}

for i in  "$@"; do
   case $i in
      -u=*)
      USER="${i#*=}"
      ;;
      -h=*)
      HOST="${i#*=}"
      ;;
      -p=*)
      PORT="${i#*=}"
      ;;
      -P=*)
      PASSWD="${i#*=}"
      ;;
      help|*)
      ShowUsage
      ;;
   esac
done


DBAemail=abc@xyz.com

THRESHOLD=1
export datetime=$(date +%Y%m%d%H%M)
export logfile=UnauthorizedUserAccess_$datetime.log

query="select extract( year from logged ) year, extract( month from logged ) month,extract( day from logged ) day,REGEXP_SUBSTR(data, '[a-z]+', 1, 5) user,REGEXP_SUBSTR(data,'[0-9.]+') IPAddress,count(*) 
from performance_schema.error_log where error_code ='MY-010926' and  logged >= curdate() group by 1,2,3,4,5 having count(*)> ${THRESHOLD}"

echo $query
mysql -u$USER -h$HOST -P$PORT -p$PASSWD -e "${query};"  > UnauthorizedUserAccess_$$.txt

if [[ ! -s UnauthorizedUserAccess_$$.txt ]]; then
   rm -rf UnauthorizedUserAccess_$$.txt
   exit 0
else 
   echo "There are some unauthorized attempts to access a database found  more than $THRESHOLD attemps:"  >> $logfile
   echo "     " >> $logfile
   echo "     " >> $logfile
   echo "     " >> $logfile
   echo "==========================================================  "  >> $logfile
   echo "unauthorized attempts to access a database "  >> $logfile
   echo "=========================================================  "  >> $logfile
   echo "     " >> $logfile
    
   cat UnauthorizedUserAccess_$$.txt >> $logfile
fi


if [[ -f $logfile && -s $logfile && -s UnauthorizedUserAccess_$$.txt ]]; then
    mail -s "Alert: unauthorized attempts to access a database" $DBAemail < $logfile
else 
   >$logfile
fi

#rm -rf UnauthorizedUserAccess_$$.txt


