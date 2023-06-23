import pygame

display_dimensions = (-1, -1)
screen : pygame.Surface = -1
clock = pygame.time.Clock()

#List of the available menus
menus = []
#index of current menu being shown
current_menu_index = -1
next_menu_index = -1

#If true display current menu (if something on screen changes)
update_display = True
redraw_stuff = True

exit_loop = False
clicking = False
key_pressed = None