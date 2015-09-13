#!/usr/bin/python

__author__ = 'arifal'


# Betradar Dispatcher
#
# Prerequisites:
#     Python 3.4 (due to ssl.create_default_context() method)
#
# Run using 'python3 betradar-dispatcher.py'


import time
import threading
import logging
import sys
import SocketUtil

from Channel import Channel
from BetradarMessage import BetradarMessage
from UserCommand import UserCommand
from MessageRelayer import MessageRelayer


USER_COMMAND_PORT = 7002
EVENTS_PORT, MATCHLIST_PORT = 8010, 8011
PROVIDER_HOST, PROVIDER_PWD = 'scouttest.betradar.com', 2047
#PROVIDER_HOST, PROVIDER_PWD = 'localhost', 2047
LOG_FILE = 'dispatcher.log'
USE_BOOKED_MATCH_IDS = True
BOOKED_MATCH_IDS = '7714164,7714586,7714590,7720410,7720852,7733856,7733858,7733866,7733868,7733870,7733872,7733874' \
                   ',7733876,7733882,7734046,7734048,7734050,7734052,7734054,7734056,7734058,7734060,7734062,7734064' \
                   ',7734066,7734078,7734116,7734118,7734120,7734124,7734126,7734128,7734132,7734136,7734138,7734140' \
                   ',7734142,7734144,7734146,7734148,7734150,7734152,7734154,7734156,7734164,7734166,7734168,7734170' \
                   ',7734172,7734174,7734176,7734178,7734180,7734182,7734184,7734186,7734188,7734190,7734192,7734712' \
                   ',7734714,7734716,7734718,7734720,7734722,7734724,7734726,7734728,7734736,7734738,7734740,7734742' \
                   ',7734744,7734746,7734748,7734758,7734760,7734762,7734764,7734766,7734768,7734770,7734772,7734774' \
                   ',7734778,7734782,7734784,7734786,7734788,7734794,7734814,7734816,7734818,7734820,7734822,7734824' \
                   ',7734826,7734828,7734844,7734846,7734858,7734864,7734872,7734878,7734884,7734914,7734920,7734922' \
                   ',7734928,7734930,7734932,7734934,7734950,7734954,7734956,7734958,7734960,7734982,7734984,7734986' \
                   ',7734988,7734992,7735016,7735482,7735490,7735492,7735494,7735496,7735498,7735500,7735502,7735504' \
                   ',7735506,7735508,7735514,7735516,7735518,7735524,7735530,7735532,7735534,7735548,7735560,7735562' \
                   ',7735564,7735566,7735568,7735570,7735572,7735574,7735576,7735580,7735582,7735584,7735586,7735588' \
                   ',7735622,7735624,7735626,7735628,7735630,7735632,7735634,7735636,7735640,7735646,7735648,7735650' \
                   ',7735652,7735654,7735656,7735658,7735660,7735662,7735664,7735666,7735674,7735676,7735678,7735680' \
                   ',7735696,7735698,7735700,7735702,7735704,7735706,7735708,7735710,7735712,7735734,7735740,7735742' \
                   ',7735764,7735766,7735768,7735770,7735772,7735778,7735780,7735782,7735784,7737788,7737790,7737792' \
                   ',7737868,7737948,7737952,7737998,7738002,7738012,7739920,7740134,7740150,7741686,7741758'.split(',')


