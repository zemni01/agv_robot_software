#!/usr/bin/env python
import rospy
import os
import time
from std_msgs.msg import Bool
from std_msgs.msg import String
from roboteq_msgs.msg import Feedback
import subprocess

# Simple command
#em_stop = False

def listener():

  time.sleep(6)
  
  while(1):
    feedback = False
    pub_emergency_stop = rospy.Publisher('/emergency_stop', Bool, queue_size=10)
#    verif= subprocess.check_output(['rosnode ping -c1 /roboteq_driver | grep reply | wc -l'], shell=True)
#    verif2 = 0
    try:
    	msg = rospy.wait_for_message('/right/feedback', Feedback, 1.2)
	feedback = True
    except:
	print "no feedback received" 
    #print "verif = "+ str(verif)
    if feedback:
	pub_emergency_stop.publish(False) 
	print "node is running..."
	time.sleep(2)

    else:
	pub_emergency_stop.publish(True)
	os.system("rosnode kill /roboteq_driver")
	os.system("rosnode kill /roboteq_drive")
	print "no reply, node has crashed"
	time.sleep(4)

	



if __name__ == '__main__':
    rospy.init_node("emergency_stop")
    listener()
    rospy.spin()
