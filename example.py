
#!/usr/bin/env python

import sys
import logging

import time
import csv
import numpy as np

import rtde.rtde as rtde
import rtde.rtde_config as rtde_config


####### FUNCIONES
# velocidades a lista
def set_q_to_list(set_q):
    list = []
    for i in range(0,7):
        list.append(set_q.__dict__["input_double_register_%i" % i])
        print 
    return list

# lista a velocidades
def list_to_set_q(set_q, list):
    for i in range (0, len(list)):
        set_q.__dict__["input_double_register_%i" % i] = list[i]
    return set_q


########################
######
###### MAIN
######
########################
def main():
    ####### Connect to controller
    ROBOT_PORT = 30004
    ROBOT_HOST = '192.168.1.50'#'localhost' 
    logging.getLogger().setLevel(logging.INFO)
    con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
    error = con.connect()
    while error != 0:
        time.sleep(0.5)
        error = con.connect()

    print 'Connected to robot'
    
    ####### Config recipes
    FREQUENCY = 500
    config_filename = 'servoj_control_loop_configuration.xml'
    conf = rtde_config.ConfigFile(config_filename)
    state_names, state_types = conf.get_recipe('state')
    set_q_names, set_q_types = conf.get_recipe('set_q')
    watchdog_names, watchdog_types = conf.get_recipe('watchdog')

    con.send_output_setup(state_names, state_types, FREQUENCY)
    set_q = con.send_input_setup(set_q_names, set_q_types)
    watchdog = con.send_input_setup(watchdog_names, watchdog_types)

    ####### Read joint positions from file
    name = 'q_example.csv'
    file = open(name, 'rb')
    reader = csv.reader(file, delimiter=',')
    q1=[]
    q2=[]
    q3=[]
    q4=[]
    q5=[]
    q6=[]
    for row in reader:
        q1.append(float(row[0]))
        q2.append(float(row[1]))
        q3.append(float(row[2]))
        q4.append(float(row[3]))
        q5.append(float(row[4]))
        q6.append(float(row[5]))                     

    ####### Initial joint pos 
    set_q.input_double_register_0 = q1[0]
    set_q.input_double_register_1 = q2[0]
    set_q.input_double_register_2 = q3[0]
    set_q.input_double_register_3 = q4[0]
    set_q.input_double_register_4 = q5[0]
    set_q.input_double_register_5 = q6[0]

    ####### Log actual joint pos 
    name = 'log.csv'
    csvfile = open(name, 'w')
    writer = csv.writer(csvfile, delimiter=',')

    #start data synchronization
    if not con.send_start():
        sys.exit()

    watchdog.input_int_register_0 = 0

    print 'Wait for the Robot to start'
    PROGRAM_STARTED_AND_READY = False
    while PROGRAM_STARTED_AND_READY == False:
        state = con.receive()
        #while state == None:
            #state = con.receive()
        con.send(watchdog)
        if state.output_bit_registers0_to_31 == True:
            PROGRAM_STARTED_AND_READY = True

    print 'Send initial qs'
    con.send(set_q)
    time.sleep(0.01)
    watchdog.input_int_register_0 = 1
    con.send(watchdog)
 
    # Wait for moveJ to finish
    state = con.receive()
    PROGRAM_STARTED_AND_READY = False
    while PROGRAM_STARTED_AND_READY == False:
        state = con.receive()
        if state.runtime_state > 1: 
            con.send(watchdog)
            if state.output_bit_registers0_to_31 == True:
                PROGRAM_STARTED_AND_READY = True
    
    print 'Control loop'
    idx = 1
    watchdog.input_int_register_0 = 2
    con.send(watchdog)
    ###### control loop
    while idx < len(q1):
        state = con.receive()
        writer.writerow([state.actual_q[0], state.actual_q[1], state.actual_q[2], state.actual_q[3], state.actual_q[4], state.actual_q[5]])
        if state.runtime_state > 1: 
            ###### send to the robot  
            list_to_set_q(set_q, [q1[idx], q2[idx], q3[idx], q4[idx], q5[idx], q6[idx]])
            con.send(set_q)
            con.send(watchdog)
            idx = idx + 1

    ###### CERRAR
    print 'End and close'
    watchdog.input_int_register_0 = 3
    con.send(watchdog)
    time.sleep(0.01)
    con.send_pause()
    con.disconnect()

if __name__ == "__main__":
    main()




