__RTDE+servoj based robot control__

This repo contains an example to control Universal Robot communicating using RTDE and controlling the movement with servoj commands. 

The robot communication through RTDE is based on the example published by Universal Robots.

Then, the example executes as follows:

* Connect to the robot 
* Configure recipes
* Read joint positions from file (q_example.csv)
* Open a log file to save the actual joint positions
* Wait for the robot to start (push the play button on the teach pendant)
* Each cycle, send the next joint position
* Close connection when finished



