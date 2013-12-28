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
import sys
import json

tornado_port = 8888

# create serial object
serial_port = sys.argv[1]
serial_baudrate = int(sys.argv[2])
ser = serial.Serial(serial_port, serial_baudrate)

# global variable
serial_pending = ""
signals = list()

# receive signal with a non-blocking way
def recieve_signal():
    try:
        data = ser.read(ser.inWaiting())
    except:
        print "Error reading from {0}".format(serial_port)

    if len(data):
        global serial_pending
        serial_pending = serial_pending + data
        parse_pending()

# parse out the signal value
def parse_pending():
    global serial_pending
    global signals

    # parse by newline
    split_lines = serial_pending.split()
    # the last element maybe incomplete, so leave it to pending string
    serial_pending = split_lines[-1]
    # remove the last element
    split_lines = split_lines[:-1]

    for lines in split_lines:
        # split by ',' and get first element
        values = lines.split(',')[0]

        # push signal into list
        if values:
            signals.append(int(values))

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
        # number of signals
        self.number_of_signal = 300
        # zip and convert to JSON format
        ret = json.dumps({'data': [list(s) for s in enumerate(signals[:self.number_of_signal])]})
        # convert to JSONP format
        ret = '{0}({1})'.format(callback, ret)
        # set content type
        self.set_header("Content-Type", "application/json")
        # write data
        self.write(ret)
        # remove first element to realtime plot
        signals.pop(0)


application = tornado.web.Application([(r"/", query_signal_handler),])

if __name__ == "__main__":

    #tell tornado to run checkSerial every 10ms
    serial_loop = tornado.ioloop.PeriodicCallback(recieve_signal, 10)
    serial_loop.start()

    application.listen(tornado_port)
    print "Starting server on port number {0}...".format(tornado_port)
    print "Open at http://localhost:{0}/".format(tornado_port)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print 'Server closed...'
