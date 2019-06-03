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
    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
    from aliyunsdkcore.client import AcsClient
except ImportError as e:
    print(colored('%s : %s' % ('Error', e), 'red'))
    exit(9)

importlib.reload(sys)


# reload(sys)


def get_sys_info(key, secret, zone):
    '''
    1、获取该区域全部主机详细信息
    2、参数：cn-qingdao、cn-hangzhou、cn-beijing 等
    '''
    # 与阿里云建立有效连接
    clt = client.AcsClient(key, secret, zone)
    # 获取该区域全部实例详细信息
    request = DescribeInstancesRequest.DescribeInstancesRequest()
    request.set_PageSize(100)
    request.set_PageNumber(1)
    # 将数据格式化成 json，默认为 XML
    request.set_accept_format('json')
    # 发起请求，获取数据
    result = json.loads(clt.do_action_with_exception(request)).get('Instances').get('Instance')
    print(result)
    return result


def get_rds_info(key, secret, zone):
    clt = client.AcsClient(key, secret, zone)
    request = DescribeDBInstanceAttributeRequest()
    # request.setKey()
    request.set_action_name("DescribeDBInstances")
    # 将数据格式化成 json，默认为 XML
    request.set_accept_format('json')
    # 发起请求，获取数据
    result = json.loads(clt.do_action_with_exception(request)).get('Items').get('DBInstance')
    print(result)
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
    print(result)
    return result

# 挑选有用的ECS实例信息，放到列表里
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
    print(result)
    return result

# 定义可以执行插入数据的函数
def insertSQL(sqlStr):
    db = pymysql.connect("192.168.100.60", "gh_bf_mimosa", "guohuaiGUO4056&", "whtestdj", charset='utf8')
    cursor = db.cursor()
    try:
        cursor.execute(sqlStr)
        db.commit()
    except ClientException:
        print("Error: connection failed, unable to fetch data")
    except SyntaxError:
        db.rollback()
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

        insert_sql = "insert into apitest_ecs (InstanceId, ZoneId, InstanceName, Cpu, Memory, PrivateIpAddress, PublicIpAddress, InternetMaxBandwidthOut, Status, CreationTime, ExpiredTime, VpcId)" \
                     " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                     % (InstanceId, ZoneId, InstanceName, Cpu, Memory, PrivateIpAddress, PublicIpAddress, InternetMaxBandwidthOut, Status, CreationTime, ExpiredTime, VpcId)
        insertSQL(insert_sql)

# 将获取到的RDS实例信息进行遍历通过设置变量，插入到数据库
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

        insert_sql = "insert into apitest_rds (DBInstanceId, DBInstanceDescription, DBInstanceType, Engine,  EngineVersion, ZoneId, DBInstanceStatus, CreateTime, ExpireTime)" \
                     " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
                     % (DBInstanceId, DBInstanceDescription, DBInstanceType, Engine,  EngineVersion, ZoneId, DBInstanceStatus, CreateTime, ExpireTime)
        insertSQL(insert_sql)




def main():
    key = 'LTAI3NcAuxKivWNG'
    secret = '9WBhKbmTe5KmeurCHLq5qfkebiTHEI'
    zones = ['cn-beijing']

    for zone in zones:
        info = get_sys_info(key, secret, zone)
        data = format_ecsdata(info)
        Decomposition_ECS_data(data)
        rds = get_rds_info(key, secret, zone)
        data = format_rdsdata(rds)
        Decomposition_RDS_data(data)


if __name__ == '__main__':
    main()
