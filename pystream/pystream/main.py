# -*- coding: utf-8 -*-
import os, sys, subprocess, threading, time, random
import socketserver, http.server
from queue import Queue, Empty
import urllib

class FFMpeg:
    def __init__(self, addr):
        self.addr = addr
        self.fragSize = 8192
        self.opts = None
        self.buffer = Queue()
        self.__STOPNOW__ = False

    def __del__(self):
        if(self.status == 'running'):
            self.stop()

    def start(self):
        self.opts = ['ffmpeg.exe', '-i', self.addr, '-acodec', 'copy', '-vcodec', 'copy', '-frag_size', str(self.fragSize), '-f', 'mpegts', '-']
        nullDev = open(os.devnull, 'wb')
        self.ffmpeg = subprocess.Popen(self.opts, stdout=subprocess.PIPE, stderr=nullDev)
        self.ffmpegThread = threading.Thread(target = self.fillBuffer, args=[])
        self.ffmpegThread.start()

    def stop(self, stopFlag = True):
        if(self.opts is None):
            raise RuntimeError('Already stopped.')
        if(not self.__STOPNOW__):
            self.__STOPNOW__ = stopFlag
            while(self.__STOPNOW__):
                pass
            if(self.ffmpeg.poll() is None):
                self.ffmpeg.kill()
            self.ffmpegThread = None
            self.ffmpeg = None
            self.opts = None
            self.buffer = Queue()

    def status(self):
        if(self.opts is None):
            return 'stopped'
        else:
            return 'running'

    def fillBuffer(self):
        while(self.__STOPNOW__ == False and self.ffmpeg.poll() is None):
            data = self.ffmpeg.stdout.read(self.fragSize)
            self.buffer.put(data)
        self.stop(stopFlag = False)
        self.__STOPNOW__ = False

    def getData(self):
        return self.buffer.get(True, 10)

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('/')
        path.remove('')
        if(len(path) == 0):
            self.send_response(404)
            self.end_headers()
        elif(len(path) == 1):
            self.send_response(404)
            self.end_headers()
        elif(len(path) == 2):
            if(path[0] == 'rtp'):
                addr = 'rtp://%s' % (path[1])
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            ffmpeg = FFMpeg(addr)
            ffmpeg.start()
            while((not self.server.stop) and ffmpeg.status() == 'running'):
                try:
                    data = ffmpeg.getData()
                except Empty:
                    break
                try:
                    self.wfile.write(data)
                except ConnectionResetError:
                    break
                except ConnectionAbortedError:
                    break
            if(ffmpeg.status() == 'running'):
                ffmpeg.stop()
            print("Connection Reset.", file=sys.stderr)

class Server:
    def __init__(self, port):
        self.port = port
        self.httpd = None

    def start(self):
        self.httpd = socketserver.ThreadingTCPServer(('192.168.1.4', self.port), Proxy)
        self.httpd.stop = False
        threading.Thread(target=self.httpd.serve_forever).start()
        print("HTTP server started at port {0}".format(self.port))

    def stop(self):
        if self.httpd:
            self.httpd.stop = True
            self.httpd.shutdown()
            print("HTTP server stopped")

if __name__ == '__main__':
    s = Server(8090)
    s.start()
