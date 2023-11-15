from gpiozero import LED
from time import sleep

red = LED(23)
green = LED(18)

def blink_red(sleep_seconds):
    red.on()
    sleep(sleep_seconds)
    red.off()

def blink_green(sleep_seconds):
    green.on()
    sleep(sleep_seconds)
    green.off()
