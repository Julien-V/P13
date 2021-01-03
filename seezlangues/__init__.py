#!/usr/bin/python3
# coding : utf-8

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DATABASE = "dbname=postgres"
DATABASE2 = "dbname=seezlangues"


def create_db():
    sql = "CREATE DATABASE seezlangues WITH ENCODING='utf8'"
    try:
        conn = psycopg2.connect(DATABASE)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute(sql)
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def exist_db():
    exist = True
    try:
        if DATABASE2:
            conn = psycopg2.connect(DATABASE2)
        else:
            conn = psycopg2.connect(DATABASE)
        conn.close()
    except psycopg2.OperationalError as e:
        print(e)
        exist = False
    return exist


if not exist_db():
    print("[!] No DB")
    if create_db():
        print("[*] DB created")
    else:
        print("[*] Error")
