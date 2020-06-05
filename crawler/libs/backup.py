#!/usr/bin/env python
import os
import time


day = time.strftime("%Y-%m-%d-%H", time.localtime())

MySQL_Dump = '/usr/local/mysql/bin/mysqldump'
MYSQL_UserName = 'root'
MYSQL_PassWord = 'hack3321'
MYSQL_Database = 'hahamh'
Backup_Home = '/home/backup/'
if not os.path.isdir(Backup_Home):
    os.makedirs(Backup_Home)

lists = os.listdir(Backup_Home)
if len(lists) > 5:
    lists = lists[0: 3]
    for f in lists:
        os.remove(os.path.join(Backup_Home, f))

Backup_file = os.path.join(Backup_Home, 'db-%s-%s.sql' % (MYSQL_Database, day))
# if not os.path.isfile(Backup_file):
cmd = '%s -u%s -p%s %s > %s' % (
    MySQL_Dump, MYSQL_UserName, MYSQL_PassWord, MYSQL_Database, Backup_file)
os.system(cmd)
print('Backup Successfully. %s' % Backup_file)

# oss = Oss()
# (res, info) = oss.qi_niu(Backup_file)
# print(res)
