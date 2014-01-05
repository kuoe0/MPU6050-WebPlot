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
import copy

tornado_port = 8888

# create serial object
serial_port = sys.argv[1]
serial_baudrate = int(sys.argv[2])
callback_timeout = int(sys.argv[3])
ser = serial.Serial(serial_port, serial_baudrate, timeout=1)

# global variable
client = list() # list of websocket client
number_of_signal = 200
serial_pending = list()
tx_status = False
level_moving_average = 0
signal_set = [[0] * 6] * number_of_signal
last_signal_set = [[0] * 6] * number_of_signal
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

def moving_average_filter(last_signal, signal, level):
    
    signal = ([0] * (level - len(last_signal))) + list(last_signal) + list(signal)
    ret = [float(sum(signal[idx:idx + level])) / level for idx in xrange(len(signal) - level + 1)]
    return ret

def make_init_data():
    
    ret_signal = [[0] * 6] * number_of_signal
    ret_signal = zip(*ret_signal)

    ret = list()
    for label in signal_type:
        ret.append({ 'data': [p for p in enumerate([0] * number_of_signal)], 'label': label })
    ret = json.dumps({ 'signal': ret })

    return ret


def make_data():

    global signal_set
    global signal_type
    global last_signal_set
    global number_of_signal
    global level_moving_average

    # take out the signal to return
    signals = signal_set[:min(number_of_signal, len(signal_set))]
    last_signals = last_signal_set[-(min(level_moving_average, len(last_signal_set))):]

    # fill the signal
    if len(signals) < number_of_signal:
        signals.extend([[0] * 6] * (number_of_signal - len(signals)))

    # transpose signals to make the signal of same type in same list
    signals = zip(*signals)
    last_signals = zip(*last_signals)

    ret = list()

    for i in xrange(6):
        if level_moving_average != 0:
            signals[i] = moving_average_filter(last_signals[i], signals[i], level_moving_average)
        ret.append({ 'data': [p for p in enumerate(signals[i])], 'label': signal_type[i] })
    ret = json.dumps({ 'signal': ret })
    return ret

# push signal data to client
def signal_tx():

    global tx_status
    global number_of_signal
    global signal_set
    global last_signal_set

    parse_pending(recieve_signal())

    if not tx_status:
        return
    
    # pop out the transmitted signal
    if len(signal_set):
        last_signal_set.append(signal_set.pop(0))
        last_signal_set = last_signal_set[-number_of_signal:]

    ret = make_data()
    for cl in client:
        cl.write_message(ret)


# tornado websocket handler
class socket_handler(tornado.websocket.WebSocketHandler):
    def open(self):
        client.append(self)
        self.write_message(make_init_data())

    def on_message(self, message):
        global tx_status
        global signal_set
        global toggle_moving_average_filter
        global level_moving_average

        token = message.split()

        if token[0] == "play":
            tx_status = True
        elif token[0] == "pause":
            tx_status = False
        elif token[0] == "clear":
            signal_set = [[0] * 6] * number_of_signal
            self.write_message(make_init_data())
        elif token[0] == "MAF":
            level_moving_average = int(token[1])
            self.write_message(make_data())

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
    serial_loop = tornado.ioloop.PeriodicCallback(signal_tx, callback_timeout)
    serial_loop.start()

    application.listen(tornado_port)
    print "Starting server on port number {0}...".format(tornado_port)
    print "Open at http://localhost:{0}/".format(tornado_port)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print 'Server closed...'
