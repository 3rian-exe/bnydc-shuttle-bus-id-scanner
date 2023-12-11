# Brooklyn Navy Yard Development Corporation Shuttle Bus ID Scanner

An access control device that scans an employee or tenant's RFID badge along with visitors Proxyclick passes to determine their eligibility. This device also serves as a method of recording ridership.

**Note: This device is a work in progress. There are hardware components, such as the housing, battery, device providing cellular data, buzzer, LEDs, and other miscellaneous components, that are still in the works or have yet to be determined.**

## Overview
Using off-the-shelf components, this project's goal is to be a cost-effective and self-contained device that is capable of scanning an employee or tenant's RFID badge or a visitor's Proxyclick QR code to determine their eligibility for the BNYDC shuttle bus. All of this is accomplished using the LenelS2 web API, Python 3, a Raspberry Pi 3, a generic USB 125kHz RFID reader, and a generic USB barcode scanner. At this time, the HID mobile application is not compatible with this hardware.

In this readme, I will run through:
1. The bill of materials
2. Setting up the hardware 
3. Setting up the software
4. Wiring the LEDs

# Lets Get Started
First, some supporting items that you'll need:
* USB Keyboard
* Monitor with an HDMI port (or appropriate adapters)
* HDMI Cable (with appropriate adapters if necessary)
* Micro SD Card Reader
* An Internet Connection

