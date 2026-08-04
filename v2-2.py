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
#1bos v2.1
#you can sav as main.py also
#run with sudo python3 main.py (or whatever the heck you called it)
#2.0 stuff
#WEATHER APP!!!! LESGOOOO THIS TOOK SO LONG TO MAKE BUT I HAVENT EVEN TESTED BUT ITLL PROB WORK. IT DOES BC I JUST TESTED

#2.1 stuff
#made it not crash if u enter zip
#made it use farenheit for api requests bc thats what my code is for
#sorry euros

#2.2 stuff
#spinny game is newwwwww
#very fun 10/10

#2.21 stuff
#bugfixes

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
# WEATHER
# ======================

import requests


weather_location = None



GRAY = (100,120,130)
ORANGE = (255,100,0)
PURPLE = (180,0,255)
SNOW = (180,230,255)



# ----------------------
# LOCATION
# ----------------------

def find_weather_location():

    log("Finding location")


    # Try IP location

    try:

        r = requests.get(
            "https://ipapi.co/json/",
            timeout=4
        )

        data = r.json()


        lat = data["latitude"]
        lon = data["longitude"]


        log(
            "Location found by IP"
        )


        return (
            float(lat),
            float(lon)
        )


    except Exception:

        log(
            "IP location failed"
        )



    # Manual fallback

    print()
    print("Weather location needed")
    print()
    print("Enter ZIP code or lat,lon")


    value = input("> ").strip()



    # Latitude,Longitude input

    if "," in value:

        lat, lon = value.split(",")

        return (
            float(lat),
            float(lon)
        )



    # ZIP code input

    else:

        zip_code = value


        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "postalcode": zip_code,
                "format": "json"
            },
            headers={
                "User-Agent": "1bOS"
            },
            timeout=5
        )


        data = r.json()


        if len(data) == 0:

            raise Exception(
                "ZIP not found"
            )


        return (
            float(data[0]["lat"]),
            float(data[0]["lon"])
        )
# ======================
# WEATHER CACHE
# ======================

weather_cache = None
weather_last_update = 0

WEATHER_REFRESH_TIME = 180

def fetch_weather():

    global weather_cache
    global weather_last_update


    # Use cached weather if still fresh

    if (
        weather_cache is not None
        and time.time() - weather_last_update
        < WEATHER_REFRESH_TIME
    ):

        return weather_cache



    log("Updating weather")


    lat,lon = weather_location


    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude":lat,
            "longitude":lon,
            "current_weather":"true",
            "temperature_unit":"fahrenheit"
        },

        timeout=5
    )


    data = r.json()["current_weather"]


    weather_cache = (
        data["temperature"],
        data["weathercode"]
    )


    weather_last_update = time.time()


    log("Weather updated")

    log(f"Weather temp: {data['temperature']}F code: {data['weathercode']}")
    
    return weather_cache



# ----------------------
# TEMP DISPLAY
# ----------------------

def temperature_band(temp):


    if temp < 0:

        return (
            WHITE,
            -20,
            0
        )


    elif temp < 32:

        return (
            BLUE,
            0,
            32
        )


    elif temp <= 50:

        return (
            GREEN,
            32,
            50
        )


    elif temp <= 70:

        return (
            YELLOW,
            51,
            70
        )


    elif temp <= 90:

        return (
            ORANGE,
            71,
            90
        )


    elif temp < 110:

        return (
            RED,
            91,
            110
        )


    else:

        return (
            PURPLE,
            110,
            130
        )



# ----------------------
# WEATHER TYPE
# ----------------------

def weather_pixels(code):


    # sunny

    if code == 0:

        return (
            YELLOW,
            YELLOW
        )


    # cloudy

    elif code in [1,2,3]:

        return (
            GRAY,
            GRAY
        )


    # rain

    elif code in [
        51,53,55,
        61,63,65
    ]:

        return (
            GRAY,
            BLUE
        )


    # snow

    elif code in [
        71,73,75
    ]:

        return (
            GRAY,
            SNOW
        )


    # storm

    elif code in [
        95,96,99
    ]:

        return (
            GRAY,
            ORANGE
        )


    # unknown

    else:

        return (
            GRAY,
            GREEN
        )



