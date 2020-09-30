#!/usr/bin/env python
import threading
import roslib
import rospy
import time

from geometry_msgs.msg import Twist

import sys, select, termios, tty
import time
import subprocess
from std_msgs.msg import Float32MultiArray
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json

direction = "stop"
msg = ""
speed = .2
turn = 1

class EchoServer(WebSocket):

    def handleMessage(self):
	global direction

    	if self.data == "up":
            direction = "up"
  	    print "go up"

    	elif self.data == "left":
            direction = "left"
    	    print "go left"

    	elif self.data == "right":
            direction = "right"
            print "go right"
        else:
            direction = "stop"
    	    print "stop"

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


def listener():
    print "init listener"
    server = SimpleWebSocketServer('', 9200, EchoServer)
    server.serveforever()

def control():
    x = 0
    th = 0
    status = 0
    count = 0
    acc = 0.1
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0
    #rospy.init_node('covea_teleop')
    pub = rospy.Publisher('cmd_vel', Twist)
    print "init control"    

    try:

        while(1):
            global direction
	    print direction

            if direction == "up":
                print "going up"
                x = 1
                th = 0
            elif direction == "left":
                print "going left"
                x = 0
                th = -1
            elif direction == "right":
                print "going right"
                x = 0
                th = 1
            else:
                print "stop"
                x = 0
                th = 0

            target_speed = speed * x
            target_turn = turn * th
            if target_speed > control_speed:
                control_speed = min( target_speed, control_speed + 0.02 )
            elif target_speed < control_speed:
                control_speed = max( target_speed, control_speed - 0.02 )
            else:
                control_speed = target_speed
            if target_turn > control_turn:
                control_turn = min( target_turn, control_turn + 0.1 )
            elif target_turn < control_turn:
                control_turn = max( target_turn, control_turn - 0.1 )
            else:
                control_turn = target_turn

            #time.sleep(2)

            '''twist = Twist()
            twist.linear.x = control_speed; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = control_turn
            pub.publish(twist)'''


    except:
        print e

    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        pub.publish(twist)



controlThread = threading.Thread(target=control)
controlThread.start()

listenThread = threading.Thread(target=listener)
listenThread.start()
