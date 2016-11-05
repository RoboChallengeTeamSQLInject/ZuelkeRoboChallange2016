#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import time
import ev3dev.ev3 as ev3

DEBUG = False
DEFAULT_SLEEP_TIMEOUT_IN_SEC = 0.1
DEFAULT_SPEED = 200
DEFAULT_DUTY_CYCLE = -100
DEFAULT_THRESHOLD_DISTANCE = 300
DEFAULT_COLOR_THRESHOLD = 20
DEFAULT_SM_RANGE = 75
##
# Setup

# motors
right_motor = ev3.LargeMotor('outA')
print("motor right connected: %s" % str(right_motor.connected))

left_motor = ev3.LargeMotor('outB')
print("motor left connected: %s" % str(left_motor.connected))

small_motor = ev3.MediumMotor('outC')
print("small motor connected: %s" % str(small_motor.connected))
small_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE

motors = [left_motor, right_motor]
for m in motors:
    m.reset()
    m.duty_cycle_sp = DEFAULT_DUTY_CYCLE

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

button = ev3.Button()

# Sound
sound = ev3.Sound()


##
#  Robot functionality
##
def backward():
    for m in motors:
        set_speed(DEFAULT_SPEED, DEFAULT_DUTY_CYCLE * -1.0)
        m.run_forever()


def forward():
    for m in motors:
        set_speed(DEFAULT_SPEED, DEFAULT_DUTY_CYCLE * 0.75)
        m.run_forever()


def set_speed(speed, duty_cycle):
    for m in motors:
        m.speed_sp = speed
        m.duty_cycle_sp = duty_cycle


def brake():
    for m in motors:
        m.stop()


def teardown():
    sound.speak('Bye bye...')
    for m in motors:
        m.stop()
        m.reset()


def rotate(left):
    brake()

    if left:
        left_motor.duty_cycle_sp = - DEFAULT_DUTY_CYCLE * 0.75
        right_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE * 0.75
    else:
        left_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE * 0.75
        right_motor.duty_cycle_sp = - DEFAULT_DUTY_CYCLE * 0.75

    for m in motors:
        m.run_forever()


def over_border():
    return (color_sensor.value() > DEFAULT_COLOR_THRESHOLD)


def turn_around():
    if DEBUG:
        print('Oiii border...')
    sound.beep()
    set_speed(DEFAULT_SPEED, DEFAULT_DUTY_CYCLE)
    brake()
    backward()
    time.sleep(0.5)


def enemy_spotted():
    return (ultrasonic_sensor.value() < DEFAULT_THRESHOLD_DISTANCE)


def attack():
    if DEBUG:
        print('Attack!')
    # sound.speak('Attack!')
    forward()


def search(left):
    if DEBUG:
        print('Searching opponent')
    # sound.speak('Where are you?')
    rotate(left)


def distract():
    # small_motor.
    if DEBUG:
        print('distract')
    if small_motor.position < -DEFAULT_SM_RANGE:
        small_motor.duty_cycle_sp = DEFAULT_DUTY_CYCLE
    elif small_motor.position > DEFAULT_SM_RANGE:
        small_motor.duty_cycle_sp = -DEFAULT_DUTY_CYCLE
    small_motor.run_to_abs_pos()


##
# Main loop

def run_loop():
    left = True

    while True:
        # time.sleep(DEFAULT_SLEEP_TIMEOUT_IN_SEC)
        if DEBUG:
            print('----------------------------')
            print('color value: %s' % str(color_sensor.value()))
            print('ultrasonic value: %s' % str(ultrasonic_sensor.value()))
            print('motor positions (r, l): %s, %s' % (str(right_motor.position), str(left_motor.position)))
            print('touch sensors: %s, %s' % (str(left_button.value()), str(right_button.value())))

        # Stop if there is a white border infront
        if over_border():
            turn_around()

        else:
            # Move forward if there is something infront, otherwise rotate
            if enemy_spotted():
                attack()
            else:
                search(left)
                distract()

            # opponent on left side, rotate left
            if left_button.value():
                left = True

            # opponent on right side, rotate right
            if right_button.value():
                left = False


def main():
    print('I am ready. Please start me!')
    sound.speak('I am ready. Please press any button!')

    # Wait for any key
    while True:
        if DEBUG:
            print('ready')
        if button.any():
            break

    set_speed(DEFAULT_SPEED, DEFAULT_DUTY_CYCLE)

    # Main loop
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
