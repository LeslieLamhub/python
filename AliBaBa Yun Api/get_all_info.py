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


def get_sys_info(AcesskeyID, AcesskeySecret, zone):
    """
    1、获取该区域全部主机详细信息
    2、参数：cn-qingdao、cn-hangzhou、cn-beijing 等
    """
    # 与阿里云建立有效连接
    clt = client.AcsClient(AcesskeyID, AcesskeySecret, zone)
    # 获取该区域全部实例详细信息
    request = DescribeInstancesRequest.DescribeInstancesRequest()
    request.set_PageSize(100)
    request.set_PageNumber(1)
    # 将数据格式化成 json，默认为 XML
    request.set_accept_format('json')
    # 发起请求，获取数据
    # 加了.get获取到的数据是一个列表
    result = json.loads(clt.do_action_with_exception(request)).get('Instances').get('Instance')
    return result


def get_rdsdata(AcesskeyID, AcesskeySecret, zone):
    """
       1、获取该区域全部RDS实例详细信息
       2、参数：cn-qingdao、cn-hangzhou、cn-beijing 等
    """
    clt = client.AcsClient(AcesskeyID, AcesskeySecret, zone)
    request = DescribeDBInstanceAttributeRequest()
    # request.setKey()
    request.set_action_name("DescribeDBInstances")
    # 将数据格式化成 json，默认为 XML
    request.set_accept_format('json')
    # 发起请求，获取数据
    # 加了.get获取到的数据是一个列表
    result = json.loads(clt.do_action_with_exception(request)).get('Items').get('DBInstance')
    return result


# 挑选有用的ECS实例信息，放到列表里
def format_ecsdata(data_info):
    result = []

    for line in data_info:
        data = (
            line.get('InstanceId'),
            line.get('ZoneId'),
            line.get('InstanceName'),
            line.get('Cpu'),
            line.get('Memory'),
            line.get('VpcAttributes').get('PrivateIpAddress').get('IpAddress')[0],
            line.get('PublicIpAddress').get('IpAddress'),
            line.get('InternetMaxBandwidthOut'),
            line.get('Status'),
            line.get('CreateTime'),
            line.get('ExpiredTime'),
            line.get('VpcAttributes').get('VpcId'),
        )
        result.append(data)
    return result


# 挑选有用的RDS实例信息，放到列表里
def format_rdsdata(data_info):
    result = []

    for line in data_info:
        data = (
            line.get('DBInstanceId'),
            line.get('DBInstanceDescription'),
            line.get('DBInstanceType'),
            line.get('Engine'),
            line.get('EngineVersion'),
            line.get('ZoneId'),
            line.get('DBInstanceStatus'),
            line.get('CreateTime'),
            line.get('ExpireTime')
        )
        result.append(data)
    return result


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


# 将获取到的ECS实例信息进行遍历通过设置变量，插入到数据库
def Decomposition_ECS_data(data):
    for i in data:
        InstanceId = i[0]
        ZoneId = i[1]
        InstanceName = i[2]
        Cpu = i[3]
        Memory = i[4]
        PrivateIpAddress = i[5]
        if len(i[6]) == 0:
            PublicIpAddress = "null"
        else:
            for j in i[6]:
                PublicIpAddress = j
        InternetMaxBandwidthOut = i[7]
        Status = i[8]
        Recive_CreationTime = i[9]
        changetime1 = datetime.datetime.strptime(Recive_CreationTime, "%Y-%m-%dT%H:%MZ")
        CreationTime = changetime1 + timedelta(hours=8)
        Recive_ExpiredTime = i[10]
        changetime2 = datetime.datetime.strptime(Recive_ExpiredTime, "%Y-%m-%dT%H:%MZ")
        ExpiredTime = changetime2 + timedelta(hours=8)
        VpcId = i[11]

        insert_sql = "insert into apitest_ecs (`InstanceId`, `ZoneId`, `InstanceName`, `Cpu`, `Memory`, `PrivateIpAddress`, `PublicIpAddress`, `InternetMaxBandwidthOut`, `Status`, `CreationTime`, `ExpiredTime`, `VpcId`)" \
                     " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                     % (InstanceId, ZoneId, InstanceName, Cpu, Memory, PrivateIpAddress, PublicIpAddress,
                        InternetMaxBandwidthOut, Status, CreationTime, ExpiredTime, VpcId)
        insertSQL(insert_sql)


# 将获取到RDS实例信息进行遍历通过设置变量，插入到数据库
def Decomposition_RDS_data(data):
    for i in data:
        DBInstanceId = i[0]
        DBInstanceDescription = i[1]
        DBInstanceType = i[2]
        Engine = i[3]
        EngineVersion = i[4]
        ZoneId = i[5]
        DBInstanceStatus = i[6]
        Recive_CreateTime = i[7]
        changetime1 = datetime.datetime.strptime(Recive_CreateTime, "%Y-%m-%dT%H:%M:%SZ")
        CreateTime = changetime1 + timedelta(hours=8)
        if i[8] != "":
            Recive_ExpireTime = i[8]
            changetime2 = datetime.datetime.strptime(Recive_ExpireTime, "%Y-%m-%dT%H:%M:%SZ")
            ExpireTime = changetime2 + timedelta(hours=8)
        else:
            ExpireTime = "0000-00-00 00:00:00"

        insert_sql = "insert into apitest_rds (`DBInstanceId`, `DBInstanceDescription`, `DBInstanceType`, `Engine`,  `EngineVersion`, `ZoneId`, `DBInstanceStatus`, `CreateTime`, `ExpireTime`)" \
                     " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                     % (DBInstanceId, DBInstanceDescription, DBInstanceType, Engine, EngineVersion, ZoneId,
                        DBInstanceStatus, CreateTime, ExpireTime)
        insertSQL(insert_sql)


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
        # ECS_info = get_sys_info(AcesskeyID, AcesskeySecret, zone)
        # ECS_data = format_ecsdata(ECS_info)
        # Decomposition_ECS_data(ECS_data)
        # RDS_info = get_rdsdata(AcesskeyID, AcesskeySecret, zone)
        # RDS_data = format_rdsdata(RDS_info )
        # Decomposition_RDS_data(RDS_data)
        for id in rdsid:
            RDS_minitor_info = get_RDS_minitor(AcesskeyID, AcesskeySecret, zone, id, key, startTime, endTime)
            RDS_minitor_data = format_RDS_minitor(RDS_minitor_info, key)
            print(RDS_minitor_data)
            Decomposition_minito_RDS(RDS_minitor_data)


if __name__ == '__main__':
    main()
