# 1bOS V1

![1bOS Ring Thing Logo](logo.jpg)

The source code for the **1bOS Ring Thing** (v1).

Feel free to open issues or submit pull requests if you want to add features, improvements, or fixes!

## Features

- Swatch Internet Time clock
- One-button navigation
- Timer app
- NeoPixel ring animations
- Low brightness mode
- Timer alarm flash

# Installation

Clone the repository:

```bash
git clone https://github.com/a9plus/1bOSV1.git
cd 1bOSV1
```

Install the required Python packages:

```bash
sudo pip3 install \
adafruit-blinka \
adafruit-circuitpython-neopixel \
Adafruit-Blinka-Raspberry-Pi5-Neopixel \
--break-system-packages
```

Run 1bOS:

```bash
sudo python3 main.py
```
If gpiod is not already installed:

```bash
sudo apt update
sudo apt install python3-libgpiod gpiod
```

# How to use 1bOS V1

## Clock App

When 1bOS boots, you will see green, yellow, and red LEDs.

These represent the three decimal digits of the current Swatch Internet Time. Some LEDs may overlap if multiple digits have the same value.

- Green = first digit
- Yellow = second digit
- Red = third digit

This is the default app when starting 1bOS.

## Switching Apps

To switch between the clock and timer apps:

1. Hold the button for about one second.
2. Release the button.
3. 1bOS will switch to the other app.

## Timer App

When opening the timer app, the LEDs will be blank.

Controls:

- **Single click:** Add 1 minute to the timer
- **Double click:** Start or pause the timer  
  (Two clicks within 500ms)

The blue LEDs show the remaining percentage of the timer.

When the timer finishes:
- The ring flashes white 3 times
- The timer resets back to 0

# Hardware Tested

## Confirmed working

- Raspberry Pi 5
  - Ubuntu
  - Kano Pi 3B Kit NeoPixel Ring Hat

## More devices coming soon!

# Contributing

Want to improve 1bOS?

Feel free to:
- Fork the repository
- Add your changes in a file named 1bOS-[YOURNAME-AND-EXTRA-INFO].py
- Submit a pull request

Ideas for future improvements:
- New apps
- More LED effects
- More supported hardware
- UI improvements
- Bug fixes
- Device support
