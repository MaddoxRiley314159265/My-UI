import pygame
from VectorUtil import *

display_dimensions = (-1, -1)
screen = -1

#List of the available menus
menus = []
#index of current menu being shown
current_menu = -1

#If true display current menu (if something on screen changes)
update_display = False

alignments = ["center", "nw", "sw", "ne", "se"]

#Basic button command to switch to next menu
def next_menu():
    global current_menu
    current_menu+=1

    if current_menu>=len(menus):
        current_menu = 0

#When switching between menus display this
class transition:
    def __init__(self, life : int) -> None:
        self.l = life
        self.c = life
    def update(self):
        self.c-=1
        #Update and display using life/counter lerp

class fade_transition(transition):
    def __init__(self, life: int, fade_out : bool = True, color : tuple = (0,0,0)) -> None:
        super().__init__(life)
        self.col = color
        self.fo = fade_out
    def update(self):
        #Get surface that supports transparent drawing
        s = pygame.Surface(screen.get_rect().size, pygame.SRCALPHA)

        life_tint = self.c/self.l*255
        if self.fo: life_tint = 255-life_tint

        pygame.draw.rect(s, self.col+(life_tint), screen.get_rect())
        global update_display
        update_display = True

class menu:
    def __init__(self, me : list = list(), in_t : transition = fade_transition(255), out_t : transition = fade_transition(255, False), *, bg_col : pygame.Color = pygame.Color("white"), bg_img : pygame.Surface = None) -> None:
        self.menu_elements = me
        self.in_transition = in_t
        self.out_transition = out_t

        self.swtiching_out = False
        self.ready_to_hide = False

        self.bg_col = bg_col
        self.bg_img = bg_img

        if self.bg_img==None:
            screen.fill(self.bg_col)
        else:
            screen.blit(pygame.transform.scale(bg_img, screen.get_rect()), (0,0))

    def update(self, mouse_pos : c, clicking : bool):
        if self.switching_out:
            if self.out_transition.c<0: self.ready_to_hide = True
            else: self.out_transition.update()
        else:
            if self.in_transition.c>=0: self.in_transition.update()
            for e in self.menu_elements:
                e.update(mouse_pos, clicking)

    def display(self):
        for e in self.menu_elements:
            e.display()

class menu_element:
    def __init__(self, pos : c, align : str) -> None:
        pass


def init(display_d : tuple, start_menus : list, start_menu : int):
    global display_dimensions, screen, menus, current_menu
    display_dimensions = display_d
    screen = pygame.display.set_mode(display_dimensions)

    menus = start_menus
    current_menu = start_menu

def main(mouse_pos : c, clicking : bool):
    menus[current_menu].update(mouse_pos, clicking)

    if update_display:
        menus[current_menu].display()
        pygame.display.flip()