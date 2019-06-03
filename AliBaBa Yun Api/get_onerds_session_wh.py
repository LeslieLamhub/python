from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.acs_exception.exceptions import ClientException
# from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkrds.request.v20140815.DescribeDBInstancePerformanceRequest import DescribeDBInstancePerformanceRequest

import datetime
from datetime import  timedelta
import json
import pymysql


client = AcsClient(
   "LTAI3NcAuxKivWNG",
   "9WBhKbmTe5KmeurCHLq5qfkebiTHEI",
   "cn-beijing"
);


def getpf(resid, key, startTime, endTime):
    request = DescribeDBInstancePerformanceRequest()
    request.set_accept_format('json')
    request.set_DBInstanceId(resid)
    request.set_Key(key)
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    response = client.do_action_with_exception(request)
    return json.loads(response)


def getSQLdata(self,sqlStr):
    db = pymysql.connect("192.168.100.66", "gh_bf_mimosa", "guohuaiGUO4056&", "whtestdj", charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute(sqlStr)
        results=cursor.fetchall()
        print(results)
    except:
        print("Error: unable to fetch data")
    db.close()
    return results

bjtime = datetime.datetime.now()
zhuanhuantime = bjtime - timedelta(hours=8)
nowTime = datetime.datetime.utcnow()
timestamp = datetime.datetime.strftime(nowTime,"%Y-%m-%dT%H:%M:%SZ")
startTime = datetime.datetime.strftime(nowTime-datetime.timedelta(minutes=6),"%Y-%m-%dT%H:%MZ")
endTime = datetime.datetime.strftime(nowTime,"%Y-%m-%dT%H:%MZ")

print(bjtime, zhuanhuantime, nowTime, timestamp, startTime, endTime)
id = "rm-2zenz683032bm4885"
key = "MySQL_Sessions"
rs = getpf(id, key, startTime, endTime)

print(rs['ValueFormat'].split('&')[0])
#print(rs['PerformanceKeys']['PerformanceKey'][0]['Values']['PerformanceValue'][0])
#print(rs['PerformanceKeys']['PerformanceKey'][0]['Values']['PerformanceValue'][0]['Value'])

#print(rs['PerformanceKeys']['PerformanceKey'][0]['Values']['PerformanceValue'][0]['Value'].split('&')[0])
#print(rs['PerformanceKeys']['PerformanceKey'][0]['Values']['PerformanceValue'][0]['Date'])
# python2:  print(response)
# print(str(response, encoding='utf-8'))

datestr="2019-05-20T07:24:52Z"

dttime = datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
nowtime = dttime + timedelta(hours=-8)

print("====",dttime , nowtime)
