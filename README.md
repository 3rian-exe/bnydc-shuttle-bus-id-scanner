Brooklyn Navy Yard Development Corporation Shuttle Bus ID Scanner
==================================================================

An access control device that scans an employee or tenants RFID badge along 
with visitors QR code passes to determine thier eligiblity. This device also 
serves as a method of recording ridership.

`Note: This device is a work in progress. There are hardware components such`
`as; the housing, battery, device providing cellular data, buzzer, LEDs and` 
`componets associated with it, that are still in the works or have yet to be`
`determined.`

## Overview
Using off the shelf compenents, this projects goal is to be a self contained 
device that is capable of scanning any employee or tenant ID badge and determine
their eligiblity for the BNYDC shuttle bus in addition to serving as a way to keep 
track of ridership. At this time the HID app is not compadible with this hardware.

so far, this is accomplished using the LenelS2 web API, Python 3, a Raspberry Pi 3, a 
generic USB 125khz RFID reader and a generic USB barcode reader scanner. 

In this readme, I will run through:
    1. The bill of materials
    2. Setting up the Raspberry Pi from scratch
    3. Setting up both the RFID reader and barcode scanner
    4. And setting up the software end so that the device is in a 'plug n play' state
    5. Connecting the LEDs.

# Lets Get Started

First, make sure you have a USB keyboard, HDMI cable (with appropriate adapters), monitor with an HDMI port, and a micro SD card reader.

