import traceback
import threading
import time

#import Logger
import SocketUtil


#log = Logger.Logger('Server')


def main(port):
    print(server_sock.is_listening)
    try:
        server_sock.listen(port)
        log.info('Listening to {}...'.format(server_sock.port))
    except Exception as e:
        print (e)
        traceback.print_exc()
        pass

    print(server_sock.is_listening)
    server_sock.set_port = 2000


def main2():
    log.info('Started.')
    #threading.Thread(target=main, args=[6010]).start()
    main(6010)
    threading.Thread(target=accept).start()
    print('Sleeping')
    time.sleep(2)
    print('Slept!')
    #log.info('Listening to {}...'.format(sock.port))
    #sock.listen(6012)
    print('Closing...')
    #sock.close()
    print('Closed!')
    print(server_sock.is_listening)
    time.sleep(2)
    server_sock.listen(6030)
    log.info('Listening to {}...'.format(server_sock.port))
    print(server_sock.is_listening)
    input()
    close()
    log.info('Stopped.')


def close():
    server_sock.close()


def accept():
    print('Accepting...')
    server_sock.accept()
    print('Accepting interrupted.')


def handle_client():
    client_sock = SocketUtil.ClientSocket(*server_sock.accept())
    while True:
        for i in range(1, 5):
            client_sock.send('Message from S')
            log.info('Message from client: {}'.format(client_sock.receive()))

def handle_client2():
    client_sock2 = SocketUtil.ClientSocket(*server_sock2.accept())
    while True:
        for i in range(1, 5):
            client_sock2.send('Message from S')
            log.info('Message from client: {}'.format(client_sock2.receive()))

def x4():
    server_sock = SocketUtil.ServerSocket(ssl_mode=True)
    server_sock.listen(6010)
    server_sock2 = SocketUtil.ServerSocket(ssl_mode=True)
    server_sock2.listen(6011)
    x = 0
    while True:
        threading.Thread(target=handle_client).start()
        threading.Thread(target=handle_client2).start()
        time.sleep(5)
        server_sock.close()

        if x == 0:
            #server_sock.listen(6011)
            x = 1
        break

    input()


def handle_send(sock):
    print('Handling send...')
    #while True:
    msg = '<matchlist>\r\n' \
        '<match booked="0" coveredfrom="venue" extrainfo="0" matchid="7751982" start="1439001900000" t1id="7415814" t1name="MORIZONO M / OSHIMA Y" t2id="8046669" t2name="FANG B / ZHU L">\r\n' \
        '<status id="94" name="WALKOVER2" start="1439001793149"/>\r\n' \
        '<score t1="0" t2="0" type="match"/>\r\n' \
        '<tournament id="46205" name="World Tour, China Open (SS) 2015, Doubles"/>\r\n' \
        '<category id="88" name="International"/>\r\n' \
        '<sport id="20" name="Table tennis"/>\r\n' \
        '</match>\r\n' \
        '<match booked="0" coveredfrom="venue" extrainfo="0" matchid="7751984" start="1439001900000" t1id="6693003" t1name="CHIANG H-C / HUANG S-S" t2id="7746165" t2name="MA L / ZHANG J">\r\n' \
        '<status id="100" name="ENDED" start="1439003069716"/>\r\n' \
        '<score t1="0" t2="3" type="match"/>\r\n' \
        '<tournament id="46205" name="World Tour, China Open (SS) 2015, Doubles"/>\r\n' \
        '<category id="88" name="International"/>\r\n' \
        '<sport id="20" name="Table tennis"/>\r\n' \
        '</match>\r\n' \
        '</matchlist>\r\n' \
        '\r\n'

    sock.send(msg)
    print('Message sent: {}'.format(msg.replace('\r\n', '^')))
    time.sleep(1)
    msg = 'loginresponse\r\n\r\n'
    sock.send(msg)
    print('Message sent: {}'.format(msg.replace('\r\n', '^')))
    time.sleep(1)
    msg = 'loginresponse2\r\n\r\n'
    sock.send(msg)
    print('Message sent: {}'.format(msg.replace('\r\n', '^')))


def handle_recv(sock):
    print('Handling recv...')
    while True:
        print('Received dispatcher message: {}'.format(sock.receive().replace('\r\n', '^')))
        time.sleep(1)


print('MOCK Started.')
sock = SocketUtil.ServerSocket(port=2047, ssl_mode=True)
sock.listen()
while True:
    client_sock = sock.accept()
    print('Accepted new connection: {}'.format(client_sock.get_addr))
    threading.Thread(target=handle_send, args=[client_sock]).start()
    threading.Thread(target=handle_recv, args=[client_sock]).start()
print('MOCK Ended.')
