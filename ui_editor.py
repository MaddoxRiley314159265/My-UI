from my_ui import *
import ui_config
import pygame
from json import loads, dumps

save_file = "ui.json"

pygame.init()

init_menus((1000, 800))

ui_config.menus.append(Menu())

def save():
    f = open(save_file, "a")

    f.write("\n")

    #Save screen size
    f.write(dumps(ui_config.display_dimensions))
    #Save current menu
    f.write(dumps(ui_config.current_menu_index))
    #Save menus
    

while not ui_config.exit_loop:
    main()