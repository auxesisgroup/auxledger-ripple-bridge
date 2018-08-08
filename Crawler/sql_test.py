import MySQLdb
import prettytable

def get_db_connect():
    return MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="a",  # your password
                     db="test_xrp")

def close_db(db):
    return db.close()

def update_active_status(address,is_active):
    query = "Update aux_ripp_address_master set is_active = {is_active} where address = '{address}'".format(is_active=is_active,address=address)
    return cur.execute(query)



db = get_db_connect()
cur = db.cursor()


status = update_active_status(address='rDUoc5LePtDy1RGfvJDYZrQfLjQigvzaiy',is_active=True)
print(status)


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