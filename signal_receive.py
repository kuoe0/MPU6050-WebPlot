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
import serial
import signal
import sys
import json

tornado_port = 8888

# create serial object
serial_port = sys.argv[1]
serial_baudrate = int(sys.argv[2])
ser = serial.Serial(serial_port, serial_baudrate, timeout=1)

# global variable
number_of_signal = 200
serial_pending = list()
signals = [[0] * 6] * number_of_signal
signal_type = ['x-acc', 'y-acc', 'z-acc', 'x-gyro', 'y-gyro', 'z-gyro']

# SIGINT handler to close serial connection
def handler_SIGINT(signum, frame):
    global ser
    print "Signal {0} happened!".format(signum)
    print "Serial connection closed..."
    ser.close()

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

    if len(data):
        parse_pending(data)

# parse out the signal value
def parse_pending(signal_string):

    global signals

    try:
    # split by ',' and get first element
        values = [int(x) for x in signal_string.split(',')]
    except:
        values = None

    # push signal into list
    if values and len(values) == 6:
        signals.append(values)

# tornado web handler
class query_signal_handler(tornado.web.RequestHandler):

    def get(self, url='/'):
        print 'get'
        # get the name of callback parameter
        callback_func = self.get_argument('callback')
        self.handle_request(callback_func)
    
    # return signals
    def handle_request(self, callback):
        global signals
        global number_of_signal
        # retrieve signal needed
        ret_signals = signals[:min(number_of_signal, len(signals))]
        # fill the signal
        if len(ret_signals) < number_of_signal:
            ret_signals.extend([[0] * 6] * (number_of_signal - len(ret_signals)))
        # transpose the list
        ret_signals = zip(*ret_signals)

        # create list of dict
        ret = list()
        for i in xrange(6):
            ret.append({ 'data': [p for p in enumerate(ret_signals[i])], 'label': signal_type[i] })

        # convert to JSON format
        ret = json.dumps({'data': ret})
        # convert to JSONP format
        ret = '{0}({1})'.format(callback, ret)
        # set content type
        self.set_header("Content-Type", "application/json")
        # write data
        self.write(ret)

        if len(signals) != 0:
            # remove first element to realtime plot
            signals.pop(0)


application = tornado.web.Application([(r"/", query_signal_handler),])

if __name__ == "__main__":

    #tell tornado to run checkSerial every 50 ms
    serial_loop = tornado.ioloop.PeriodicCallback(recieve_signal, 1)
    serial_loop.start()

    application.listen(tornado_port)
    print "Starting server on port number {0}...".format(tornado_port)
    print "Open at http://localhost:{0}/".format(tornado_port)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print 'Server closed...'
