import pymongo

myclient = pymongo.MongoClient(host='127.0.0.1', port=27017)
mydb = myclient["mydatabase"]
# mycol = mydb["customers"]
#
# mydict = { "name": "John", "address": "Highway 37" }
#
# x = mycol.insert_one(mydict)

print(mydb.collection_names())