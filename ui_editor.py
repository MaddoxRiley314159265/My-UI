from my_ui import *
import ui_config
import pygame

save_file = "ui.json"

pygame.init()

init_menus((1000, 800))

ui_config.menus.extend([Menu([Button(c(500, 700), "center", c(200, 400), next_menu, border_img_name=bg_img_name), Label(c(0, 600), "nw", c(400, 100)), Text(c(500,800), "se", 50, "Hello World"), Entry(c(500, 800), "nw", c(300, 300), 50, clamp_text=False)], bg_img_name=bg_img_name), 
            Menu([Label(c(200, 200), "nw", c(200, 100), text="Welcome to menu 2"), Button(c(500, 500), "center", c(300, 100), prev_menu, text="If we could turn back time")], bg_col=(200, 200, 100))])
    

while not ui_config.exit_loop:
    main()