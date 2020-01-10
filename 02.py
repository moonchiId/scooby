import pygame
from pygame.locals import *
import random
import datetime
import time
import multiprocessing as mp


def blinks_detector(quit_program, blink_det, blinks_num, blink):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        #print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()

    if __name__ == '__main__':
        clock = pg.time.Clock()

        frt = flt.FltRealTime()
        brt = blk.BlinkRealTime()

        if SYMULACJA_SYGNALU:
            df = pd.read_csv('dane_do_symulacji/data.csv')
            for sample in df['signal']:
                if quit_program.is_set():
                    break
                detect_blinks(sample)
                clock.tick(200)
            print('KONIEC SYGNAŁU')
            quit_program.set()
        else:
            board = OpenBCIGanglion(mac=mac_adress)
            board.start_stream(detect_blinks)

blink_det = mp.Queue()
blink = mp.Value('i', 0)
blinks_num = mp.Value('i', 0)
connected = mp.Event()
quit_program = mp.Event()

proc_blink_det = mp.Process(
    name='proc_',
    target=blinks_detector,
    args=(quit_program, blink_det, blinks_num, blink,)
    )

# rozpoczęcie podprocesu
proc_blink_det.start()
print('subprocess started')



#stałe
SCREEN_WIDTH = 675
SCREEN_HEIGHT = 400
ROAD_HEIGHT = 250
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 25
DINO_POS_X = 60
DINO_POS_Y = ROAD_HEIGHT - 18
CACTUS_POS_Y = ROAD_HEIGHT - 20

pygame.init()
gameDisplay = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Scooby Doo Game')
clock = pygame.time.Clock()
background = pygame.image.load('graphics/tlo.jpg')


dino_list = []
dino_list.append(pygame.image.load("graphics/scoobyjump.png")) #0
dino_list.append(pygame.image.load("graphics/scoobyrun1.png")) #1
dino_list.append(pygame.image.load("graphics/scoobyrun2.png")) #2
dino_list.append(pygame.image.load("graphics/scoobyjump.png")) #3
run_indx = 1

jumping = pygame.image.load('graphics/doo1.jpg')
character = pygame.image.load('graphics/doo1.jpg')
road1 = pygame.image.load('graphics/ziemia.png')
road2 = pygame.image.load('graphics/ziemia.png')
## inna droga ##
##road1 = pygame.image.load('graphics/background1.jpg').convert()
##road2 = pygame.image.load('graphics/background1.jpg').convert()

cactus_list = []
cactus_list.append(pygame.image.load("graphics/grave3.png")) #0
cactus_list.append(pygame.image.load("graphics/hand.png")) #1
cactus_list.append(pygame.image.load("graphics/grave.png")) #2
cactus_list.append(pygame.image.load("graphics/grave3.png")) #3

road1_pos_x = 0
road2_pos_x = 600


speed_was_up = True
clear_game = True
game_on = False
lost_game = True
dino_jump = False
jump_height = 7
points = 0

frames_since_cactus = 0
gen_cactus_time = 50 #moment wygenerowania pierwszego kaktusa


#napisy

font = pygame.font.SysFont("Times New Roman", 18)
points_font = pygame.font.SysFont('Times New Roman', 16)
startScreen = font.render('NACIŚNIJ SPACJĘ ABY ZACZĄĆ', True, WHITE, BLACK)
startScreenRect = startScreen.get_rect()
startScreenRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2-50)



