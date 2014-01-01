#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 KuoE0 <kuoe0.tw@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import serial
import signal
import sys
import json
import os

tornado_port = 8888

# create serial object
serial_port = sys.argv[1]
serial_baudrate = int(sys.argv[2])
ser = serial.Serial(serial_port, serial_baudrate, timeout=1)

# global variable
client = list() # list of websocket client
number_of_signal = 200
serial_pending = list()
signal_set = [[0] * 6] * number_of_signal
signal_type = ['x-acc', 'y-acc', 'z-acc', 'x-gyro', 'y-gyro', 'z-gyro']

# SIGINT handler to close serial connection
def handler_SIGINT(signum, frame):
    global ser
    print "Signal {0} happened!".format(signum)
    print "Serial connection closed..."
    ser.close()
    sys.exit()

signal.signal(signal.SIGINT, handler_SIGINT)

# receive signal with a non-blocking way
def recieve_signal():

    data = ""
    try:
        if ser.inWaiting() != 0:
            data = ser.readline()
            print data
    except Exception as e:
        error_msg = "Error reading from {0}".format(serial_port)
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)

        print error_msg, message

    return data

# parse out the signal value
def parse_pending(signal_string):

    if len(signal_string) == 0:
        return

    global signal_set

    try:
    # split by ',' and get first element
        values = [int(x) for x in signal_string.split(',')]
    except:
        values = None

    # push signal into list
    if values and len(values) == 6:
        signal_set.append(values)

# push signal data to client
def signal_tx():
    parse_pending(recieve_signal())
    ret_signal = signal_set[:min(number_of_signal, len(signal_set))]
    if len(signal_set):
        signal_set.pop(0)

    # fill the signal
    if len(ret_signal) < number_of_signal:
        ret_signal.extend([[0] * 6] * (number_of_signal - len(ret_signal)))
    # transpose the list
    ret_signal = zip(*ret_signal)

    ret = list()
    for i in xrange(6):
        ret.append({ 'data': [p for p in enumerate(ret_signal[i])], 'label': signal_type[i] })
    ret = json.dumps({ 'signal': ret })
    
    for cl in client:
        cl.write_message(ret)

# tornado websocket handler
class socket_handler(tornado.websocket.WebSocketHandler):
    def open(self):
        client.append(self)
    def on_close(self):
        client.remove(self)

class homepage_handler(tornado.web.RequestHandler):
    def get(self):
        self.render('template/index.html')

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
}

application = tornado.web.Application([
    (r'/', homepage_handler),
    (r'/ws', socket_handler),
    ], **settings)

if __name__ == "__main__":
    #tell tornado to run signal_tx every 1 ms
    serial_loop = tornado.ioloop.PeriodicCallback(signal_tx, 1)
    serial_loop.start()

    application.listen(tornado_port)
    print "Starting server on port number {0}...".format(tornado_port)
    print "Open at http://localhost:{0}/".format(tornado_port)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print 'Server closed...'