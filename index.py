import sys
import os
import hashlib
import sqlite3
from sqlite3 import Error

#CertUtil -hashfile C:\TEMP\MyDataFile.img MD5
block_size = 16*512

def true_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
def md5(fname):
    hash_md5 = hashlib.md5()
    size = os.stat(fname).st_size 
    f = open(fname, "rb")

    dat = f.read(block_size)
    hash_md5.update(dat)

    sz = 1
    while sz*block_size<size:
        print(sz)
        f.seek(sz*block_size)
        dat = f.read(block_size)
        hash_md5.update(dat)
        sz = sz * 2
    f.close()
    md = hash_md5.hexdigest()
    print(md)
    return md

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None

def create_table(create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_rec(f):
    sql = 'INSERT INTO files(name, size, mtime, md5) VALUES(?,?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, f)
    conn.commit()
    return cur.lastrowid
    
def exist_rec(name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE name=?", (name,))
    rows = cur.fetchall()
    print(len(rows))
    return len(rows) > 0

if __name__ == '__main__':
    database = "sqlite.db"
    sql_create_table = 'CREATE TABLE IF NOT EXISTS files (id integer PRIMARY KEY, name text NOT NULL, size integer, mtime float NOT NULL, md5 text NOT NULL);'
    conn = create_connection(database)
    if conn is not None:
        create_table(sql_create_table)
    else:
        print("Error! cannot create the database connection.")

    for entry in scantree(sys.argv[1] if len(sys.argv) > 1 else '.'):
        print(entry.path)
        f_md5 = md5(entry.path)
        f_size = os.stat(entry.path).st_size 
        f_mtime = os.stat(entry.path).st_mtime
        if not exist_rec(entry.path):
            insert_rec((entry.path, f_size, f_mtime, f_md5))
    
    conn.close()