# MySQLUnAuthorizedUsers
Problem Statement: script that will monitor unauthorized attempts to access a database and trigger a notification in case of too many (attempts) >10.

Script: UnauthorizedUserAccess.sh
1. The script UnauthorizedUserAccess.sh covers a scenario where MySQL instance configured to write ERROR LOG information to the database table and this scripts reads data and send an email if it finds any data which breaches the defined threshholds.
2. sh UnauthorizedUserAccess.sh -u=root -h=<<10.10.10.10>> -p=3306 -P=<<passwd>>

Script: ErrorLogParse.py
1. This script ErrorLogParse.py assumes MySQL instace configured to write ERROR LOG info to the error log file and in GCP environment we can retrieve respective info using GCLOUD LOGGING READ command and here i am using that approach to fetch the respective data from the log file and parsing that to perform analytics on top of that data for further actions.
2. pyton ErrorLogParse.py

Options Considered:
  1. MySQL ERROR Log - Table/File
     a. Compare to rest of the other two approaches i feel ERROR Log approach seems straight forward and provides more info which is handy to understand           the case.
     b. For Example, if you notice none of the other approaches gives if the attempt is due to missing password or due to wrong password try, which i               believe crucial to understand the scenario.
  
  2. MySQL General Log
     a. The problem of the General Query Log is that it will log everything so it can cause performance degradation and you will have to deal with very             large files on high loaded servers.
     b. Parameters involved: general_log=on and log_output=TABLE
     c. Data can be accessed from mysql.general_log table

  3. MySQL Audit plugin
     a. CloudSQL for MySQL facilitates "cloudsql_mysql_audit" as one of the flags which we can use to enable auditing in the instance
     b. Parameters involved: cloudsql_mysql_audit = ON/FORCE/FORCE_PLUS_PERMENANT/OFF
     c. we can choose what operations we like to enable auditing, in our case connect and disconnect are our interested operations, so we can enable this           using following commands.
     
          CALL mysql.cloudsql_create_audit_rule('*','*','*','connect,disconnect','B',0, @outval,@outmsg);
          SELECT @outval, @outmsg;
          CALL mysql.cloudsql_reload_audit_rule(1)
     d. respective data can be accessed from log viewer using log type logName=( "projects/<<projectName>>/logs/cloudaudit.googleapis.com%2Fdata_access")
     e. Sample Log file for example:
          {
            insertId: "2#40341998183#829766093922394308#cloudsql_mysql_audit#1682300554494849323#000000000000231a-0-0@a1"
            labels: {2}
            logName: "projects/manh-tsg-sandbox/logs/cloudaudit.googleapis.com%2Fdata_access"
            protoPayload: {
            @type: "type.googleapis.com/google.cloud.audit.AuditLog"
            methodName: "cloudsql.instances.query"
            request: {
            @type: "type.googleapis.com/google.cloud.sql.audit.v1.MysqlAuditEntry"
            cmd: "connect"
            date: "2023-04-24T14:09:30.998222Z"
            errCode: "1045"
            ip: "199.47.37.3"
            msgType: "activity"
            privUser: "root"
            queryId: "0"
            status: "unsuccessful"
            threadId: "9426"
            user: "root"
            }
            resourceName: "instances/mohaninst1"
            serviceName: "cloudsql.googleapis.com"
            }
            receiveTimestamp: "2023-04-24T14:09:33.807692640Z"
            resource: {2}
            severity: "INFO"
            timestamp: "2023-04-24T14:09:30.998222Z"
           }
