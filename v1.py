#                        ,----..               
#     ,---,             /   /   \   .--.--.    
#  ,`--.' |  ,---,     /   .     : /  /    '.  
# /    /  :,---.'|    .   /   ;.  \  :  /`. /  
#:    |.' '|   | :   .   ;   /  ` ;  |  |--`   
#`----':  |:   : :   ;   |  ; \ ; |  :  ;_     
#   '   ' ;:     |,-.|   :  | ; | '\  \    `.  
#   |   | ||   : '  |.   |  ' ' ' : `----.   \ 
#   '   : ;|   |  / :'   ;  \; /  | __ \  \  | 
#   |   | ''   : |: | \   \  ',  / /  /`--'  / 
#   '   : ||   | '/ :  ;   :    / '--'.     /  
#   ;   |.'|   :    |   \   \ .'    `--'---'   
#   '---'  /    \  /     `---`                 
#          `-'----'                            
#i used https://patorjk.com/software/taag/ for the ascii art btw
#
#1bos v1
#you can sav as main.py also
#run with sudo python3 main.py (or whatever the heck you called it)

import time
import math
import traceback
from datetime import datetime, timezone, timedelta

import board
import neopixel
import gpiod


# ======================
# SETTINGS
# ======================

NUM_PIXELS = 10
BRIGHTNESS_CAP = 0.18
ROTATE = 2

DOUBLE_CLICK_TIME = 0.5
HOLD_TIME = 1.0


# ======================
# LOGGING
# ======================

def log(msg):
    print(f"[1bOS] {time.strftime('%H:%M:%S')} | {msg}")


# ======================
# LED
# ======================

pixels = neopixel.NeoPixel(
    board.D18,
    NUM_PIXELS,
    brightness=BRIGHTNESS_CAP,
    auto_write=False
)


BLACK  = (0,0,0)
RED    = (255,0,0)
GREEN  = (0,255,0)
YELLOW = (255,180,0)
BLUE   = (0,0,255)
WHITE  = (255,255,255)



def rotate(i):
    return (i + ROTATE) % NUM_PIXELS



def set_led(i,color):
    pixels[rotate(i)] = color



def clear():
    pixels.fill(BLACK)



def show():
    pixels.show()



def shutdown():
    log("Turning LEDs off")
    clear()
    show()



# ======================
# BUTTON
# ======================

chip = gpiod.Chip("/dev/gpiochip0")

button = chip.request_lines(
    consumer="1bOS-button",
    config={
        3: gpiod.LineSettings(
            direction=gpiod.line.Direction.INPUT,
            bias=gpiod.line.Bias.PULL_UP
        )
    }
)


log("Button ready")



def pressed():

    return (
        button.get_value(3)
        == gpiod.line.Value.INACTIVE
    )



# ======================
# CLOCK
# ======================

def swatch_beats():

    now = (
        datetime.now(timezone.utc)
        + timedelta(hours=1)
    )

    seconds = (
        now.hour*3600
        + now.minute*60
        + now.second
    )

    return int(seconds / 86.4) % 1000



def draw_clock():

    clear()

    value = f"{swatch_beats():03d}"


    set_led(
        int(value[0]),
        GREEN
    )

    set_led(
        int(value[1]),
        YELLOW
    )

    set_led(
        int(value[2]),
        RED
    )


    show()



# ======================
# TIMER
# ======================

timer_seconds = 0
timer_start = 0
timer_running = False

timer_finished = False
alarm_done = False



def remaining():

    global timer_running
    global timer_finished


    if not timer_running:
        return timer_seconds


    left = (
        timer_seconds
        - int(time.time()-timer_start)
    )


    if left <= 0:

        timer_running = False
        timer_finished = True

        log("Timer finished!")

        return 0


    return left



def add_minute():

    global timer_seconds

    timer_seconds += 60

    log(
        f"Timer set: {timer_seconds//60} min"
    )



def flash_alarm():

    global timer_seconds
    global timer_finished
    global alarm_done


    log("FLASHING ALARM")


    for i in range(3):

        pixels.fill(WHITE)
        show()

        time.sleep(.25)

        clear()
        show()

        time.sleep(.25)


    log("Alarm done")


    # reset everything

    timer_seconds = 0
    timer_finished = False
    alarm_done = False


    log("Timer reset to 0")



def draw_timer():

    clear()


    if timer_seconds == 0:

        show()
        return


    left = remaining()


    amount = math.ceil(
        (left / timer_seconds)
        * NUM_PIXELS
    )


    for i in range(amount):

        set_led(
            i,
            BLUE
        )


    show()



# ======================
# APPS
# ======================

apps = [
    "clock",
    "timer"
]


app_index = 0
mode = "clock"



def next_app():

    global app_index
    global mode


    old = mode


    app_index += 1


    if app_index >= len(apps):

        app_index = 0


    mode = apps[app_index]


    log(
        f"App: {old} -> {mode}"
    )


    # transition animation

    for i in range(NUM_PIXELS):

        clear()

        set_led(
            i,
            WHITE
        )

        show()

        time.sleep(.03)


    clear()
    show()



# ======================
# INPUT
# ======================

clicks = 0
last_click = 0



# ======================
# MAIN
# ======================

log("Ring Thing boot")
log("Starting clock")


try:

    while True:


        # alarm works anywhere

        if timer_finished and not alarm_done:

            alarm_done = True

            flash_alarm()



        if mode == "clock":

            draw_clock()


        elif mode == "timer":

            draw_timer()



        if pressed():

            log("Button pressed")


            start = time.time()


            while pressed():

                time.sleep(.01)


            held = time.time() - start


            log(
                f"Released after {held:.2f}s"
            )


            if held >= HOLD_TIME:

                next_app()



            else:

                now = time.time()


                if now-last_click <= DOUBLE_CLICK_TIME:

                    clicks += 1

                else:

                    clicks = 1


                last_click = now



                if clicks == 2:

                    clicks = 0

                    log("Double click")


                    if mode == "timer":

                        if timer_running:

                            timer_running = False

                            log("Timer paused")


                        else:

                            timer_finished = False

                            timer_running = True
                            timer_start = time.time()

                            log("Timer started")



        if (
            clicks == 1
            and time.time()-last_click > DOUBLE_CLICK_TIME
        ):

            clicks = 0

            log("Single click")


            if mode == "timer":

                add_minute()



        time.sleep(.05)



except KeyboardInterrupt:

    log("Shutdown")


except Exception:

    log("CRASH")

    traceback.print_exc()


finally:

    shutdown()
