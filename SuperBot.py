# -*- coding: utf-8 -*-

import json
import os
import time

import psutil
import pyautogui

import keyboard #Using module keyboard

import random
import sys
from threading import Thread

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

from pytesseract import image_to_string

CH2_url = 'steam://rungameid/629910'

PROCNAME = "ClickerHeroes2.exe"
start_state = "HELLO"
play_state = "PLAYING"
play_timer_max = 60 * 3

state = start_state
takeScrenshot = False

timer = 0.0


def getConfig():
    with open('config.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data

global screen

def initScreen():
    screen = pyautogui.screenshot()

initScreen()

def getpixel(x, y, newshot):
    #print('New Screen')
    return pyautogui.screenshot().getpixel((x, y))
    # else:
    #     try:
    #         #print('Old Screen')
    #         return screen.getpixel((x, y))
    #     except NameError:
    #         #print('New Screen')
    #         return pyautogui.screenshot().getpixel((x, y))




def pixelMatchesColor(x, y, expectedRGBColor, tolerance=0, newshot=True):
    pix = getpixel(x,y, newshot)
    if len(pix) == 3 or len(expectedRGBColor) == 3:  # RGB mode
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4:  # RGBA mode
        r, g, b, a = pix
        exR, exG, exB, exA = expectedRGBColor
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance) and (
            abs(a - exA) <= tolerance)
    else:
        assert False, 'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s' % (
            len(pix), len(expectedRGBColor))


def printScreen(message):
    if takeScrenshot:
        if not os.path.exists(debug_directory):
            os.makedirs(debug_directory)
        pyautogui.screenshot('{}/{}{}.png'.format(debug_directory, time.strftime("%m.%d %H.%M.%S", time.gmtime()), message))


def changeState(value):
    global state, timer
    state = value
    timer = 0


def killGame():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            proc.kill()

def matchesButton(position):
    if pixelMatchesColor(position[0], position[1], white_button,
                      tolerance=color_tolerance,newshot=False) or pixelMatchesColor(position[0],
                                                                      position[1],
                                                                      gray_button,
                                                                      tolerance=color_tolerance,newshot=False) \
    or pixelMatchesColor(position[0],
                         position[1],
                         super_white_button,
                         tolerance=color_tolerance,newshot=False) or pixelMatchesColor(
        position[0], position[1], energy_jar_color, tolerance=color_tolerance,newshot=False):
        return True
    return False

def isGameRunning():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            return True
        else:
            return False

def checkTimer():
    global state
    if state == loading_state and timer > loading_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)
    elif state == matching_state and timer > matching_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)
    elif state == play_state and timer > play_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)
    elif state == gameloading_state and timer > gameloading_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)


config = getConfig()

# Menu
print('By using this software you agree with license! You can find it in code.')

takeScrenshot = False

# Position init
text_position = (config['text']['x'], config['text']['y'])
resume_button_position = (config['resume_button_position']['x'], config['resume_button_position']['y'])
ruby_position = (config['ruby_position']['x'], config['ruby_position']['y'])
buy_new_stuff_position = (config['buy_new_stuff']['x'], config['buy_new_stuff']['y'])
energy_jar_position_top = (config['energy_jar_position_top']['x'], config['energy_jar_position_top']['y'])
energy_jar_position_bottom = (config['energy_jar_position_bottom']['x'], config['energy_jar_position_bottom']['y'])
reload_battery_position = (config['reload_battery_position']['x'], config['reload_battery_position']['y'])
totem_mana_position_droite = (config['totem_mana_droite']['x'], config['totem_mana_droite']['y'])
totem_mana_position_gauche = (config['totem_mana_gauche']['x'], config['totem_mana_gauche']['y'])
can_reload_position = (config['can_reload']['x'], config['can_reload']['y'])
the_fish_right = (config['the_fish_right']['x'], config['the_fish_right']['y'])
piece_right_1 = (config['piece_right_1']['x'], config['piece_right_1']['y'])
piece_right_2 = (config['piece_right_2']['x'], config['piece_right_2']['y'])
piece_right_3 = (config['piece_right_3']['x'], config['piece_right_3']['y'])
piece_right_4 = (config['piece_right_4']['x'], config['piece_right_4']['y'])

# Reading timings
wait_after_killing_a_game = config["timers"]["wait_after_killing_a_game"]
start_delay = config["timers"]["start_delay"]
animation_delay = config["timers"]["animation_delay"]
wait_for_players = config["timers"]["wait_for_players"]
wait_for_plain = config["timers"]["wait_for_plain"]
exit_animation_delay = config["timers"]["exit_animation_delay"]
loading_delay = config["timers"]["loading_delay"]

# Colors
def getColor(config, name):
    return (config["colors"][name]["r"], config["colors"][name]["g"], config["colors"][name]["b"])


color_tolerance = config["color_tolerance"]
energy_jar_top_white = getColor(config, "energy_jar_top_white")
energy_jar_bottom_blue = getColor(config, "energy_jar_bottom_blue")
super_white_button = getColor(config, "super_white_button")
ruby_color = getColor(config, "ruby_color")
can_buy_color = getColor(config, "buy_upgrade_color")
totem_mana_color = getColor(config, "totem_mana_color")
can_reload_color = getColor(config, "can_reload_color")
the_fish_color = getColor(config, "the_fish_color")
piece_color = getColor(config, "piece_color")



def CheckIfPause():
    #print('CheckIfPause')
    if pixelMatchesColor(text_position[0], text_position[1], super_white_button, tolerance=color_tolerance,newshot=True):
        print('Jeu actuellement en pause')
        pyautogui.click(resume_button_position[0], resume_button_position[1])

