import threading
import time
import datetime
import logging

import pygame
import random

from queue import Queue
from pygame import mixer

from pygame.locals import *

pygame.init()
mixer.init()

# -------------- variables Init -----------

win_x = 600
win_y = 700
player_loc_x = 300
player_loc_y = 650
ini = 0
img = 0
pressed = False
stop_all = False

player_width = 20
player_height = 30

# ----------- User can change these variables -------------
velocity = 1
fps = 30
game_time_limit = 90
# ----------------------------------------------------------

doll_sleep_values = [i for i in range(1, 10, 1)]

doll = [pygame.image.load('doll_images/doll_front.png'),
        pygame.image.load('doll_images/doll_back.png')]

lights = [pygame.image.load('lights/red.png'),
          pygame.image.load('lights/green.png')]

black = [pygame.image.load('doll_images/black.png')]

clock = pygame.time.Clock()
win = pygame.display.set_mode((win_x, win_y))
pygame.display.set_caption("Red Light Green Light")

p_Q = Queue()
p_Q.put([player_loc_x, player_loc_y])

logging.basicConfig(filename='game.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def print_message(message):

    pygame.draw.rect(win, (0, 0, 0), (0, 20, 120, 50))
    font = pygame.font.Font('freesansbold.ttf', 25)
    message = font.render(message, True, (255, 255, 0))
    win.blit(message, (5, 20))
    pygame.display.update()


def get_doll():
    global ini

    if ini == 0:
        ini = 1
    else:
        ini = 0
    return ini


def doll_handling():

    global img
    global stop_all

    while not stop_all:
        img = get_doll()
        win.blit(black[0], (230, 0))
        win.blit(doll[img], (230, 0))
        win.blit(lights[img], (450, 0))
        if img == 0:
            mixer.music.pause()
        pygame.display.update()
        sleep_value = random.choice(doll_sleep_values)
        pygame.time.wait(sleep_value * 1000)
        mixer.music.unpause()
    logging.info('doll killed')
    mixer.music.pause()


def player_handling(q):

    global stop_all

    old_pos = [0, 0]
    logging.info('player thread starting')
    while not stop_all:
        player_loc = q.get()
        if player_loc != old_pos:
            pygame.draw.rect(win, (0, 0, 0), (old_pos[0], old_pos[1], player_width, player_height))
            pygame.display.update()

        pygame.draw.line(win, (255, 255, 0), (0, 150), (600, 150))
        pygame.draw.rect(win, (255, 0, 0), (player_loc[0], player_loc[1], player_width, player_height))
        pygame.display.update()
        logging.info('player updated')

        old_pos = player_loc.copy()
    logging.info('player killed')


def start_timer():
    global stop_all
    for i in range(game_time_limit):
        pygame.time.wait(1000)
        print_message(str(datetime.timedelta(seconds=game_time_limit-i)))
        if stop_all:
            break
    logging.info('timer completed')
    stop_all = True


def init_handling(p_q):

    global player_loc_x
    global player_loc_y
    global pressed
    global stop_all
    global img

    mixer.music.load("music/music.mp3")
    mixer.music.play(-1)
    run = True

    while run:
        logging.info(f'In init handling {img}')
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            logging.info('LEFT')
            pressed = True
            if player_loc_x > 0:
                player_loc_x -= velocity
        if keys[pygame.K_RIGHT]:
            logging.info('RIGHT')
            pressed = True
            if player_loc_x < win_x - player_width and player_loc_x + velocity <= win_x - player_width:
                player_loc_x += velocity
        if keys[pygame.K_UP]:
            logging.info('UP')
            pressed = True
            if player_loc_y > 0:
                player_loc_y -= velocity
        if keys[pygame.K_DOWN]:
            logging.info('DOWN')
            pressed = True
            if player_loc_y < win_y - player_height and player_loc_y + velocity <= win_y - player_height:
                player_loc_y += velocity
        p_location = [player_loc_x, player_loc_y]

        # This can be refactored
        if pressed or stop_all:
            p_q.put(p_location)
            pressed = False
            if player_loc_y <= 150:
                stop_all = True
                time.sleep(1)
                win.fill((0, 0, 0))
                print_message('You won. Press q to Quit or r to restart')
                logging.info('You won. Press q to Quit or r to restart')
            elif img == 0 or stop_all:
                mixer.music.pause()
                stop_all = True
                time.sleep(1)
                win.fill((0, 0, 0))
                print_message('YOU ARE DEAD. Press q to Quit or r to restart')
                logging.info('YOU ARE DEAD. Press q to Quit or r to restart')

            while stop_all:
                keys = pygame.key.get_pressed()
                event = pygame.event.wait()
                if event.type == K_r or keys[pygame.K_r]:
                    win.fill((0, 0, 0))
                    print_message('Please wait Game Initializing')
                    logging.info('Please wait Game Initializing')
                    player_loc_x = 300
                    player_loc_y = 600
                    p_q.put([player_loc_x, player_loc_y])
                    time.sleep(10)
                    win.fill((0, 0, 0))
                    pygame.display.update()
                    inner_timer_thread = threading.Thread(target=start_timer, daemon=True)
                    inner_player_thread = threading.Thread(target=player_handling, args=(p_Q,), daemon=True)
                    inner_doll_thread = threading.Thread(target=doll_handling, daemon=True)
                    stop_all = False
                    inner_timer_thread.start()
                    inner_player_thread.start()
                    inner_doll_thread.start()
                    mixer.music.unpause()
                    break
                if event.type == K_q or keys[pygame.K_q]:
                    run = False
                    break
    pygame.quit()


timer_thread = threading.Thread(target=start_timer, daemon=True)
init_thread = threading.Thread(target=init_handling, args=(p_Q,))
player_thread = threading.Thread(target=player_handling, args=(p_Q,), daemon=True)
doll_thread = threading.Thread(target=doll_handling, daemon=True)

init_thread.start()
timer_thread.start()
player_thread.start()
doll_thread.start()
logging.info('All threads started')
