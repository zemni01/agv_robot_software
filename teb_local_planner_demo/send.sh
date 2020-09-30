#!/bin/bash

if sshpass -p "EX53Uj1M" scp /home/covea/catkin_ws/src/teb_local_planner_demo/map_enova.png root@92.222.64.10:/var/www/html;
then
	echo 'ok!'
fi
