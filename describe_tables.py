#!/usr/bin/env python
import argparse, mysql.connector, os, sys, re

def prepare_sql_query(all,dbs):
  if all=="yes":
    sql_query="select concat(table_schema,'.',table_name) from information_schema.tables where table_schema != \'information_schema\'"
  elif all=="no":
    sql_query="select concat(table_schema,'.',table_name) from information_schema.tables where table_schema = \""+dbs+"\""
  else :
    sql_query="select concat(table_schema,'.',table_name) from information_schema.tables where table_schema != \'information_schema\' and table_schema like \"%"+db_grep+"%\""
  return sql_query

parser = argparse.ArgumentParser(add_help=True)
group = parser.add_argument_group('host')
group.add_argument('-H', action="store")
group = parser.add_mutually_exclusive_group()
group.add_argument('-A', action="store_true", default=True)
group.add_argument('-l', action='store')
group.add_argument('-d', action='store')

options_values = parser.parse_args()
host=options_values.H
db=options_values.d
db_grep=options_values.l
db_all=options_values.A


if db:
  all="no"
  dbs=db
elif db_grep:
  all="like"
  dbs="information_schema"
else :
  all="yes"
  dbs="information_schema"

sql_query = prepare_sql_query(all,dbs)

PASSWORD = os.environ.get('DB_PASSWORD')
if not PASSWORD:
    print ("DB_PASSWORD variable is not set")
    sys.exit(2)
USER = os.environ.get('DB_USER')
if not USER:
    print ("DB_USER variable is not set")
    sys.exit(2)

db_conection = mysql.connector.connect(
  host=host,
  user=USER,
  password=PASSWORD,
  database=dbs
)


db_cursor = db_conection.cursor(buffered=True)
db_cursor.execute(sql_query)
db_result = db_cursor.fetchall()


for x in db_result:
  table_name=(str(x).replace('\'', '').replace('(', '').replace(')', '').replace(',', ''))
  print(table_name)
  describe_table=("describe "+table_name)
  file_name=(table_name+".txt")
  db_cursor.execute(describe_table)
  table_description=str(db_cursor.fetchall()).replace('[','').replace(']','').replace('), ','\n').replace('(\'','\'')#.replace(')$','')
  table_description=re.sub('\)$', '', table_description)
  f = open(file_name, "w")
  f.write(table_description)
  f.close()
db_cursor.close()