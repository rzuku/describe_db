#!/usr/bin/env python
import argparse
import mysql.connector
import os
import sys
import re

def prepare_sql_query(all):
    if all == "yes":
        sql_query = (
            "select concat(table_schema,'.',table_name) from information_schema.tables \
                where table_schema != %s")
    elif all == "no":
        sql_query = (
            "select concat(table_schema,'.',table_name) from information_schema.tables \
                where table_schema = %s")
    else:
        sql_query = (
            "select concat(table_schema,'.',table_name) from information_schema.tables \
                where table_schema like concat('%', %s, '%')")
    return sql_query

parser = argparse.ArgumentParser(add_help=True)
group = parser.add_argument_group('host')
group.add_argument('-H', action="store", help='provide DB Host address')
group = parser.add_mutually_exclusive_group()
group.add_argument('-A', action="store_true", default=True,
                   help='will get structure of all DBs')
group.add_argument('-l', action='store',
                   help='provide substring of db name. This will be used to go \
                       to all dbs like ...')
group.add_argument('-d', action='store', help='provide db name')

options_values = parser.parse_args()
host = options_values.H
db = options_values.d
db_grep = options_values.l
db_all = options_values.A

if db:
    all = "no"
elif db_grep:
    all = "like"
    db = db_grep
else:
    all = "yes"
    db = "information_schema"

PASSWORD = os.environ.get('DB_PASSWORD')
if not PASSWORD:
    print("DB_PASSWORD variable is not set")
    sys.exit(2)
USER = os.environ.get('DB_USER')
if not USER:
    print("DB_USER variable is not set")
    sys.exit(2)

try:
    db_conection = mysql.connector.connect(
        host=host,
        user=USER,
        password=PASSWORD,
        database="information_schema"
    )
except mysql.connector.errors.ProgrammingError as ie:
    print("Exception : {0}".format(ie))
    sys.exit(2)

sql_query = prepare_sql_query(all)
db_cursor = db_conection.cursor(buffered=True)
db_cursor.execute(sql_query, (db, ))
db_result = db_cursor.fetchall()

for table in db_result:
    table_name = (str(table).replace('\'', '').replace(
        '(', '').replace(')', '').replace(',', ''))
    print(table_name)
    describe_table = ("describe "+table_name)
    file_name = (table_name+".txt")
    db_cursor.execute(describe_table)
    table_description = re.sub('\)\]$|^\[\(', '', str(db_cursor.fetchall()))
    table_description = re.sub('\), \(', '\n', table_description)
    f = open(file_name, "w")
    f.write(table_description)
    f.close()
db_cursor.close()