class BetradarDispatcher:

    USER_COMMAND = 'user_command'
    EVENTS = 'events'
    MATCHLIST = 'matchlist'

    _channels = {
        USER_COMMAND : Channel("UserCommands", USER_COMMAND_PORT)
        , EVENTS : Channel("Events", EVENTS_PORT)
        , MATCHLIST : Channel("Matchlist", MATCHLIST_PORT)
    }

    def __init__(self):
        self._user_command_sock = SocketUtil.ServerSocket(USER_COMMAND_PORT, ssl_mode=False)
        self._events_sock = SocketUtil.ServerSocket(EVENTS_PORT, ssl_mode=True)
        self._matchlist_sock = SocketUtil.ServerSocket(MATCHLIST_PORT, ssl_mode=True)
        self._user_commands = []
        self._message_relayers = []
        self._stop = False

    def start(self):
        logging.info('Started.')
        logging.info('# Type \'exit\' to stop.')
        self._listen_to_ports()
        self._start_accepting_connections()

        try:
            while not self._stop:
                time.sleep(0.3)
        except KeyboardInterrupt:
            pass
        finally:
            logging.info('Exiting...')
            self.stop()

    def stop(self):
        self._stop = True
        self._stop_listeners()
        self._stop_user_commands()
        self._stop_message_relayers()

    def _listen_to_ports(self):
        self._user_command_sock.listen()
        self._events_sock.listen()
        self._matchlist_sock.listen()

    def _start_accepting_connections(self):
        threading.Thread(target=self._wait_for_connections, args=[self._user_command_sock, self._channels[self.USER_COMMAND]]).start()
        threading.Thread(target=self._wait_for_connections, args=[self._events_sock, self._channels[self.EVENTS]]).start()
        threading.Thread(target=self._wait_for_connections, args=[self._matchlist_sock, self._channels[self.MATCHLIST]]).start()

    def _wait_for_connections(self, server_sock, channel):
        logging.info('Listening for {} connections on port {}...'.format(channel.get_name, channel.get_port))
        while not self._stop:
            try:
                sock = server_sock.accept()
                name = '{}:{}'.format(sock.get_addr[0], sock.get_addr[1])
                logging.info('Accepted new {} connection from {}.'.format(channel.get_name, channel.get_port))

                if channel.get_name in [self.EVENTS, self.MATCHLIST]:
                    threading.Thread(target=self._handle_new_connection, args=[sock, name]).start()
                else:
                    user_command = UserCommand(self, sock)
                    self._user_commands.append(user_command)
                    threading.Thread(target=user_command.start).start()
            except Exception as e:
                logging.error('Unable to listen to port {} - {}'.format(channel.get_port, e))

        logging.info('Listener for {} connections has stopped.'.format(channel.get_name))

    def _handle_new_connection(self, sock, name):
        logging.info('{} - Connecting to provider {}:{}...'.format(name, PROVIDER_HOST, PROVIDER_PWD))

        prov_sock = SocketUtil.ClientSocket(host=PROVIDER_HOST, port=PROVIDER_PWD, ssl_mode=sock.get_ssl_mode())
        try:
            prov_sock.connect()
        except Exception as e:
            logging.error('{} - Unable to connect to provider - {}'.format(name, e))
            return

        client_to_provider_msg_relayer = MessageRelayer(sock, prov_sock, BetradarMessage.NEWLINE, '{}_to_prov'.format(name), False, USE_BOOKED_MATCH_IDS, BOOKED_MATCH_IDS)
        provider_to_client_msg_relayer = MessageRelayer(prov_sock, sock, BetradarMessage.DELIMITER, '{}_fr_prov'.format(name), True, USE_BOOKED_MATCH_IDS, BOOKED_MATCH_IDS)

        self._message_relayers.append(client_to_provider_msg_relayer)
        self._message_relayers.append(provider_to_client_msg_relayer)

        threading.Thread(target=client_to_provider_msg_relayer.start).start()
        threading.Thread(target=provider_to_client_msg_relayer.start).start()

    def _stop_user_commands(self):
        for uc in self._user_commands:
            uc.stop()

    def _stop_message_relayers(self):
        for mr in self._message_relayers:
            mr.stop()

    def _stop_listeners(self):
        self._user_command_sock.close()
        self._events_sock.close()
        self._matchlist_sock.close()


def main():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s | %(message)s'))

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ch)

    betradar_dispatcher = BetradarDispatcher()
    betradar_dispatcher.start()


if __name__ == '__main__':
    main()
