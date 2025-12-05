# -*- coding: utf-8 -*-
import os
import sys,getopt
import threading
import Thread
from ui_server import Ui_server
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow
#from PyQt5.QtGui import *
from server import Server
import uvicorn
from rest_api import app, set_server

class MyWindow(QMainWindow,Ui_server):
    def __init__(self):
        self.user_ui=True
        self.start_tcp=False
        self.server=Server()
        self.rest_api_thread=None
        self.parseOpt()
        # Initialize REST API server
        set_server(self.server)
        self.start_rest_api()
        if self.user_ui:
            self.app = QApplication(sys.argv)
            super(MyWindow,self).__init__()
            self.setupUi(self)
            self.pushButton_On_And_Off.clicked.connect(self.on_and_off_server)
            self.on_and_off_server()
        if self.start_tcp:
            self.server.start_server()
            self.server.tcp_flag=True
            self.video=threading.Thread(target=self.server.transmit_video)
            self.video.start()
            self.instruction=threading.Thread(target=self.server.receive_commands)
            self.instruction.start()
            if self.user_ui:
                self.pushButton_On_And_Off.setText('Off')
                self.states.setText('On')
    
    def start_rest_api(self):
        """Start REST API server in a separate thread"""
        def run_api():
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        self.rest_api_thread = threading.Thread(target=run_api, daemon=True)
        self.rest_api_thread.start()
        print("REST API server started on http://0.0.0.0:8000")

    def parseOpt(self):
        self.opts,self.args = getopt.getopt(sys.argv[1:],"tn")
        for o,a in self.opts:
            if o in ('-t'):
                print ("Open TCP")
                self.start_tcp=True
            elif o in ('-n'):
                self.user_ui=False
                
    def on_and_off_server(self):
        if self.pushButton_On_And_Off.text() == 'On':
            self.pushButton_On_And_Off.setText('Off')
            self.states.setText('On')
            self.server.start_server()
            self.server.tcp_flag=True
            self.video=threading.Thread(target=self.server.transmit_video)
            self.video.start()
            self.instruction=threading.Thread(target=self.server.receive_commands)
            self.instruction.start()
        else:
            self.pushButton_On_And_Off.setText('On')
            self.states.setText('Off')
            self.server.tcp_flag=False
            try:
                Thread.stop_thread(self.video)
                Thread.stop_thread(self.instruction)
            except Exception as e:
                print(e)
            self.server.stop_server()
            print("close")
    def closeEvent(self,event):
        try:
            Thread.stop_thread(self.video)
            Thread.stop_thread(self.instruction)
        except:
            pass
        try:
            if hasattr(self.server, 'video_socket'):
                self.server.video_socket.close()
            if hasattr(self.server, 'command_socket'):
                self.server.command_socket.close()
            self.server.stop_server()
        except:
            pass
        if self.user_ui:
            QCoreApplication.instance().quit()
        os._exit(0)
        
if __name__ == '__main__':
    try:
        myshow=MyWindow()
        if myshow.user_ui==True:
            myshow.show();   
            sys.exit(myshow.app.exec_())
        else:
            try:
                pass
            except KeyboardInterrupt:
                myshow.close()
        while True:
            pass
    except KeyboardInterrupt:
            myshow.close()