1. Bill Of Materials (BOM):
    * Raspberry Pi
        You'll need a Raspberry Pi 3 or better, though a Raspberry Pi Zero W (or 2W) 
        could work as well but may require more adapters since you're limited by the 
        USB ports on the Zero varients. Not to mention the lack of an ethernet port 
        which may prove challenging later down the road. A 1GB model will sefice as 
        this program isn't too heavy on memory. You can find either the raspberry Pi 3, 
        Raspberry Pi 4, raspberry Pi 5 from either [Pimoroni](https://shop.pimoroni.com/) 
        or [Adafriut](https://www.adafruit.com/). There are other vendors but those
        are the ones I have purchased from in the past and can comfortably reccomend.
        A Raspberry Pi 4 1GB shouldn't run you more than $37 as of the time of this writing.
    * Micro SD Card
        Any micro sd card 32GB in size or greater is recommended. (And micro sd card reader)
    * RFID Reader 
        This [USB RFID Reader 125KHz](https://www.amazon.com/gp/product/B083KMYRZ5/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1) emulates a keyboard device and acts as the input for all the 
        RFID card/badge scans. In this doc I'll be using the document that this 
        reader comes with to setup the reader.
    * QR/Barcode Scanner
        This [USB 2D Embedded Mini Barcode Scanner](https://www.amazon.com/Embedded-Barcode-Scanner-Symcode-Computer/dp/B08SQBDT4W/ref=psdc_15327871_t1_B07CHGLY2W?th=1) also acts like a 
        keboard device and serves as the input device for all the visitor QR codes. 
    * Power Adapter
        Depending on the model you 
    * (Optional for the current stage of the project) Breadboard Kit
        This [Breadboard Kit](https://www.amazon.com/gp/product/B07ZYR7R8X/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1) will make it easier to prototype the hardware aspect 
        of this project but is not necissary as of yet. Note which Raspberry Pi 
        it's compadible with when purchasing. In this doc I'll also be using 
        the document that this QR reader comes with it for setup.

2. Setting Up The Raspberry Pi
    1. Download and install the [Raspberry Pi imager](https://www.raspberrypi.com/software/).
    2. Once you've installed the imager, insert the micro sd card into your computer. 
    Open the application and click the `CHOOSE DEVICE` button and find your 
    specific Raspberry Pi device. 
    Next click on `CHOOSE OS`, click on 'Raspberry Pi OS (other)' then click on 
    Raspberry Pi OS Lite (64-bit). 
    Next, click on `CHOOSE STORAGE` and select the micro sd card that you inserted. 
    Click `NEXT` and then click `EDIT SETTINGS`. 
    Under the `GENERAL` tab you can set the host name and configure the wireless 
    LAN setting. Fill in the username and password along with configuring the 
    wireless LAN setting. Feel free to set the host name to whatever you want but 
    make sure to take note of it along with the username, and password. Once you're 
    finished with that, go the `SERVICES` tab, and check the `Enable SSH` checkbox. 
    Under that checkbox, check the `Use Password authentication` option.
    Now click `SAVE`, agree to formatting the card and flash the OS.
    Once that's done remove the micro sd card and insert it into the Raspberry Pi. 
    3. Before powering on the Raspberry Pi for the first time make sure you have a USB keyboard and an HDMI monitor that you can plug into the Pi. Once you have those plugged in, plug in the power and wait for the first boot sequence to finish then login once prompted with the credentials from the previous step. Next, you want to find the devices IP address so you can SSH into it for any future interactions without needing a keyboard and monitor plugged in. Now that you're logged in, type `ifconfig`. Under 'wlan0' you should see your IP address next to 'inet'.
    4. Now login for the first time by opening Git Bash and typing ```ssh <userName>@<IPAdress``` and then you should see a prompt asking if you want to continue connecting. Type ```yes``` and hit enter. Next once prompted, enter the password that you set and hit enter. Not you're all set.
    Note: If you get an error after trying to SSH in that says `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` go to the file that is specified and deletet the lines that have the same IP address.

3. Setting up the USB RFID reader and barcode scanner
    * RFID Reader
    1. When configuring the RFID reader for the first time, it's best to open a text editor on PC with a regular GUI enviroment. 
        1. Open a text editor of your choice and make sure the coursor is blinking as if you were ready to start typing.
        2. Next plug the RFID reader in and tap the Config Card that comes in the box with the reader.
        3. You should see the following: 
            ```
            support email  taylor@szjat.com.cn

            download user manual/video  www.fissaid.cn/eh301

            fm ver-6.0.0

            current setting is
                01  8h-10d           
                with enter       
                enable buzzer   
                disable hid raw  
                normal data      
                usa keyboard     

            important-
            use short or long read card method to choice or disable items
            short read card = read card till 1 beep,then remove card
            long read card =  read card till 2 beep,then remove card

            config reader ...if format 1-11 not same as your hid card , try advanced config
            ```

            Note: The instructions for confirming or dening a setting by either short or long tapping the config card.

            You're going to skip till you see `02  2h-3d 4h-5d`. Long tap the config card until you hear the double beep.
            Then short read until you come to buzzer sound. You don't have to but I reccomend disabling it since it can get annoying after testing many cards.
            For the next option you'll want to enable HID raw output by long tapping the config card until you hear the double beep.
            The rest of the settings you should short tap the config card. Then quit with a long tap until you hear the double beep. The RFID reader set up is now complete. IF you're unsure of something either consult the included documentation or some Googling should do the trick.

    * Setting up the USB Barcode Scanner
    1. The setup for the USB barcode scanner is more straight forward and doesn't require a text editor.
    Plug in the scanner and take out the included document.
    2. Scan the following QR codes present on the included doc by pressing the button on top.
        1. Sound setting: scan the 'turn off sound' QR code (This is optinal but recommended).
        2. Reading Mode: scan the 'Continuous Mode' QR code.
    
    And that's it for the input devices.

4. Setting Up The Software Side Of Things On The Raspberry Pi
       ** set static IP address
    1. SSH into your Pi and run `sudo apt update` once your Pi is updated, install git by running `sudo apt install git`. 
    2. SSH into your Pi and navigate to the directory where you want this project to live and clone this repo.
    3. Ask somebody for the config.json file and put that into projects directory. Once you have it locally on your pc, open a terminal and type `scp <sourceFilePath> <user>@<IPaddress>: <targetDestinationPath>`.
    4. Open main.py in a text editor and set the `config_file_path` variable to the absolute path of the config file. Save and close it.
    5. Open login_logout_s2.py and again add the absolute path of the config file. Save and close it.
    5. Install pip by typing `sudo apt install python3-pip`
    6. Install the following Pyton libraries: `xmltodict`, and `urllib3`
        * Type: `pip install xmltodict` hit enter.
        * Type: `pip install urllib3` hit enter.
    5. Test the program by running main.py. To do this type `sudo python main.py` into the terminal. If you're within the the shuttle bus operating hours time frame you should see the prompt 'Tap RFID card or scan QR code: ' printed to the screen along with the current session ID printed above it. Hit ctrl+C to exit. If it doesn't exit right away hit enter and you'll be prompted to exit the process. Type `y` and hit enter.

    Verify the input devices work.
    1. Plug the Pi into an HDMI monitor and connect a keyboard to it. Plug in both the RFID reader and the barcode reader. You may see a warning regarding undervoltage being detected. Don't worry about that for the time being.
    2. If the Pi has the LEDs already connected to it you will briefly see them flash once the program starts and every time someone is granted or denied access you see a green or red LED flash briefly. If they aren't already connected, consult the next section which will cover how to do this.
    3. Run main.py and start scanning RFID cards and Proxyclick QR passes to verify its working. Note: if there aren't any LEDs connected you will have to open main.py in a text editor and uncomment the lines with ```print("Green")``` and ```print("Red")``` inside the ```loop()``` function. This way you'll see the output locally as well as on S2's activity feed.
    4. Next we need to make sure that the Pi is automatically logged in on startup. Type `sudo raspi-config` into the terminal and navigate through the following `1 System Options` -> `S5 Boot / Auto Login` -> `B2 Console Autologin` hit enter, then `Finish` then click `yes` to the prompt asking you if you want to reboot. Or in the terminal type `sudo reboot` and hit enter.
    5. Navigate to `home/<user>/` and open `.bashrc` with a text editor. Go all the way to the bottom and add the following: `sleep 20` and on the next line type `python /home/<user>/<projectDir>/main.py` (`pyhton /<fullPathTomain.py>`). Save and quit.
    6. Shutdown the Pi by typing `sudo shutdown -h now`, wait about 30 seconds and disconnect the power. Plug in the RFID reader, the barcode scanner, and an HDMI monitor. Plug the power in and verify that mian.py is automatically running. This could take some time as there is a delay to allow enough time for the wifi to connect. 

6. Wiring Up The LEDs
    1. From the breadboard holder kit get a green and red LED diode, the T-shaped GPIO extension board (![looks like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true)) along with 2, 1K resistors, and some jumper wires.
    2. Connect the T-shaped GPIO  extension board to the breadboard like (![this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true))
    3. Connect a jumper wire from 'GND' to the minus row like (![this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true))
    4. Connect one jumper to GPIO 18 and another jumper wire to GPIO 23 like (![this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true))
    5. Insert the jumper wire from GPIO 23 to a resistor. Then on a column next to the resistor connect a jumper wire to the minus rail. Then insert an let across those two columns where the longer side of the LED is in the same column as the resistor and the shorter side is in the same column as the wire connected to ground. (![like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true))
    6. Do the same thing as the previous step but instead with the jumper connected to GPIO 18 and with the Green LED. (![like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true))
    7. Connect the ribbon cable to the T-shaped board that you plugged into the breadboard. It's keyed with a notch on one side so there's only one way to do it.
    8. Plug the other side of the cable into the Raspberry Pis GPIO pins (![like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/main/image.jpg?raw=true))

    9. Trouble shooting: If none of the LEDs light up, verify that the the LED diodes are inserted the correct way as stated in step 5. If this was the case the LED/s could have been burnt out and likely need to be replaced.
