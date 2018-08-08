import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

# r.set('foo', 1)
# r.set('foo',int(r.get('foo')) + 1)
# value = r.get('foo')
# print(value)

# r.sadd('xrp_multi_address','rfLFKGKSq4K9eZg1LzaXuPuxZc5GdKwyRt')
# r.sadd('xrp_multi_address','r3QyzpwXDQr7YMDTLoC5vX867Hqz32pENH')
# r.sadd('xrp_multi_address','r9BAwyyVVYkqRb6jgB7nX7Jb7WxxvFhQpN')
print r.smembers('xrp_multi_address')

# print (r.smembers('a1'))
# print type(r.smembers('a1'))
# r.srem('a1','1')
# print r.smembers('a1')
# r.delete('a1')
# print r.smembers('a1')