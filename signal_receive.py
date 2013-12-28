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

    split_lines = serial_pending.split()
    serial_pending = split_lines[-1]
    split_lines = split_lines[:-1]

    for lines in split_lines:
        values = lines.split(',')[0]
        if values:
            signals.append(int(values))

class query_signal_handler(tornado.web.RequestHandler):

    def get(self, url='/'):
        print 'get'
        self.handle_request()
    
    def handle_request(self):
        global signals
        self.number_of_signal = 300
        ret = json.dumps({'data': [list(s) for s in enumerate(signals[:self.number_of_signal])]})
        self.write(ret)
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