1. Bill Of Materials (BOM):
    1. Raspberry Pi
        * The following Raspberry Pi models are recommended for this project: Raspberry Pi 3, Raspberry Pi 4, or Raspberry Pi 5. The Raspberry Pi Zero W or Zero 2W are likely to work as well, but the lack of ports may become a limitation as the project progresses. The 1GB Raspberry Pi 4 is a solid choice for this projects needs. Any of the aforementioned hardware can be purchased from either [Pimoroni](https://shop.pimoroni.com/), [Adafriut](https://www.adafruit.com/), or most other hobby electronics retailers.
    2. Micro SD Card
        * Any microSD card of 32GB or greater in size is recommended.
    3. RFID Reader 
        * This [USB 125KHz RFID Reader](https://www.amazon.com/gp/product/B083KMYRZ5/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1) emulates a keyboard device and acts as the input device reading  all the RFID badge scans. 
    4. QR/Barcode Scanner
        * This [USB 2D Embedded Mini Barcode Scanner](https://www.amazon.com/Embedded-Barcode-Scanner-Symcode-Computer/dp/B08SQBDT4W/ref=psdc_15327871_t1_B07CHGLY2W?th=1) also acts like a keyboard device and serves as the input device reading all the visitor QR code scans. 
    5. Power Adapter
        * For the Raspberry Pi 3, you will need a 5V, 3Amp power supply with a micro USB cable. For the Raspberry Pi 4, you will need a 5V, 3Amp power supply with a USB-C cable. And for the Raspberry Pi 5, you will need a 5V, 5Amp power supply and a USB-C cable.
    6. (Optional for the current stage of the project) Breadboard Kit
        * This [breadboard kit](https://www.amazon.com/gp/product/B07ZYR7R8X/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1) will make it easier to prototype the hardware aspects of this project, but it is not necessary as of yet. Note which Raspberry Pi it's compatible with when purchasing.

2. Setting up the hardware
    1. The Raspberry Pi
        1. Download and install the [Raspberry Pi imager](https://www.raspberrypi.com/software/).
        2. Once you've installed the imager, insert the microSD card into your computer. Open the application, click the `CHOOSE DEVICE` button, and find your model of Raspberry Pi. Next, click on `CHOOSE OS`, click on `Raspberry Pi OS (other)`, then click on `Raspberry Pi OS Lite (64-bit)`. Next, click on `CHOOSE STORAGE` and select the microSD card that you inserted. Click `NEXT` and then click `EDIT SETTINGS`. Under the `GENERAL` tab, you can set the host name and configure the wireless LAN. Fill in the username and password, along with configuring the wireless LAN. Feel free to set the host name to whatever you want, but make sure to take note of it along with the username and password. Once you're finished, go to the `SERVICES` tab and check the `Enable SSH` checkbox. Under that checkbox, check the `Use Password authentication` option. Now click `SAVE`, agree to formatting the card, and flash the OS. Once that's done, remove the microSD card and insert it into the Raspberry Pi.
        3. Before powering on the Raspberry Pi for the first time, plug in both the HDMI monitor and USB keyboard. Now plug in the power and wait for the first boot sequence to finish, then login once prompted with the credentials from the previous step. Next, you want to find the device's IP address so you can SSH into it for any future interactions without needing a keyboard and monitor plugged in. You can do this one of two ways: 
            * Type ```hostname -I```, hit enter and you should see it.
            * Type ```ifconfig```, hit enter and under `wlan0`, you should see your IP address next to `inet`.
        4. Now SSH in by opening Git Bash and typing ```ssh <userName>@<IPAdress```, and then you should see a prompt asking if you want to continue connecting. Type ```yes``` and hit enter. Next, once prompted, enter the password that you set and hit enter. Now you're all set.
        Note: If you get an error after trying to SSH in that says, `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` go to the file that is specified and delete the lines that have the same IP address.
        5. Now you want to assign the device a static IP address. To do this, first make sure you SSH into your device. Then type ```sudo route -n``` and hit enter. Under `Gateway` you'll see an IP address. Write it down. Next, type ```sudo vim /etc/dhcpcd.conf``` and hit enter. Type ```i``` and hit enter to insert text. Now, on the first line type in ```interface wlan0```, on the second line type ```static ip_address=<static_IP_address>``` replace ```<static_IP_address>``` with your current IP address, on the third line type ```static routers=<gateway>``` and replace ```<gateway>``` with the gateway IP address you wrote down. On the fourth line, type ```static domain_name_servers=8.8.8.8 8.8.4.4```. In this case, I used Googles domain name, but you can change it to a different one if you'd like. Now hit Esc, and type ```:wq``` and hit enter. Next, restart by typing ```sudo reboot``` and hit enter. And that's it for this step.

    2. The USB RFID Reader
        1. Open a text editor of your choice on your pc.
        2. Plug the RFID reader in and tap the config card that comes in the box.
        3. You should see the following being typed into your text editor: 
            ```support email  taylor@szjat.com.cn

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

        Note: The instructions for confirming or denying a setting by either short or long tapping the config card.
        You're going to skip until you see `02  2h-3d 4h-5d`. Long tap the config card until you hear the double beep. Then short read until you come to the enable buzzer setting. You don't have to, but I recommend disabling it since it can get annoying after testing many cards. For the next option, you'll want to enable HID raw output by long tapping the config card until you hear the double beep. The rest of the settings you should short tap the config card. Then quit with a long tap until you hear the double beep. The RFID reader set up is now complete. If you're unsure of something, either consult the included documentation ([documentation front](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/rfid-reader-doc1.jpeg), [documentation back](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/rfid-reader-doc2.jpeg)) or some Googling should do the trick.

    3. The USB Barcode Scanner
        1. The setup for the USB barcode scanner is more straight forward and doesn't require a text editor. Plug in the scanner and take out the included document ([document front](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/barcode-scanner-doc1.jpeg), [document back](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/barcode-scanner-doc2.jpeg)).
        2. Scan the following QR codes present on the included document by pressing the button on top.
            1. Sound setting: scan the `turn off sound` QR code (This is optinal but recommended).
            2. Reading Mode: scan the `Continuous Mode` QR code.

3. Setting Up The Software
    Note: To find the full or absolute path to a file in your current directory, navigate to the directory where the file resides and type ```readlink -f <fileName>```, replacing ```<fileName>``` with the actual name of the file you're trying to retrieve the absolute path to.
    1. SSH into your Pi and update it by typing ```sudo apt update```, and hitting enter. Once your Pi is updated, install git by typing ```sudo apt install git``` and hitting enter.
    2. Navigate to the directory where you want this project to live and clone this repo by typing ```git clone <httpsLink>``` and replace ```<httpsLink>``` with the link you got from this repositories clone tab (found in this repository -> Code -> Local -> HTTPS). Hit enter and wait for it all to download.
    3. Ask somebody for the config.json file. Once you have it locally on your pc, open a terminal and type ```scp <configFilePath/config.json> <user>@<IPaddress>: <targetDestinationPath>```, replacing ```<configFilePath/config.json>``` with where the config.json file is stored on your local machine, replacing ```<user>@<IPaddress>``` with the same credentials as when you normally SSH in, and replacing ``` <targetDestinationPath>``` with the path to the cloned repository directory. Once you hit enter, you will be prompted for a password, which is the same as if you SSH in like usual.
    4. Open main.py in a text editor and set the `config_file_path` variable to the absolute path of the config.json file. Save it and close it.
    5. Open login_logout_s2.py and again set the `config_file_path` variable to the absolute path of the config.json file. Save it and close it.
    5. Install pip by typing ```sudo apt install python3-pip``` and hitting enter.
    6. Install the following Python libraries: `xmltodict`, and `urllib3`
        * Type: ```pip install xmltodict``` hit enter.
        * Type: ```pip install urllib3``` hit enter.
    5. Test the program by running main.py. To do this, navigate to this repo and type ```sudo python main.py``` into the terminal and hit enter. If you're within the shuttle bus operating hours, you should see the prompt `Tap RFID card or scan QR code: ` printed to the screen along with the current session ID printed above it. Hit Ctrl+C to exit. If it doesn't exit right away, hit enter, and you'll be prompted to exit the process. Type ```y``` and hit enter.

    Verify that the input devices work.
    1. Plug the Pi into an HDMI monitor and connect a keyboard to it. Plug in both the RFID reader and the barcode reader. You may see a warning regarding undervoltage being detected. Don't worry about that for the time being, just hit enter.
    2. If the Pi has the LEDs already connected to it, you will briefly see them flash once the program starts, and every time someone is granted or denied access, you see a green or red LED flash briefly. If they aren't already connected, consult the next section, which will cover how to do this.
    3. Run main.py and start scanning RFID cards and Proxyclick QR passes to verify it's working.
    Note: If there aren't any LEDs connected, you will have to open main.py in a text editor and uncomment the lines with `print("Green")` and `print("Red")` inside the `loop()` function. This way, you'll see the output locally and not just on S2's activity feed.
    4. Next, we need to make sure that the Pi is automatically logged in on startup. Type ```sudo raspi-config``` into the terminal and navigate through the following with your arrow keys: `1 System Options` -> `S5 Boot / Auto Login` -> `B2 Console Autologin`, next `Finish`, then click `yes` to the prompt asking you if you want to reboot. Or in the terminal, type ```sudo reboot``` and hit enter.
    5. Once you SSH back in, navigate to `home/<user>/`, where `<user>` is the username that you set for the Raspberry Pi. Open `.bashrc` with a text editor. Go all the way to the bottom and add the following: ```sleep 20``` and on the next line type ```python /home/<user>/<projectDir>/main.py```, replacing ```<user>``` with your username and ```<projectDir>```, with the absolute path to `main.py`. Save and quit.
    6. Shutdown the Pi by typing ```sudo shutdown -h now```, wait about 30 seconds, and disconnect the power. Plug in the RFID reader, the barcode scanner, and an HDMI monitor. Plug the power in and verify that mian.py is automatically running. You should see the LEDs blink briefly and the prompt from main show up on the terminal. This could take about 45 seconds, as there is a delay to allow enough time for the wifi to connect.
    Note: Every time you login to this device, whether it be with SSH or with a keyboard and monitor connected to it, main.py will run within about 20 seconds. To prevent this for an individual login, simply hit Ctrl+C once you're logged in.

4. Wiring Up The LEDs
    1. From the breadboard holder kit, get a [green](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/greenLED.png) and [red](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/redLED.png) LED diode, the [T-shaped GPIO extension board](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/GPIO-t-board.png) along with 2 [1K resistors](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/resistor.png)(they may be blue), and some [jumper wires](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/jumperWires.png).
    2. Connect the T-shaped GPIO extension board to the breadboard [like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/TBoardOnBreadboard.png).
    3. Connect a jumper wire from 'GND' to the minus rail [like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/GND-to-GND-rail.png).
    4. Connect one jumper wire to GPIO 18 and another jumper wire to GPIO 23 [like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/GPIO-wire-connection.png).
    5. Insert the jumper wire from GPIO 23 into a column connected to a resistor. Then, on a column next to the resistor, connect a jumper wire to the minus rail. Then insert the red LED across those two columns, where the LONGER pin of the LED is in the same column as the resistor and the shorter side is in the same column as the wire connected to ground. It should look [like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/redLEDConnection.png).
    6. Do the same thing as the previous step, but instead with the jumper wire connected to GPIO 18 and with the green LED. It should look [like this](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/green-LED-connection.png).
    7. Connect the rainbow-colored 40-pin ribbon cable to the T-shaped board that you plugged into the breadboard. It's keyed with a notch on one side, so there's only one way to plug it in.
    8. Plug the other side of the cable into the Raspberry Pi's GPIO pins with the notch facing inwards [like so](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/ribbon-cable-connection-to-pi2.png). Here's what the other side [looks like](https://github.com/3rian-exe/bnydc-shuttle-bus-id-scanner/blob/main/images/ribbon-cable-connection-to-pi1.png).
    9. Troubleshooting: If none of the LEDs light up, verify that the LED diodes are inserted in the correct way, as stated in step 5. If this were the case, the LED(s) could have been burned out and likely need to be replaced.

