import re
import urllib2
import socket
import threading
import psycopg2
import logging

#create logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MMB")

GENERIC_ERROR = 'ERR:Malformed request, acceptable format is "<MYMEDTAG CODE>,<LATITUDE>,<LONGITUDE>" but received {}'

DSN = "host=localhost port=5432 dbname=mymedbook user=mymedbook password=mymedbook"
QUERY="""select s.id,s.name,u.first_name,u.last_name
from backend_mymedtag t
join public.backend_structureaffiliation a on a.id=t.structure_affiliation_id
join public.backend_structure s on s.id =a.structure_id
join public.backend_userprofile u on u.id=a.user_id
where t.active and t.code=%s"""

bind_ip = '0.0.0.0'
bind_port = 4242

REQUEST_URL = "https://www.mymedbook.it/api/v1/COC/assistance/request/?code={}&latlng=({},{})&COC={}"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(20)  # max backlog of connections


logger.info('Listening on {}:{}'.format(bind_ip, bind_port))


def handle_client_connection(client_socket):
    request = client_socket.recv(4096)
    try:
        conn = psycopg2.connect(DSN)
        logger.info('Received {}'.format(request))
        regex = r"^([\w\-]+),(\d+(?:\.\d+)?),(\d+(?:\.\d+)?)$"
        values = re.findall(regex,request)
        if len(values)==0:
            client_socket.send(GENERIC_ERROR.format(request))
        elif len(values[0])!=3:
            client_socket.send(GENERIC_ERROR.format(request))
        else:
            try:
                values = list(values[0])
                cur = conn.cursor()
                cur.execute(QUERY,[values[0],])
                coc=cur.fetchone()
                conn.rollback()
                cur.close()
                if coc == None:
                    logger.error("ERR:MyMedTag {} not found".format(values[0]))
                    client_socket.send("ERR:MyMedTag {} not found".format(values[0]))
                else:
                    try:
                        values.append(coc[0])
                        r = urllib2.urlopen(REQUEST_URL.format(*values))
                        response = r.read()
                        if response != '{"message":"ok"}':
                            logger.error('MMB response {}'.format(response))
                            client_socket.send("ERR:Server error MyMedTag assistance request result is {}".format(response))
                        else:
                            logger.info('MMB response {}'.format(response))
                            client_socket.send('OK')
                    except Exception:
                        logger.error("ERR:Server error while sending MyMedTag assistance request", exc_info=True)
                        client_socket.send("ERR:Server error while sending MyMedTag assistance request")
            except Exception:
                logger.error("ERR:SQL error while retrieving MyMedTag {}".format(values[0]), exc_info=True)
                client_socket.send("ERR:SQL error while retrieving MyMedTag {}".format(values[0]))
        conn.close()
    except Exception:
        logger.error("ERR:Cannot open database", exc_info=True)
        client_socket.send("ERR:Cannot open database")
    finally:
        client_socket.close()

while True:
    client_sock, address = server.accept()
    print 'Accepted connection from {}:{}'.format(address[0], address[1])
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
    )
    client_handler.start()
