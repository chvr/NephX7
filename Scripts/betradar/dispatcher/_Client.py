import time
import threading
import socket

#import Logger
import SocketUtil


#log = Logger.Logger('Client')

def connect(host, port):
    global sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
    except Exception as e:
        log.error('Unable to connect - {}'.format(e))
        return False

    return True

def disconnect():
    if sock is not None:
        sock.close()

def main2():
    log.info('Started.')
    connect('localhost', 6010)
    log.info('Stopped.')


def handle_client(client_sock):
    while True:
        for i in range(1, 5):
            client_sock.send('<match matchid="944423" feedtype="full" includeavailable="yes"/>'.format(client_sock))
            log.info('Message from client: {}'.format(client_sock.receive()))
        time.sleep(5)
        print('x')

def handle_client2(client_sock):
    while True:
        for i in range(1, 5):
            client_sock.send('Message from C: {}'.format(client_sock))
            log.info('Message from client: {}'.format(client_sock.receive()))
        time.sleep(5)
        print('y')

def x2():
    client_sock = SocketUtil.ClientSocket()
    print(client_sock.is_connected)
    client_sock.connect('127.0.0.1', 6010, ssl_mode=True)

    threading.Thread(target=handle_client, args=[client_sock]).start()
    print('1111')
    time.sleep(2)

    print(client_sock.is_connected)
    #client_sock.disconnect()
    print('2222 conn')
    client_sock2 = SocketUtil.ClientSocket()
    client_sock2.connect('127.0.0.1', 6011, ssl_mode=True)
    print('2222 connend')
    print(client_sock2.is_connected)
    print(client_sock2.is_connected)

    threading.Thread(target=handle_client2, args=[client_sock2]).start()

    time.sleep(1)
    print(client_sock2.is_connected)

    input()


def connect(sock, port):
    #sock.connect('test09-v3.dev.kambi.com', port, ssl_mode=True)
    sock.connect('localhost', port, ssl_mode=True)
    print('Connected to {}'.format(port))
    return sock


def handle_send(sock, msg):
    print('Handling send...')
    #while True:
    sock.send(msg)
    print('Message sent: {}'.format(msg.replace('\r\n', '^')))
    time.sleep(1)
    msg = 'clientreq\r\n'
    sock.send(msg)
    print('Message sent: {}'.format(msg.replace('\r\n', '^')))
    time.sleep(1)
    msg = 'clientreq2\r\n'
    sock.send(msg)
    print('Message sent: {}'.format(msg.replace('\r\n', '^')))


def handle_recv(sock, log):
    print('Handling recv...')
    while True:
        msg = sock.receive()
        print('{} {}'.format(log, msg.replace('\r\n', '^')))
        time.sleep(1)


print('CLIENT started.')
eventsClientSock = SocketUtil.ClientSocket()
#matchlistClientSock = SocketUtil.ClientSocket()

eventsClientSock = connect(eventsClientSock, 8010)
#matchlistClientSock = connect(matchlistClientSock, 8011)

threading.Thread(target=handle_send, args=[eventsClientSock, '<match matchid="944423" feedtype="full" includeavailable="yes"/>\r\n']).start()
threading.Thread(target=handle_recv, args=[eventsClientSock, 'EVENTS received: ']).start()
#threading.Thread(target=handle_send, args=[matchlistClientSock, '<match matchid="944423" feedtype="full" includeavailable="yes"/>\r\n']).start()
#threading.Thread(target=handle_recv, args=[matchlistClientSock, 'MATCHLIST received: ']).start()

print('CLIENT Waiting..')
input()
print('CLIENT Ended.')
