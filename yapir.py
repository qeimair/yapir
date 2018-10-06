import os
import sys
from subprocess import call
from mpd import MPDClient
from PersistentMPDClient.PersistentMPDClient import PersistentMPDClient
import pifacecad
from  time import sleep

backlight = 1       # Radio starts with display light on
status = "playing"  # Set starting status on Playing
channel_pos = 0
# Update display and perform action depending on button pressed
def update_pin_text(event):
        global channel_pos
        global status

        if(event.pin_num == 0 ) :
                if status == "playing" :
                             currentsong = client.currentsong()         # if playback on and play button pressed show current song title
                             cadline = (currentsong['title'])
                             cadlinelen = len(cadline)
                             for i in range(0,cadlinelen-14) :          # scrolling song title!
                                      cadline2 = cadline[i:i+16]
                                      cad.lcd.set_cursor(0,1)
                                      cad.lcd.write(cadline2[0:15])
                                      sleep(.2)
                             sleep(.5)
                             init_display()
                             display_channel()
                             display_playlist()
                else :
                             client.play()
                             status = "playing"
                             event.chip.lcd.set_cursor(0,1)
                             event.chip.lcd.write_custom_bitmap(1)
                             event.chip.lcd.write(" ")
                             display_channel()
                             display_playlist()

        elif(event.pin_num == 1) :
                if status == "playing" :                     # stops playback
                              client.stop()
                              event.chip.lcd.set_cursor(0,1)
                              event.chip.lcd.write_custom_bitmap(2)
                              event.chip.lcd.write(" ")
                              clear_channel()
                              status = "stopped"
                else :                                       # closes the program if stop button is pressed when playback already stopped it closes the program
                              cad.lcd.backlight_off()
                              cad.lcd.clear()
                              os._exit(0)

        elif(event.pin_num == 2 and status == "playing"):    # skips to previous radio channel
                client.previous()
                clear_channel()
                display_channel()
                display_playlist()

        elif(event.pin_num == 3 and status == "playing"):    # skips to next radio channel
                client.next()
                clear_channel()
                display_channel()
                display_playlist()

        elif(event.pin_num == 4):
                global backlight                             # handle backlight on/off
                if(backlight == 1):
                        event.chip.lcd.backlight_off()
                        backlight = 0
                else:
                        event.chip.lcd.backlight_on()
                        backlight = 1

        elif(event.pin_num == 5):
                sleep(1)

        elif(event.pin_num == 6):                            # handles volume down
                playerstatus=client.status()
                volume = int((playerstatus['volume']))
                volume = volume-5
                client.setvol(volume)
                display_volume()

        elif(event.pin_num == 7):                            # handles volume down
                playerstatus=client.status()
                volume = int((playerstatus['volume']))
                volume = volume+5
                client.setvol(volume)
                display_volume()
        else:
                sleep(0.1)

# Define and store custom bitmaps to be displayed
def custom_bitmaps():
        speaker = pifacecad.LCDBitmap([1,3,15,15,15,3,1,0])
        play = pifacecad.LCDBitmap([0,8,12,14,12,8,0,0])
        stop = pifacecad.LCDBitmap([0,31,31,31,31,31,0,0])
        playlist = pifacecad.LCDBitmap([2,3,2,2,14,30,12,0])

        cad.lcd.store_custom_bitmap(0, speaker)
        cad.lcd.store_custom_bitmap(1, play)
        cad.lcd.store_custom_bitmap(2, stop)
        cad.lcd.store_custom_bitmap(3, playlist)

# Init display by showing idle state
def init_display():
        cad.lcd.blink_off()
        cad.lcd.cursor_off()
        cad.lcd.clear()
        cad.lcd.set_cursor(11,1)
        cad.lcd.write_custom_bitmap(0)
        display_volume()

# Retrieve and display radio channel
def display_channel():
       currentsong=client.currentsong()
       channel = (currentsong['name'])
       cad.lcd.set_cursor(0,0)
       cad.lcd.write(channel)

# Write an empty row
def clear_channel():
        cad.lcd.set_cursor(0,0)
        cad.lcd.write("                ")

# Retrieve radio playlist number and size and display
def display_playlist():
        playerstats=client.status()
        playlist = (playerstats['song'])
        cad.lcd.set_cursor(4,1)
        cad.lcd.write_custom_bitmap(3)
        cad.lcd.write(playlist)

# Retrieve volume level from mpc and display
def display_volume():
        playerstatus=client.status()
        volume = (playerstatus['volume'])
        cad.lcd.set_cursor(12,1)
        cad.lcd.write(volume)

cad = pifacecad.PiFaceCAD()         # creating Pifacecad object
cad.lcd.backlight_on()              # put the lcd backlight on
client = MPDClient()                # create MPD client object
client.timeout = 1000               # setting network timeout in seconds
client.idletimeout = None           # setting timeout timeout for fetching results
client.connect("localhost", 6600)   # connect to localhost:6600
client.play()                       # starts playing
custom_bitmaps()                    # defines simple char bitmaps to be shown on the display
init_display()                      # initialise the display
display_channel()                   # shows current radio station on display

listener = pifacecad.SwitchEventListener(chip=cad) # listens to button pressed

for i in range(8):
        listener.register(i,pifacecad.IODIR_FALLING_EDGE,       update_pin_text)

listener.activate()
