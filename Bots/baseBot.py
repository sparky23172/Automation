import pyautogui
import logging
import keyboard
import time
import argparse

logging.basicConfig(level=logging.INFO)

# Set up logging
def get_arg():
    """ Takes nothing
Purpose: Gets arguments from command line
Returns: Argument's values
"""
    parser = argparse.ArgumentParser()
    # Information
    parser.add_argument("-d","--debug",dest="debug",action="store_true",help="Turn on debugging",default=False)
    # Functionality
    parser.add_argument("-f","--find",dest="find",action="store_true",help="Turn on finder mode to see coordinates for mouse and colors",default=False)

    options = parser.parse_args()
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
        global DEBUG
        DEBUG = True
    else:
        logging.basicConfig(level=logging.INFO)
    return options


def finder():
    """ Takes nothing
Purpose: Finds the mouse position and color
Returns: Nothing
"""
    while keyboard.is_pressed('q') != True:
        if keyboard.is_pressed('c') == True:
            x, y = pyautogui.position()
            r,g,b = pyautogui.pixel(x, y)

            logging.info("Mouse position: {}, {}. R: {}. G: {}. B: {}.".format(x, y, r, g, b))
            logging.info("\twin32api.SetCursorPos(({}, {}))".format(x, y))
            logging.info("\tpyautogui.pixel({}, {})[0] == {} and pyautogui.pixel({}, {})[1] == {} and pyautogui.pixel({}, {})[2] == {}\n".format(x, y, r, x, y, g, x, y, b))
            time.sleep(1)


def main():
    options = get_arg()
    logging.info("Starting program")
    if options.find:
        finder()


if __name__ == "__main__":
    main()
    
