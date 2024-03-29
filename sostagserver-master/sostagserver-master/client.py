import socket

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))
client.connect(('www.mymedbook.it', 4242))

mmtag = 'W000501'
longitude = 10.4733796
latitude = 43.6815689

# send some data (in this case a HTTP GET request)
client.send('{},{},{}'.format(mmtag, latitude, longitude))


# receive the response data (4096 is recommended buffer size)
response = client.recv(4096)

print response
