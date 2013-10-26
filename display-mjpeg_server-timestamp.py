#!/usr/bin/env python
# coding: utf-8

'''
Software License Agreement (BSD License)

Copyright (c) 2013, Yota Ichino
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided
   with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

import time
import socket
from urlparse import urlparse
from datetime import datetime
from optparse import OptionParser

def create_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    return client

def receive_line(client):
    ret = ''
    while True:
        c = client.recv(1)
        if c == '\r':
            client.recv(1) # for avoiding '\n'
            break
        ret += c
    return ret

def parse_a_header(header_line):
    return header_line.split(': ')

def main():
    USAGE = 'usage: %prog --url=[URL]'
    parser = OptionParser(USAGE)
    parser.add_option('-U', '--url', dest='url', help='mjepg_server URL',
                      metavar='URL')
    (options, args) = parser.parse_args()
    if options.url is None:
        parser.error('mjpeg_server URL was not specified')

    url = urlparse(options.url)
    client = create_client(url.hostname, url.port)

    # request header
    client.send('GET %s?%s HTTP/1.0 \r\n\r\n' % (url.path, url.query))

    print 'now, mjpeg_server, delay'
    while True:
        line = receive_line(client)
        if line.startswith('--boundarydonotcross'):
            now = time.time()

            line = receive_line(client)
            assert line.startswith('Content-Type: ')

            line = receive_line(client)
            assert line.startswith('Content-Length: ')
            h = parse_a_header(line)
            content_length = int(h[1])

            line = receive_line(client)
            assert line.startswith('X-Timestamp: ')
            h = parse_a_header(line)
            mjpeg_server_timestamp = float(h[1])

            line = receive_line(client)
            assert line.startswith('')

            img4dummy = client.recv(content_length)
            # uncomment the below a line for saving img4dummy as JPEG image.
            # open('dummy.jpg', 'wb').write(img4dummy)

            print '%f, %f, %f' %(now, mjpeg_server_timestamp,
                                 now - mjpeg_server_timestamp)


if __name__ == '__main__':
    main()