gra_trwa = True
while gra_trwa:
    if blink.value == 1:
        if dino_jump == False:
            game_on = True
            dino_jump = True
            ##jumpSound.play()
            blink.value = 0
        if lost_game == True:
            time.sleep(1)
            clear_game = True
            lost_game = False
            blink.value = 0
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit_program.set()
                pygame.quit()
                quit()
                gra_trwa = False
            if event.key == pygame.K_SPACE and dino_jump == False:
                game_on = True
                dino_jump = True
                ##jumpSound.play()
            if lost_game == True and event.key == pygame.K_SPACE:
                time.sleep(1)
                clear_game = True
                lost_game = False

    #ustawienia początkowe
    if clear_game == True:
        FPS = 25
        cactus_pos_x = []
        curr_cactus = []
        speed = 10
        points = 0
        clear_game = False

    #początkowy ekran
    gameDisplay.fill(BLACK)
    gameDisplay.blit(background,(0,0))
    gameDisplay.blit(road1, (road1_pos_x, ROAD_HEIGHT))
    if game_on == False:
        gameDisplay.blit(startScreen, startScreenRect)

    #przegrany ekran
    if game_on == True and lost_game == True:
        gameDisplay.blit(startScreen, startScreenRect)
        lostScreen = font.render('LICZBA SCOOBY CHRUPEK: ' + str(points), True, WHITE, BLACK)
        lostScreenRect = lostScreen.get_rect()
        lostScreenRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2-25)
        gameDisplay.blit(lostScreen, lostScreenRect)

    #zwiększanie prędkości gry
    if speed_was_up == False and points%5 == 0:
        ##checkpointSound.play()
        FPS += 5
        speed_was_up = True
    if points%5 == 1:
        speed_was_up = False

    #wyświetlanie punktów
    if game_on == True:
        pointsDisplay = points_font.render('SCOOBY-CHRUPKI: ' + str(points), True, WHITE, BLACK)
        pointsRect = pointsDisplay.get_rect()
        pointsRect.center = (SCREEN_WIDTH-100, 10)
        gameDisplay.blit(pointsDisplay, pointsRect)


    #dino biegnie, jedna animacja powinna trwać 3 klatki
    if game_on == True and dino_jump == False and lost_game == False:
        if run_indx <= 3:
            dino = gameDisplay.blit(dino_list[1], (DINO_POS_X, DINO_POS_Y))
            run_indx += 1
        elif run_indx < 6:
            dino = gameDisplay.blit(dino_list[2], (DINO_POS_X, DINO_POS_Y))
            run_indx += 1
        else:
            dino = gameDisplay.blit(dino_list[2], (DINO_POS_X, DINO_POS_Y))
            run_indx = 1
    elif game_on == False:
        dino = gameDisplay.blit(dino_list[0], (DINO_POS_X, DINO_POS_Y))

    #dino skacze
    if game_on == True and dino_jump == True:
        if jump_height >= -7:
            going_up = 1
            if jump_height < 0:
                going_up = -1
            DINO_POS_Y -= (jump_height ** 2) * 0.8 * going_up
            jump_height -= 1
        else:
            dino_jump = False
            jump_height = 7
        dino = gameDisplay.blit(dino_list[0], (DINO_POS_X, DINO_POS_Y))

    #przewijanie drogi
    if game_on == True:
        frames_since_cactus += 1
        road1_pos_x -= speed
        if road1_pos_x <= -SCREEN_WIDTH:
            gameDisplay.blit(road2, (road2_pos_x, ROAD_HEIGHT))
            road2_pos_x -= speed
            if road2_pos_x == 0:
                road2_pos_x = 600
                road1_pos_x = 0

    #przeszkody
    if frames_since_cactus == gen_cactus_time:
        gen_cactus_time = random.randint(30, 50) #nowa przeszkoda generowana jest raz na 20 do 50 klatek
        gen_cactus_img = random.randint(0, 3)
        frames_since_cactus = 0
        curr_cactus.append([gen_cactus_img, SCREEN_WIDTH]) #każdy kaktus ma [swój obrazek, swoją pozycję x]

    for i in range(len(curr_cactus)):
        if curr_cactus[i][0] == 0 or curr_cactus[i][0] == 3: #obniżenie położenia Y mniejszych kaktusów
            lower = 12
        else: lower = 0
        cactus = gameDisplay.blit(cactus_list[curr_cactus[i][0]], (curr_cactus[i][1], CACTUS_POS_Y+lower))
        curr_cactus[i][1] -= speed
        #punkty
        if curr_cactus[i][1] == 0:
            points += 1
        #zderzenie
        if dino.colliderect(cactus):
            speed = 0
            ##if lost_game == False:
                ##dieSound.play()
            lost_game = True
            dino = gameDisplay.blit(dino_list[3], (DINO_POS_X, DINO_POS_Y))
            #informacja o momencie zderzenia
            #print(str(datetime.datetime.now().time()) + " punkty: " + str(points))


    pygame.display.update()
    clock.tick(FPS)

proc_blink_det.join()
