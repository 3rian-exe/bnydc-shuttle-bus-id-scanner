Brooklyn Navy Yard Development Corporation Shuttle Bus ID Scanner
==================================================================

An access control device that scans an employee or tenants RFID badge along 
with visitors QR code passes to determine thier eligiblity. This device also 
serves as a method of recording ridership.

`Note: This device is a work in progress. There are hardware components such as; the housing, battery, device providing cellular data, buzzer, LEDs and componets associated with it, that are still in the works or have yet to be determined. `

## Overview
Using off the shelf compenents, this projects goal is to be a lef contained device that is capable of scanning any employee or tenant ID badge and determine their eligiblity for the BNYDC shuttle bus in addition to serving as a way to keep track of ridership. 

This is accomplished using the LenelS2 web API, Python 3, a Raspberry Pi 3, a generic USB 125khz RFID reader and a generic USB barcode reader scanner. 

In this readme, I will run through:
    1. The bill of materials
    2. Setting up the Raspberry Pi from scratch
    3. Setting up both the RFID reader and barcode scanner
    4. And setting up the software end so that the device is in a 'plug n play' state

# Lets Get Started

1. Bill Of Materials (BOM):

    * Raspberry Pi
        You'll need a Raspberry Pi 3 or better, though a Raspberry Pi Zero W (or 2W) could work as well but may require more adapters since you're limited by the USB ports on the Zero varients. Not to mention the lack of an ethernet port which may prove challenging later down the road. A 1GB model will sefice as this program isn't too heavy on memory. You can find either the raspberry Pi 3, Raspberry Pi 4, raspberry Pi 5 from either [Pimoroni](https://shop.pimoroni.com/) or [Adafriut](https://www.adafruit.com/). There are other vendors but those are the ones I have purchased from in the past and can comfortably reccomend.
        A Raspberry Pi 4 1GB shouldn't run you more than $37 as of the time of this writing.
    
    * Micro SD Card
        Any micro sd card 32GB in size or greater is recommended.

    * RFID Reader 
        This [USB RFID Reader 125KHz](https://www.amazon.com/gp/product/B083KMYRZ5/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1) emulates a keyboard device and acts as the input for all the RFID card/badge scans. In this doc I'll be using the document that this reader comes with to setup the reader.
    
    * QR/Barcode Scanner
        This [USB 2D Embedded Mini Barcode Reader Scanner Scan](https://www.amazon.com/Embedded-Barcode-Scanner-Symcode-Computer/dp/B08SQBDT4W/ref=psdc_15327871_t1_B07CHGLY2W?th=1) also acts like a keboard device and serves as the input device for all the visitor QR codes. 
    
    * (Optional for the current stage of the project) Breadboard Kit
        This [Breadboard Kit](https://www.amazon.com/gp/product/B07ZYR7R8X/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1) will make it easier to prototype the hardware aspect of this project but is not necissary as of yet. Note which Raspberry Pi it's compadible with when purchasing.

2. Setting Up The Raspberry Pi
    1. Download and install the [Raspberry Pi imager](https://www.raspberrypi.com/software/).
    2. Once you've installed the imager, insert the micro sd card into your computer. Open the application and choose the Raspberry Pi device that you'll be using. Next click on operating system, choose 'Raspberry Pi OS (other)' then click on Raspberry Pi OS Lite (64-bit). Next, click on 'choose storage' and select the micro sd card that you inserted. Click 'next' and then click 'edit settings'. Under the 'general' tab you can set the host name and configure the wireless LAN setting. Fill in the username and password along with configuring the wireless LAN setting. Feel free to set the host name to whatever you want but make sure to take note of the username, password, and hostname. Once you're finished with that, go the 'services' tab, and check the 'enable ssh' checkbox. Under that checkbox, check the 'use password authentication' option.
    Now click save, agree to formatting the card and flash the OS.
    Once that's done remove the micro sd card and insert it into the Raspberry Pi. 
    3. Before powering on the Raspberry Pi for the first time make sure you have a USB keyboard and an HDMI monitor that you can plug the Pi into. Once you have those plugged in, plug in the power and login into the Pi with the credentials from the previous step. Next you want to find the devices IP address so you can SSH into it for any future interactions without needing a keyboard and monitor plugged in. Now that you're logged in, type `ifconfig` and you'll find the devices IP address by the INET paremeter on the second line ***** DOUBLE CHECK THIS PART ******
    

        

