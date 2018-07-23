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
CRASH_PROCNAME = "BroCrashReporter.exe"
debug_directory = "debug_screenshots"
start_state = "HELLO"
play_state = "PLAYING"
play_timer_max = 60 * 3
matching_state = "MATCHING"
matching_timer_max = 60 * 3
loading_state = "LOADING"
loading_timer_max = 60 * 3

state = start_state
takeScrenshot = False

timer = 0.0


def getConfig():
    with open('config.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data

def getpixel(x, y):
    return pyautogui.screenshot().getpixel((x, y))

def pixelMatchesColor(x, y, expectedRGBColor, tolerance=0):
    pix = getpixel(x,y)
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
                      tolerance=color_tolerance) or pixelMatchesColor(position[0],
                                                                      position[1],
                                                                      gray_button,
                                                                      tolerance=color_tolerance) \
    or pixelMatchesColor(position[0],
                         position[1],
                         super_white_button,
                         tolerance=color_tolerance) or pixelMatchesColor(
        position[0], position[1], energy_jar_color, tolerance=color_tolerance):
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
totem_mana_position = (config['totem_mana']['x'], config['totem_mana']['y'])
can_reload_position = (config['can_reload']['x'], config['can_reload']['y'])



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
dark_play_color = getColor(config, "dark_play_color")
play_color = getColor(config, "play_color")
matching_color = getColor(config, "matching_color")
matching_tick_color = getColor(config, "matching_tick_color")
white_button = getColor(config, "white_button")
gray_button = getColor(config, "gray_button")
energy_jar_top_white = getColor(config, "energy_jar_top_white")
energy_jar_bottom_blue = getColor(config, "energy_jar_bottom_blue")
super_white_button = getColor(config, "super_white_button")
windows_background = getColor(config, "windows_background")
exit_button_color = getColor(config, "exit_button_color")
reconnect_button_color = getColor(config, "reconnect_button_color")
ruby_color = getColor(config, "ruby_color")
can_buy_color = getColor(config, "buy_upgrade_color")
totem_mana_color = getColor(config, "totem_mana_color")
can_reload_color = getColor(config, "can_reload_color")

def CheckIfPause():
    if pixelMatchesColor(text_position[0], text_position[1], super_white_button, tolerance=color_tolerance):
        print('Jeu actuellement en pause')
        pyautogui.click(resume_button_position[0], resume_button_position[1])

def CheckTabNeeded():
    CheckIfPause()
    isTotemMana()
    if pixelMatchesColor(ruby_position[0], ruby_position[1], ruby_color, tolerance=color_tolerance):
        # pyautogui.press('tab')
        print('wait')
        time.sleep(animation_delay)

def CheckBetterUpgradeAvalaible(checkNumber):
    CheckTabNeeded()
    numb = 1
    for access in config['accessoires']:
        if pixelMatchesColor(access['x'], access['y'], can_buy_color, tolerance=color_tolerance):
            if numb < checkNumber:
                return True
            else:
                return False
        numb += 1

def BuyUpgrade():
    CheckTabNeeded()
    isTotemMana()
    ReloadBattery()
    number = 1
    for access in config['accessoires']:
        if pixelMatchesColor(access['x'], access['y'], can_buy_color, tolerance=color_tolerance):
            print('{}. {}'.format(number, access['name']))
            while pixelMatchesColor(access['x'], access['y'], can_buy_color, tolerance=color_tolerance):
                BuyNewStuff()
                pyautogui.click(access['x'], access['y'])
                isTotemMana()
                ReloadBattery()
                # if CheckBetterUpgradeAvalaible(number) == True:
                    # break
            break
        number += 1
    BuyNewStuff()

def BuyNewStuff():
    CheckTabNeeded()
    if pixelMatchesColor(buy_new_stuff_position[0], buy_new_stuff_position[1], can_buy_color, tolerance=color_tolerance):
        pyautogui.click(buy_new_stuff_position[0], buy_new_stuff_position[1])


def Attack():
    CheckIfPause()
    while not pixelMatchesColor(energy_jar_position_bottom[0], energy_jar_position_bottom[1], energy_jar_bottom_blue, tolerance=5):
        i = 0
        while i < 10:
            isTotemMana()
            pyautogui.press('w')
            i += 1
        ReloadBattery()
        BuyUpgrade()

def ReloadBattery():
    CheckIfPause()
    if not pixelMatchesColor(can_reload_position[0], can_reload_position[1], can_reload_color, tolerance=5) and not pixelMatchesColor(reload_battery_position[0], reload_battery_position[1], super_white_button, tolerance=5):
            pyautogui.click(reload_battery_position[0], reload_battery_position[1])



def isTotemMana():
    if pixelMatchesColor(totem_mana_position[0], totem_mana_position[1], totem_mana_color, tolerance=color_tolerance):
        pyautogui.click(totem_mana_position[0], totem_mana_position[1])
        ReloadBattery()


# class Attack(Thread):
#
#     def __init__(self):
#         Thread.__init__(self)
#
#     def run(self):
#         while True:
#             if keyboard.is_pressed('d'):#if key 'q' is pressed
#                 print('You Pressed D Key!')
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
    # try:
    #     for proc in psutil.process_iter():
    #         # check whether the process name matches
    #         if proc.name() == CRASH_PROCNAME:
    #             print('Fucking bugs in PUBG. Trying to avoid them!')
    #             proc.kill()
    #             killGame()
    #             time.sleep(wait_after_killing_a_game)
    #             changeState(start_state)
    # except Exception as ex:
    #     print('Something went wrong while killing bug reporter... Error message: {}'.format(ex))
    if state == start_state:
        # img = Image.open('C:/Users/Cr4zZyBipBiip/Downloads/botpubg-mpgh_mpgh.net/BOTClickHeroe2/test2.png')
        # text = image_to_string(img)
        # print(text)


        try:
            already_lauch = False
            for proc in psutil.process_iter():
                if proc.name() == PROCNAME:
                    already_lauch = True
            if already_lauch:
                changeState(loading_state)
                print("ClickerHeroes2 already launched")
            else:
                print("ClickerHeroes2 need to be launched")
                os.startfile(CH2_url)
                time.sleep(start_delay)
                changeState(start_state)
        except Exception as ex:
            print('Something went wrong while starting ClickerHeroes2... Error message: {}'.format(ex))
    elif state == loading_state:
        CheckIfPause()
        CheckTabNeeded()
        isTotemMana()
        BuyNewStuff()
        BuyUpgrade()
        Attack()
        ReloadBattery()