def CheckTabNeeded():
    #print('CheckTabNeeded')
    CheckIfPause()
    if pixelMatchesColor(ruby_position[0], ruby_position[1], ruby_color, tolerance=color_tolerance,newshot=True):
        # pyautogui.press('tab')
        print('wait')
        time.sleep(animation_delay)

def CheckBetterUpgradeAvalaible(checkNumber):
    #print('CheckBetterUpgradeAvalaible')
    CheckTabNeeded()
    numb = 1
    for access in config['accessoires']:
        if pixelMatchesColor(access['x'], access['y'], can_buy_color, tolerance=color_tolerance,newshot=False):
            if numb < checkNumber:
                return True
            else:
                return False
        numb += 1

def BuyUpgrade():
    #print('BuyUpgrade')
    CheckTabNeeded()
    number = 1
    for access in config['accessoires']:
        if pixelMatchesColor(access['x'], access['y'], can_buy_color, tolerance=color_tolerance,newshot=False):
            print('{}. {}'.format(number, access['name']))
            while pixelMatchesColor(access['x'], access['y'], can_buy_color, tolerance=color_tolerance,newshot=False):
                BuyNewStuff()
                #print('BuyedUpgrade')
                pyautogui.click(access['x'], access['y'])
                # if CheckBetterUpgradeAvalaible(number) == True:
                    # break
            break
        number += 1
    BuyNewStuff()

def BuyNewStuff():
    #print('BuyNewStuff')
    CheckTabNeeded()
    if pixelMatchesColor(buy_new_stuff_position[0], buy_new_stuff_position[1], can_buy_color, tolerance=color_tolerance,newshot=True):
        #print('BuyedNewStuff')
        pyautogui.click(buy_new_stuff_position[0], buy_new_stuff_position[1])


def Attack():
    #print('Attack')
    CheckIfPause()
    isImportantItem()
    #print('Spell Attack')
    pyautogui.click(1275, 1035)
    while not pixelMatchesColor(energy_jar_position_bottom[0], energy_jar_position_bottom[1], energy_jar_bottom_blue, tolerance=5,newshot=False):
        i = 0
        while i < 10:
            #print('Attacked')
            pyautogui.press('w')
            i += 1
        ReloadBattery()
        BuyUpgrade()

def ReloadBattery():
    #print('ReloadBattery')
    CheckIfPause()
    if not pixelMatchesColor(can_reload_position[0], can_reload_position[1], can_reload_color, tolerance=5,newshot=False) and not pixelMatchesColor(reload_battery_position[0], reload_battery_position[1], super_white_button, tolerance=5,newshot=True):
        #print('BatteryReloaded')
        pyautogui.click(reload_battery_position[0], reload_battery_position[1])

def isImportantItem():
    #print('isImportantItem')
    if pixelMatchesColor(the_fish_right[0], the_fish_right[1], the_fish_color, tolerance=color_tolerance,newshot=True):
        #print('Founded item')
        pyautogui.click(the_fish_right[0], the_fish_right[1])
    elif pixelMatchesColor(piece_right_1[0], piece_right_1[1], piece_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(piece_right_1[0], piece_right_1[1])
    elif pixelMatchesColor(piece_right_2[0], piece_right_2[1], piece_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(piece_right_2[0], piece_right_2[1])
    elif pixelMatchesColor(piece_right_3[0], piece_right_3[1], piece_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(piece_right_3[0], piece_right_3[1])
    elif pixelMatchesColor(piece_right_4[0], piece_right_4[1], piece_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(piece_right_4[0], piece_right_4[1])
    elif pixelMatchesColor(piece_right_4[0], piece_right_4[1], piece_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(piece_right_4[0], piece_right_4[1])
    else:
        isTotemMana()

def isTotemMana():
    #print('isTotemMana')
    if pixelMatchesColor(totem_mana_position_droite[0], totem_mana_position_droite[1], totem_mana_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(totem_mana_position_droite[0], totem_mana_position_droite[1])
        ReloadBattery()
    elif pixelMatchesColor(totem_mana_position_gauche[0], totem_mana_position_gauche[1], totem_mana_color, tolerance=color_tolerance,newshot=False):
        #print('Founded item')
        pyautogui.click(totem_mana_position_gauche[0], totem_mana_position_gauche[1])
        ReloadBattery()



# class Attack(Thread):
#
#     def __init__(self):
#         Thread.__init__(self)
#
#     def run(self):
#         while True:
#             if keyboard.is_pressed('d'):#if key 'q' is pressed
#                 #print('You Pressed D Key!')
#                 break#finishing the loop
#             else:
#                 pyautogui.press('w')
#                 time.sleep(animation_delay)
# # Création des threads
# thread_1 = Attack()
#
# # Lancement des threads
# thread_1.start()
#
# # Attend que les threads se terminent
# thread_1.join()





# Game info
while (1):
    if state == start_state:
        try:
            already_lauch = False
            for proc in psutil.process_iter():
                if proc.name() == PROCNAME:
                    already_lauch = True
            if already_lauch:
                changeState(play_state)
                print("ClickerHeroes2 already launched")
            else:
                print("ClickerHeroes2 need to be launched")
                os.startfile(CH2_url)
                time.sleep(start_delay)
                changeState(start_state)
        except Exception as ex:
            print('Something went wrong while starting ClickerHeroes2... Error message: {}'.format(ex))
    elif state == play_state:
        #print('On recommence')
        CheckIfPause()
        CheckTabNeeded()
        BuyNewStuff()
        BuyUpgrade()
        Attack()
        ReloadBattery()
