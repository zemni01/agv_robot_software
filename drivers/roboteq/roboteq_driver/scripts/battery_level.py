import time
import rospy
import datetime
import math
from roboteq_msgs.msg import Command, Feedback
from std_msgs.msg import Bool, Float32, Int8
from geometry_msgs.msg import Twist

class Battery:
    def __init__(self):
    	rospy.Subscriber("/right/feedback", Feedback, self.MotorsCallback)
    	rospy.Subscriber("/emergency_stop", Bool, self.Em_Stop_Callback)
    	rospy.Subscriber("/cmd_vel", Twist, self.cmd_vel_Callback)
    	self.pub_voltage = rospy.Publisher('/voltage', Float32, queue_size=10)
    	self.pub_level = rospy.Publisher('/voltage_level1', Float32, queue_size=10)
    	self.pub_state = rospy.Publisher('/charge_state', Bool, queue_size=10)
    	self.Q_Bat = 12
    	self.I_PC = 4
    	self.I_leds = 1.75
    	self.I_Motors_max = 0.8
    	self.I_Motors = 0.0
	self.I_charger = 4
    	self.V_charge = 14.1
    	self.V_discharge = 10
    	self.t_PC = self.Q_Bat/self.I_PC
    	self.t_Motors_min = self.Q_Bat/self.I_Motors_max 
	self.t_Motors = self.t_Motors_min
    	self.t_leds = self.Q_Bat/self.I_leds
    	self.t_without_teleop = self.Q_Bat/(self.I_leds+self.I_PC)
	self.t_charger = self.Q_Bat/self.I_charger*3600
	self.charge_state = False
    	self.current_voltage = 0.0
    	self.last_voltage = 0.0
	self.voltage = 0.0 
	bat_level = open("/home/covealink2/catkin_ws/src/drivers/roboteq/roboteq_driver/battery_data/battery.txt", "r") 
        try:
		lines = bat_level.readlines()
		self.bat_last_level = float(lines[0])
		self.voltage_off = float(lines[1])
	except:
		print ("File is empty or does not contain all teh required data")
		try:
			msg = rospy.wait_for_message("/right/feedback",Feedback, 5.0)
                        self.voltage_off = msg.supply_voltage
                        self.bat_last_level = (self.voltage_off - self.V_discharge) *100/ (self.V_charge - self.V_discharge)
		except:
			print ("Couldn't get voltage value!!")
		        self.bat_last_level = 100.
		        self.voltage_off = 14.

	self.discharge_percent = int(self.bat_last_level)
	self.t_start_robot = datetime.datetime.now()
	self.time_cap = self.t_start_robot
	self.cptr = 0
	self.charge_verif = 0.0
	self.verif = False
	self.change_status = False
	self.Em_Stop = False
	self.cmd_vel_angular = 0.0
    	self.cmd_vel_linear = 0.0
	#self.t_off = self.t_start_robot - self.t_last_shutdown
	
    def MotorsCallback(self,feedback):


    	self.I_Motors = feedback.motor_current 
    	self.voltage = feedback.supply_voltage
    	self.pub_voltage.publish(self.voltage)
	self.current_voltage = self.voltage
	
    def Em_Stop_Callback(self,em_stop):

    	self.Em_Stop = em_stop.data

    def cmd_vel_Callback(self,cmd):

    	self.cmd_vel_linear = cmd.linear.x
    	self.cmd_vel_angular = cmd.angular.z


    def battery_state(self):

      if self.cmd_vel_linear <= 0.0 and self.cmd_vel_angular == 0.0 and (self.current_voltage > 0 and not self.Em_Stop) :
    	self.last_voltage = self.current_voltage
	if self.cptr == 0:
		self.charge_verif = self.current_voltage
		rospy.loginfo("cptr null")
	elif  self.cptr > 30:
		self.cptr = 0
	#rospy.loginfo("cptr = " + str(self.cptr))
	#rospy.loginfo("chg verif = " + str(self.charge_verif))
	#rospy.loginfo("diff = " + str(self.charge_verif - self.current_voltage))
    	time.sleep(0.3)
    	self.current_voltage = self.voltage
    	if (self.current_voltage - self.last_voltage)>0.25 or ((self.current_voltage - self.last_voltage)==0.0 and self.current_voltage > 13.89):
		self.charge_state = True
		self.cptr+=1
    	elif ( self.last_voltage - self.current_voltage)>0.25:
		self.charge_state = False
		self.cptr+=1
    	elif (self.current_voltage - self.charge_verif) > 0.2 and self.cptr==30 and self.charge_state == False and not self.change_status:
                self.charge_state = True
		self.change_status = True
                self.cptr+=1
	else:
                self.cptr+=1
    		self.pub_state.publish(self.charge_state)
      else:
	time.sleep(2)
	self.last_voltage = self.current_voltage
	self.charge_state = False
    
       
    def start(self):
        r = rospy.Rate(10) # 10hz
        while not rospy.is_shutdown():
            self.battery_state()
	    self.charge_percentage()
	    self.discharge_percentage()
            r.sleep()
    def charge_percentage(self):
	if self.charge_state:
	    t = datetime.datetime.now()# - self.t_start_robot
	    diff = t - self.time_cap
	    elapsed_ms = diff.total_seconds()

	    if (self.voltage_off - self.voltage) > 0.3 and not self.verif:	
	        self.bat_last_level = (self.voltage - self.V_discharge) *100/ (self.V_charge - self.V_discharge)
		self.verif = True
	    rospy.loginfo("elapsed_ms = " + str(elapsed_ms))
	    rospy.loginfo("step_time = " + str(self.t_charger-self.t_without_teleop))
	    if  elapsed_ms > (self.t_charger-self.t_without_teleop)/100 and self.discharge_percent<100:
		self.discharge_percent += 1.0
		self.time_cap = datetime.datetime.now()
		save_bat_level = open("/home/covealink2/catkin_ws/src/drivers/roboteq/roboteq_driver/battery_data/battery.txt", "w") 
		save_bat_level.write( str(self.discharge_percent)+"\n")
		save_bat_level.write( str(self.voltage))
	    #t_charger_rest = self.t_charger/100 * (100-self.discharge_percent)
	    #charge_percent = (self.V_charge - self.voltage)/(100-self.discharge_percent)
	    #save_bat_level = open("/home/covea/catkin_ws/src/drivers/roboteq/roboteq_driver/battery_data/battery.txt", "w") 
	    #save_bat_level.write( str(charge_percent))
	    	self.pub_level.publish(self.discharge_percent)
	    rospy.loginfo("charge_percent = " + str(self.discharge_percent)+"%")
	    self.pub_level.publish(self.discharge_percent)
    def discharge_percentage(self):
	t = datetime.datetime.now()# - self.t_start_robot
	diff = t - self.time_cap
	elapsed_ms = diff.total_seconds()
	if (self.voltage_off - self.voltage) > 0.3 and not self.verif:	
	    self.bat_last_level = (self.voltage - self.V_discharge) *100/ (self.V_charge - self.V_discharge)
	    self.verif = True
	if not self.charge_state:
	 if self.I_Motors>0 : 
	    t_with_teleop= self.Q_Bat/(self.I_Motors+self.I_leds+self.I_PC)*3600
	    if  elapsed_ms > t_with_teleop/100 and self.discharge_percent>0:
		self.discharge_percent -= 1.0
		self.time_cap = datetime.datetime.now()
		save_bat_level = open("/home/covealink2/catkin_ws/src/drivers/roboteq/roboteq_driver/battery_data/battery.txt", "w") 
		save_bat_level.write( str(self.discharge_percent)+"\n")
		save_bat_level.write( str(self.voltage))
	 else: 
	    self.t_without_teleop = self.Q_Bat/(self.I_PC)*3600 # +self.I_leds
	    if elapsed_ms > self.t_without_teleop/100 and self.discharge_percent>0:
		self.discharge_percent -= 1.0
		save_bat_level = open("/home/covealink2/catkin_ws/src/drivers/roboteq/roboteq_driver/battery_data/battery.txt", "w") 
		save_bat_level.write( str(self.discharge_percent)+"\n")
		save_bat_level.write( str(self.voltage))
		self.time_cap = datetime.datetime.now()
		rospy.loginfo("elapsed_ms = " + str(elapsed_ms))
		rospy.loginfo("t_without_teleop/100 = " + str(self.t_without_teleop/100))
	 rospy.loginfo("discharge_percent = " + str(self.discharge_percent)+"%")
	 self.pub_level.publish(self.discharge_percent)
	
	

if __name__ == '__main__':
    rospy.init_node("battery_level")
    battery_node = Battery()
    battery_node.start()

