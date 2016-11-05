#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import time
import ev3dev.ev3 as ev3

DEBUG = False

# default sleep timeout in sec
DEFAULT_SLEEP_TIMEOUT_IN_SEC = 0.1

# default speed
DEFAULT_SPEED = 200
DEFAULT_DUTY_CYCLE = -100

# default threshold distance
DEFAULT_THRESHOLD_DISTANCE = 300
DEFAULT_COLOR_THRESHOLD = 20
##
# Setup
##
if DEBUG:
    print("Setting up...")

# motors
right_motor = ev3.LargeMotor('outA')
print("motor right connected: %s" % str(right_motor.connected))

left_motor = ev3.LargeMotor('outB')
print("motor left connected: %s" % str(right_motor.connected))

motors = [left_motor, right_motor]
right_motor.reset()
left_motor.reset()
right_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE
left_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE

# sensors
color_sensor = ev3.ColorSensor()
print("color sensor connected: %s" % str(color_sensor.connected))
color_sensor.mode = 'COL-REFLECT'

ultrasonic_sensor = ev3.UltrasonicSensor()
print("ultrasonic sensor connected: %s" % str(ultrasonic_sensor.connected))
ultrasonic_sensor.mode = 'US-DIST-CM'

# buttons
right_button = ev3.TouchSensor('in3')
print("button right connected: %s" % str(right_button.connected))

left_button = ev3.TouchSensor('in4')
print("button left connected: %s" % str(right_button.connected))

# Sound
sound = ev3.Sound()

# Start Button
button = ev3.Button()


##
#  Robot functionality
##
def backward():
    for m in motors:
        # m.speed_sp = 500
        m.duty_cycle_sp = -DEFAULT_DUTY_CYCLE
        m.run_forever()


def forward():
    for m in motors:
        # m.speed_sp = -500
        m.duty_cycle_sp = DEFAULT_DUTY_CYCLE * 0.75
        m.run_forever()


def set_speed(speed, duty_cycle):
    for m in motors:
        m.speed_sp = speed
        m.duty_cycle_sp = duty_cycle


def brake():
    for m in motors:
        m.stop()


def teardown():
    print('Tearing down...')
    for m in motors:
        m.stop()
        m.reset()


def rotate(left):
    brake()
    if left:
        left_motor.duty_cycle_sp = - DEFAULT_DUTY_CYCLE
        right_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE
    else:
        left_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE
        right_motor.duty_cycle_sp = - DEFAULT_DUTY_CYCLE
    for m in motors:
        m.run_forever()


def run_loop():
    left = True
    # game loop (endless loop)
    while True:
        # time.sleep(DEFAULT_SLEEP_TIMEOUT_IN_SEC)
        if DEBUG:
            print('----------------------------')
            print('color value: %s' % str(color_sensor.value()))
        # print('ultrasonic value: %s' % str(ultrasonic_sensor.value()))
        # print('motor positions (r, l): %s, %s' % (str(right_motor.position), str(left_motor.position)))
        # print('touch sensors: %s, %s' % (str(left_button.value()), str(right_button.value())))

        # Stop if there is a white border infront
        if color_sensor.value() > DEFAULT_COLOR_THRESHOLD:
            if DEBUG:
                print('Oiii border...')
            sound.beep()
            set_speed(DEFAULT_SPEED, DEFAULT_DUTY_CYCLE)
            brake()

            backward()
            time.sleep(0.5)

        else:

            # Move forward if there is something infront, otherwise rotate
            if ultrasonic_sensor.value() < DEFAULT_THRESHOLD_DISTANCE:
                if DEBUG:
                    print('Attack!')
                sound.speak('Attack!')
                forward()
            else:
                if DEBUG:
                    print('Searching opponent')
                # sound.speak('Where are you?')
                rotate(left)

            # opponent on left side, rotate left
            if left_button.value():
                sound.speak('left')
                if DEBUG:
                    print('setting rotation direction to left')
                left = True

            # opponent on right side, rotate right
            if right_button.value():
                sound.speak('right')
                if DEBUG:
                    print('setting rotation direction to right')
                left = False


def main():
    print('start me!')
    while True:
        if DEBUG:
            print('ready')
        if button.any():
            break

    set_speed(DEFAULT_SPEED, DEFAULT_DUTY_CYCLE)

    try:
        run_loop()

    # doing a cleanup action just before program ends
    # handle ctr+c and system exit
    except (KeyboardInterrupt, SystemExit):
        teardown()
        raise

    # handle exceptions
    except Exception as e:
        print('ohhhh error!')
        print(e)
        teardown()


##
# start the program
##
main()
