from adafruit_max7219 import matrices
from board import TX, RX, A2, A0, BUTTON_A, BUTTON_B, SPEAKER_ENABLE
import busio
import digitalio
import time
import random
import audioio
from microcontroller import reset

clk = RX
din = TX
cs = digitalio.DigitalInOut(A2)

spi = busio.SPI(clk, MOSI=din)
display = matrices.Matrix8x8(spi, cs)

spkrenable = digitalio.DigitalInOut(SPEAKER_ENABLE)
spkrenable.switch_to_output()
spkrenable.value = True

btn_a = digitalio.DigitalInOut(BUTTON_A)
btn_b = digitalio.DigitalInOut(BUTTON_B)
btn_a.switch_to_input(pull=digitalio.Pull.DOWN)
btn_b.switch_to_input(pull=digitalio.Pull.DOWN)

def play_file(filename):
    f = open(filename, "rb")
    a = audioio.AudioOut(A0, f)
    a.play()
    while a.playing:
        pass
    f.close()
    
def picread(file):
    f = open(file, 'rt')
    picdata = []
    sordata = []
    pics = []
    piccs = []
    for sor in f:
        sor = sor.strip().split()
        sordata.append(sor)
    f.close()
    for i in range(len(sordata)):
        for pix in range(len(sor)):
            if sordata[i][pix] != '0':
                pic_color = 1
            elif sordata[i][pix] == '0':
                pic_color = 0
            picdata.append(pic_color)
    for y in range(8):
        for x in range(8):
            piccs.append([x, y])
    for i in range(len(picdata)):
        pics.append([piccs[i][0], piccs[i][1], picdata[i]])
    return pics
    
def picdraw(pics):
    pics = picread(pics)
    for i in pics:
        display.pixel(i[0], i[1], i[2])
    display.show()

def scroll_txt(txt, speed):
    display.clear_all()
    for c in range(len(txt)*8):
        display.fill(0)
        display.text(txt, -c, 0)
        display.show()
        time.sleep(speed)
        
def scrollup_txt(txt, speed):
    display.clear_all()
    for c in range(-8, len(txt)):
        display.fill(0)
        display.text(txt, 0, -c)
        display.show()
        time.sleep(speed)
        
def scrolldown_txt(txt, speed):
    display.clear_all()
    for c in range(-6, len(txt)*12):
        display.fill(0)
        display.text(txt, 0, c)
        display.show()
        time.sleep(speed)

def pad(pos):
    display.pixel(pos, 7, 1)
    display.pixel(pos+1, 7, 1)
        
def enemies():
    for i in range(2):
        display.pixel(BOMB1_x+i, 0, 1)
        display.pixel(BOMB2_x+i, 1, 1)
        
def bomb():
    display.pixel(BOMB1_x, BOMB1_y, 1)
    display.pixel(BOMB2_x, BOMB2_y, 1)
        
def enemy_line():    
    for i in range(8):
        display.pixel(i, BOMB1_y, 1)
    display.pixel(BOMB_x, BOMB1_y, 0)
    display.pixel(BOMB_x+1, BOMB1_y, 0)
    
def boom():
    for a in range(5):
        picdraw('skull1.txt')
        time.sleep(.08)
        display.fill(0)
        display.show()
        time.sleep(.08)

pos = 2
BOMB_x = random.randint(0, 6)
BOMB1_x, BOMB1_y = random.randint(0, 7), 0
BOMB2_x, BOMB2_y = random.randint(0, 7), 1
score = 0
lives = 3
extra_game = False

while True:
    display.clear_all()
    display.brightness(5)
    scroll_txt(' METEOR ', .05)
    scroll_txt('press ', .05)
    scrollup_txt('A', .05)
    while btn_a.value is False:
        display.show()
    else:
        scrolldown_txt('3', .05)
        time.sleep(.30)
        scrolldown_txt('2', .05)
        time.sleep(.30)
        scrolldown_txt('1', .05)
        time.sleep(.30)
        break
    
while True:
    display.clear_all()
    if btn_a.value is True and pos > 0:
        pos -= 1
    if btn_b.value is True and pos < 6:
        pos += 1
    if lives == 0:
        scroll_txt('GameOver Score '+str(score), .05)
        reset()
    if extra_game is False:
        pad(pos)
        bomb()
        enemies()
        if BOMB1_y == 7 and ((BOMB1_x == pos) or (BOMB1_x == pos+1)) or \
        BOMB2_y == 7 and ((BOMB2_x == pos) or (BOMB2_x == pos+1)):
            play_file('Beep8.wav')
            boom()
            lives -= 1
            time.sleep(.5)
    elif extra_game is True:
        pad(pos)
        enemy_line()
        if (pos != BOMB_x and BOMB1_y == 7):
            play_file('Beep8.wav')
            boom()
            lives -= 1
            time.sleep(.5)
    BOMB1_y += 1
    BOMB2_y += 1
    if BOMB1_y > 7:
        BOMB1_x, BOMB1_y = random.randint(0, 7), 0
    if BOMB2_y > 7:
        BOMB2_x, BOMB2_y = random.randint(0, 7), 1
        score += 1
        if score % 25 == 0:
            BOMB_x, BOMB1_y = random.randint(0, 6), 0
            extra_game = True
        else:
            extra_game = False
    display.show()
    time.sleep(.12)

    
    