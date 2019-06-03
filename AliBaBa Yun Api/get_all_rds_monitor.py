import importlib
import json
import sys
import pymysql
import datetime
from datetime import timedelta

try:
    from termcolor import colored
    from xlsxwriter import workbook
    from aliyunsdkcore import client
    from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
    from aliyunsdkrds.request.v20140815.DescribeDBInstanceAttributeRequest import DescribeDBInstanceAttributeRequest
    from aliyunsdkrds.request.v20140815.DescribeDBInstancePerformanceRequest import DescribeDBInstancePerformanceRequest
    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
    from aliyunsdkcore.client import AcsClient
except ImportError as e:
    print(colored('%s : %s' % ('Error', e), 'red'))
    exit(9)

importlib.reload(sys)


# reload(sys)


# 定义可以执行插入数据的函数
def insertSQL(sqlStr):
    db = pymysql.connect("192.168.100.60", "gh_bf_mimosa", "guohuaiGUO4056&", "whtestdj", charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute(sqlStr)  # 执行sql
        db.commit()  # 提交修改
    except ClientException:
        print("Error: connection failed, unable to fetch data")
    except SyntaxError:
        db.rollback()  # 失败回滚
    db.close()


# 获取RDS运行时的监控信息
def get_RDS_minitor(AcesskeyID, AcesskeySecret, zone, rdsid, key, startTime, endTime):
    clt = client.AcsClient(AcesskeyID, AcesskeySecret, zone)
    request = DescribeDBInstancePerformanceRequest()
    request.set_accept_format('json')
    request.set_DBInstanceId(rdsid)
    request.set_Key(key)
    request.set_StartTime(startTime)
    request.set_EndTime(endTime)
    response = clt.do_action_with_exception(request)
    return json.loads(response)


# 将RDS监控数据放进列表中，列表中包含元组，每个元组代表一个监控信息
def format_RDS_minitor(data, key):
    result = []
    for i in range(len(key.split(','))):
        DBInstanceId = data['DBInstanceId']
        key = data['PerformanceKeys']['PerformanceKey'][i]['Key']
        key_value = data['PerformanceKeys']['PerformanceKey'][i]['Values']['PerformanceValue'][0]['Value']
        Recivedate = data['PerformanceKeys']['PerformanceKey'][i]['Values']['PerformanceValue'][0]['Date']
        format_time = datetime.datetime.strptime(Recivedate, "%Y-%m-%dT%H:%M:%SZ")
        beijing_time = format_time + timedelta(hours=8)
        time = str(beijing_time)
        value_format = data['PerformanceKeys']['PerformanceKey'][i]['ValueFormat']
        tuple = (DBInstanceId, key_value, time, key, value_format)
        result.append(tuple)
    return result


# 将列表里的元素提取，存入到数据库
def Decomposition_minito_RDS(data):
    DBInstanceId = data[0][0]
    MySQL_IOPS = data[0][1]
    MySQL_cpuusage = data[1][1].split('&')[0]
    MySQL_memusage = data[1][1].split('&')[1]
    MySQL_Network_recv_k = data[2][1].split('&')[0]
    MySQL_Network_sent_k = data[2][1].split('&')[1]
    MySQL_QPS = data[3][1].split('&')[0]
    MySQL_TPS = data[3][1].split('&')[1]
    MySQL_active_session = data[4][1].split('&')[0]
    MySQL_total_session = data[4][1].split('&')[1]
    Now_time = data[4][2]
    # print(DBInstanceId, MySQL_IOPS, MySQL_cpuusage, MySQL_memusage, MySQL_Network_recv_k, MySQL_Network_sent_k, MySQL_QPS, MySQL_TPS, MySQL_active_session, MySQL_total_session, Now_time)

    insert_sql = "insert into apitest_rds_minitor (`DBInstanceId`, `MySQL_IOPS`, `MySQL_cpuusage`, `MySQL_memusage`, `MySQL_Network_recv_k`, `MySQL_Network_sent_k`, `MySQL_QPS`, `MySQL_TPS`, `MySQL_active_session`, `MySQL_total_session`, `Now_time`)" \
                 " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                 % (DBInstanceId, MySQL_IOPS, MySQL_cpuusage, MySQL_memusage, MySQL_Network_recv_k, MySQL_Network_sent_k, MySQL_QPS, MySQL_TPS, MySQL_active_session, MySQL_total_session, Now_time)
    insertSQL(insert_sql)


def main():
    AcesskeyID = 'LTAI3NcAuxKivWNG'
    AcesskeySecret = '9WBhKbmTe5KmeurCHLq5qfkebiTHEI'
    zones = ['cn-beijing']

    rdsid = ['rm-2zenz683032bm4885', 'rm-2zen8430b4g5bql8b', 'rm-2zeswxv3enr583mt8', 'rm-2ze2g030zc5139n5p']
    key = "MySQL_QPSTPS,MySQL_IOPS,MySQL_Sessions,MySQL_NetworkTraffic,MySQL_MemCpuUsage"
    print(len(key.split(',')))
    nowTime = datetime.datetime.utcnow()
    startTime = datetime.datetime.strftime(nowTime - datetime.timedelta(minutes=5), "%Y-%m-%dT%H:%MZ")
    endTime = datetime.datetime.strftime(nowTime, "%Y-%m-%dT%H:%MZ")


    for zone in zones:
        for id in rdsid:
            RDS_minitor_info = get_RDS_minitor(AcesskeyID, AcesskeySecret, zone, id, key, startTime, endTime)
            RDS_minitor_data = format_RDS_minitor(RDS_minitor_info, key)
            print(RDS_minitor_data)
            Decomposition_minito_RDS(RDS_minitor_data)


if __name__ == '__main__':
    main()
