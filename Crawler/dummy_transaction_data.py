import MySQLdb
import random
from uuid import uuid4
import datetime

def get_db_connect():
    return MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="a",  # your password
                     db="test_xrp_admin")

def close_db(db):
    return db.close()

def insert_dummy_data(ta,count = 0):
    insert_query = 'Insert into admin_panel_transaction_master' \
                   ' (from_address,to_address,amount,txid,sequence,ledger_index,created_at,bid_id)' \
                   ' values(%s,%s,%s,%s,%s,%s,%s,%s)'
    for i in range(count):
        from_address = ta
        to_address = uuid4().hex
        amount = random.randint(1, 10000000)
        txid = uuid4().hex
        sequence = random.randint(1,100)
        ledger_index = random.randint(1,1000000)
        created_at = datetime.datetime.now()
        bid_id = random.randint(1000000,99999999)

        cur.execute(insert_query,(from_address,to_address,amount,txid,sequence,ledger_index,created_at,bid_id))

db = get_db_connect()
cur = db.cursor()


insert_dummy_data(ta='rDUoc5LePtDy1RGfvJDYZrQfLjQigvzaiy',count=10)


db.commit()
close_db(db)



# # Use all the SQL you like
# columns = ['id', 'from_address', 'to_address', 'txid', 'created_at', 'ledger_index', 'sequence', 'bid_id']
# query = 'SELECT ' + ','.join(columns) + ' FROM aux_ripp_transaction_master'
# cur.execute(query)
#
# x = prettytable.PrettyTable(columns)
#
# # print all the first cell of all the rows
# for row in cur.fetchall():
#     x.add_row(row)
#
# print x