# ----------------------
# WEATHER APP
# ----------------------

def draw_weather():


    global weather_location



    # find location

    if weather_location is None:


        log(
            "No weather location"
        )


        for c in [
            RED,
            GREEN,
            BLUE
        ]:

            pixels.fill(c)

            show()

            time.sleep(.3)


        clear()
        show()


        weather_location = (
            find_weather_location()
        )



    try:

        temp,code = fetch_weather()


    except Exception as e:


        log(
            "Weather error"
        )


        clear()


        set_led(
            0,
            RED
        )


        show()


        return



    clear()



    # pixel 1 + 2

    sky,event = weather_pixels(
        code
    )


    set_led(
        0,
        sky
    )


    set_led(
        1,
        event
    )



    # pixel 3

    color,low,high = temperature_band(
        temp
    )


    set_led(
        2,
        color
    )



    # pixels 4-10 meter


    percent = (
        temp-low
    )/(high-low)


    percent=max(
        0,
        min(1,percent)
    )


    filled=int(
        percent*7
    )


    for i in range(filled):

        set_led(
            i+3,
            color
        )


    show()

# ======================
# SPINNY GAME
# ======================

import random


spin_position = 0
spin_target = 5

spin_speed = 0.50
spin_level = 1

spin_score = 0
spin_highscore = 0

spin_running = True
spin_last_move = 0



def reset_spinny():

    global spin_position
    global spin_target
    global spin_speed
    global spin_level
    global spin_score
    global spin_running


    spin_position = 0

    spin_target = random.randint(
        0,
        NUM_PIXELS-1
    )


    spin_speed = 0.50
    spin_level = 1
    spin_score = 0

    spin_running = True


    log("Spinny reset")



def draw_spinny():

    clear()


    set_led(
        spin_target,
        RED
    )


    set_led(
        spin_position,
        GREEN
    )


    show()



def spinny_update():

    global spin_position
    global spin_last_move


    if not spin_running:
        return


    if time.time()-spin_last_move >= spin_speed:

        spin_position += 1


        if spin_position >= NUM_PIXELS:

            spin_position = 0


        spin_last_move = time.time()



def spinny_hit():

    global spin_score
    global spin_level
    global spin_speed
    global spin_target
    global spin_highscore


    # Correct click

    if spin_position == spin_target:

        spin_score += 1
        spin_level += 1


        # Make it 10% faster

        spin_speed *= 0.9


        log(
            f"Spinny hit! Level {spin_level}"
        )


        # New high score

        if spin_score > spin_highscore:

            spin_highscore = spin_score

            log(
                f"NEW HIGH SCORE: {spin_highscore}"
            )

            spinny_highscore_animation()


        # Pick new target

        spin_target = random.randint(
            0,
            NUM_PIXELS - 1
        )


        return True



    # Wrong click

    else:

        log(
            f"Spinny miss! Score {spin_score}"
        )


        # Good run animation

        if spin_score > 10:

            spinny_good_animation()


        else:

            red_flash()



        reset_spinny()


        return False


def spinny_good_animation():

    for i in range(NUM_PIXELS):

        clear()

        set_led(
            i,
            GREEN
        )

        show()

        time.sleep(.08)



def spinny_highscore_animation():

    for i in range(NUM_PIXELS):

        clear()

        set_led(
            i,
            YELLOW
        )

        show()

        time.sleep(.08)



def red_flash():

    for i in range(3):

        pixels.fill(RED)

        show()

        time.sleep(.2)

        clear()

        show()

        time.sleep(.2)



# ======================
# APPS
# ======================

apps = [
    "clock",
    "timer",
    "weather",
    "spinny"
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

        elif mode == "weather":

            draw_weather()

        elif mode == "spinny":

            spinny_update()
            draw_spinny()

      
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
            
            elif mode == "spinny":

                spinny_hit()


        time.sleep(.05)



except KeyboardInterrupt:

    log("Shutdown")


except Exception:

    log("CRASH")

    traceback.print_exc()


finally:

    shutdown()
