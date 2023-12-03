import pymysql
import configparser
import pandas as pd
from dbutils.persistent_db import PersistentDB
import os
from threading import RLock
import copy
from datetime import datetime

MYSQL = 'mysql'
test = False

def d_parse_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return config

def d_log_error(error):
    """
    打印错误日志
    """
    with open('error.log','a+',encoding='utf-8') as f:
        for key,value in error.items():
            if key == 'error':
                f.write(str(value))
                f.write('#')
            if key == 'value':
                f.write(str(value))
                f.write('#')
            if key == 'table':
                f.write(str(value))
        f.write('\n')
        
project_configs = d_parse_config()

def mysql_connect(config='mysql'):
    """
    连接数据库
    """
    db = pymysql.connect(
        host='rm-2vc07dt7jw3vtt8x1uo.mysql.cn-chengdu.rds.aliyuncs.com',
        port = 3306,
        user = 'bidder_dev',
        password = 'Bidder@2022!',
        db = 'bigdata-com',
        charset='utf8'
    )
    return db

db = mysql_connect(MYSQL)

def mysql_connect_pool(config='mysql'):
    pool = PersistentDB(
                    pymysql,
                    5,
                    host='rm-2vc07dt7jw3vtt8x1uo.mysql.cn-chengdu.rds.aliyuncs.com',
                    port=3306,
                    user='bidder_dev',
                    password='Bidder@2022!',
                    db='bigdata-com',
                    charset='utf8',
                    setsession=['SET AUTOCOMMIT = 1']
                    )
                        
    return pool


pool = mysql_connect_pool(MYSQL)

conn = pool.connection()

LOCK = RLock()

def mysql_select_df(sql):
    """
    执行sql，返回的数据转换成dataframe，并且表头是列名
    """
    import pandas as pd
    with LOCK:
        cursor = conn.cursor()  
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
    df = pd.DataFrame(data)
    try:
        df.columns = [i[0] for i in cursor.description]
    except:
        # 为空
        pass
    return df

def mysql_select_data_by_ids(ids,table):
    """
    使用id批量查询数据
    """
    sql = "select * from {} where id in {}".format(table,tuple(ids))
    df = mysql_select_df(sql)
    return df

def mysql_delete_data(df,task):
    """
    使用df的id，批量删除数据表中的数据
    """
    sql = 'delete from %s where id in %s'
    cursor = conn.cursor()
    cursor.executemany(sql,(project_configs[task]['target'],df['id'].values.tolist()))
    db.commit() 


def mysql_delete_data_by_id(id,table):
    """
    使用id删除数据表中的数据
    """
    sql = "delete from {} where id = '{}'".format(table,id)
    with LOCK:
        cursor = conn.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()

def mysql_delete_win_by_id(id,table_name,table):
    """
    使用id删除数据表中的数据
    """
    sql  = f"delete from {table} where table_name = '{table_name}' and announcement_id = '{id}'"
    with LOCK:
        cursor = conn.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()

def mysql_delete_win_by_ids(ids,table_name,table):
    """
    使用ids删除对应的表格中的数据
    """
    sql = f"delete from {table} where table_name = '{table_name}' and announcement_id in {tuple(ids)}"
    with LOCK:
        cursor = conn.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()

def mysql_insert_data(df,table):
    """
    使用df的表头和数据拼成批量更新的sql语句
    """
    sql = 'insert into {} ({}) values ({})'.format(table,','.join(df.columns), ','.join(['%s'] * len(df.columns)))
    id_idx = df.columns.to_list().index('id')
    values = df.values.tolist()
    # 将NaT 替换成 ''
    for i in range(len(values)):
        for j in range(len(values[i])):
            if pd.isnull(values[i][j]):
                values[i][j] = None
    with LOCK:
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, values)
        except:
            for i in range(len(values)):
                if test:
                    cursor.execute(sql, values[i])
                else:
                    try:
                        select_id_df = mysql_select_df(f"select * from material where id = '{values[i][id_idx]}'")
                        if len(select_id_df)>0:
                            select_id_dict = select_id_df.iloc[0].to_dict()
                            # 逻辑一：新数据签订时间不为空时，旧数据时间为空或者及数据时间不为空但新数据时间大于旧数据时间，执行新数据不为空的字段替换旧数据对应字段
                            if (df.iloc[i]['signDate'] is not None and
                                    (select_id_dict['signDate'] is None or df.iloc[i]['signDate'] >= select_id_dict[
                                        'signDate'])):
                                # 如果新数据时间戳较新，检查字段是否为空,新数据不空，替换
                                for key, value in df.iloc[i].items():
                                    # 跳过创建时间字段
                                    if key == 'createTime':
                                        continue
                                    if value is not None:
                                        select_id_dict[key] = value
                                # 更新数据库中的数据
                            # 逻辑二：其余情况为执行补充旧数据空白数据
                            else:
                                # 新数据不空，旧数据空，更新
                                for key, value in df.iloc[i].items():
                                    # 跳过创建时间字段
                                    if key == 'createTime':
                                        continue
                                    if value is not None and select_id_dict[key] is None:
                                        select_id_dict[key] = value

                            select_id_dict['updateTime'] = datetime.now()
                            id = select_id_dict.pop('id')
                            partial_sql = ','.join([f"{key} = '{value}'" for key, value in select_id_dict.items()])
                            sql = f"update {table} set {partial_sql} where id = '{id}'".replace("'None'",'Null')
                            cursor.execute(sql)
                            print("Data updated successfully.")
                        else:
                            cursor.execute(sql, value)
                    except Exception as e:
                        error = {'error':e,'value':values[i],'table':table}
                        d_log_error(error)
        db.commit()
        cursor.close()

def mysql_delete_data_by_ids(ids,table):
    """
    使用ids删除对应的表格中的数据
    """
    sql = "delete from {} where id in {}".format(table,tuple(ids))
    with LOCK:
        cursor = conn.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()

def mysql_update(dict_value):
    """
    使用insert into语句批量更新表格的数据
    """
    tmp  = copy.deepcopy(dict_value)
    table = tmp.pop('table')
    id = tmp.pop('id')
    partial_sql = ','.join([f"{key} = '{value}'" for key,value in tmp.items()])
    sql = f"update {table} set {partial_sql} where id = '{id}'"
    with LOCK:
        cursor = conn.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()
