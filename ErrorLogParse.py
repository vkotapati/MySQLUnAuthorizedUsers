import re
import csv
import subprocess
import pandas as pd

def processdata(inputfilename, pat):
    fields = ['time','thread','User_Host','password']
    
    lines = ''
    filename = open(inputfilename, 'r')
    for line in filename:
        lines = lines + line

    f=re.findall(pat, lines, re.MULTILINE |re.DOTALL)
    df = pd.DataFrame(f, columns =['time', 'thread', 'user','passwd'])
    df['time']=df['time'].astype('datetime64[ns]')
    df['H']=df.time.dt.hour
    df['D']=df.time.dt.date

    # To Check the counts
    dfc = df.groupby(['D','H','user'])['user'].size().reset_index(name='counts')
    
    #To get the details of attempts which are failed more than 4 times in a given hour
    dfs = df.groupby(['D','H','user']).filter(lambda x: len(x) > 4)
    return dfc,dfs


def generatecsv(inputfilename, pat):
    outfilename = inputfilename.split('.')[0]+'.csv'
    fields = ['time','thread','User_Host','password']
    
    lines = ''
    filename = open(inputfilename, 'r')
    for line in filename:
        lines = lines + line
    
    
    with open(outfilename, 'w', newline='') as myfile:
        writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        headers_printed = False
        for match in re.finditer(pat, lines, re.MULTILINE |re.DOTALL):
            if not headers_printed:
                writer.writerow(fields)
                headers_printed = True
            writer.writerow(match.groups())

if __name__ == '__main__':
    FILTER="resource.type=\\\"cloudsql_database\\\" resource.labels.database_id=\\\"manh-tsg-sandbox:mohaninst1\\\" logName=\\\"projects/manh-tsg-sandbox/logs/cloudsql.googleapis.com%2Fmysql.err\\\""
    
    cmd_str = "gcloud logging read \""+FILTER + " AND receiveTimestamp>=\\\"2023-04-21T00:00:01\\\" AND receiveTimestamp<=\\\"2023-04-21T10:30:01\\\"  AND textPayload : (\\\"Access denied\\\") \"   --format=json --format=\"value(textPayload)\" --project manh-tsg-sandbox --freshness=1d --order=asc> cloud-sql-slow.log 2> error.log"
    subprocess.run(cmd_str, shell=True)

    #2023-04-21T02:58:38.532957Z 710 [Note] [MY-010926] [Server] Access denied for user 'root'@'199.47.37.3' (using password: YES)
    pat = r"""^(?P<time>\d{4}.\d{2}.\d{2}T\d{2}:\d{2}:\d{2}.\d{6}Z\s?)+(?P<thread>\d+)\s+\[Note\]+\s+\[MY-010926\]+\s\[Server\]\s+Access+\s+denied+\s+for+\s+user+\s+(?P<User_Host>.*?)\s+\(using\s+password:+\s+(?P<password>.*?)\)$"""
    
    #inputfilename = sys.argv[1]
    generatecsv('cloud-sql-slow.log',pat)
    dfc,dfs=processdata('cloud-sql-slow.log',pat)
    print(dfc)
    print(dfs)

    # Logic to send an email or interface CSV file to grafana/other tools to send an alert to pager duty.