import pygame
from VectorUtil import *
from VectorUtil import c
pygame.init()
f1 = pygame.font.SysFont("Helvetica", 500)

display_dimensions = (-1, -1)
screen = -1
clock = pygame.time.Clock()

#List of the available menus
menus = []
#index of current menu being shown
current_menu = -1

#If true display current menu (if something on screen changes)
update_display = True
redraw_stuff = True

alignments = ["center", "nw", "sw", "ne", "se"]

#Basic button command to switch to next menu
def next_menu():
    global current_menu
    current_menu+=1

    if current_menu>=len(menus):
        current_menu = 0
#Basic button command
def say_hello():
    print("Hello!")



#-------------------------------------------------------Menu Stuff---------------------------------------------------------------

#When switching between menus display this
class transition:
    def __init__(self, life : int) -> None:
        self.l = life
        self.c = life
    def update(self):
        self.c-=1
        #Update and display using life/counter lerp

class fade_transition(transition):
    def __init__(self, life: int, fade_out : bool = True, color : tuple = (0,0,0), fade_modifier = 0) -> None:
        super().__init__(life)
        self.col = color
        self.fo = fade_out
        self.fm = fade_modifier
    def update(self, menu_rect : pygame.Rect):
        global screen
        #Get surface that supports transparent drawing
        s = pygame.Surface(menu_rect.size, pygame.SRCALPHA)

        t = self.c/self.l
        #Fast
        if self.fm==0: d=t
        elif self.fm==1: d = t*t*t
        #Slow then fast
        elif self.fm==2: d = 1-(1-t)**3
        #elif self.fm==3: d = 4*t*t*t*(1-t)+t*(1-4*(1-t)**3)

        life_tint = int(d*255)
        if not self.fo: life_tint = 255-life_tint
        c = (self.col[0], self.col[1], self.col[2], life_tint)

        s.fill(c)
        screen.blit(s, menu_rect)
        global update_display, redraw_stuff
        update_display = True
        redraw_stuff = False
        #print("Draw transition")

        self.c-=1

class menu:
    def __init__(self, me : list = list(), rect : pygame.Rect = None, in_t : transition = fade_transition(100, fade_modifier=2), out_t : transition = fade_transition(100, False), *, bg_col : pygame.Color = pygame.Color("white"), bg_img : pygame.Surface = None) -> None:
        global screen
        if rect==None: rect = screen.get_rect()
        self.r = rect
        self.s = pygame.Surface(self.r.size)

        self.menu_elements = me
        self.in_transition = in_t
        self.out_transition = out_t

        self.switching_out = False
        self.ready_to_hide = False

        self.bg_col = bg_col
        self.bg_img = bg_img

        self.draw_menu()

    def update(self, mouse_pos : c, clicking : bool, key_down = None):
        global update_display

        if self.switching_out:
            if self.out_transition.c<0: self.ready_to_hide = True
            else: 
                self.display()
                self.out_transition.update(self.r)
        else:
            if self.in_transition.c>=0: 
                self.display()
                self.in_transition.update(self.r)
            for e in self.menu_elements:
                e.update(mouse_pos, clicking, key_down)

    def draw_menu(self):
        if self.bg_img==None:
            self.s.fill(self.bg_col)
        else:
            #screen.fill((255,255,255))
            self.s.blit(pygame.transform.scale(self.bg_img, self.r.size), (0,0))

        screen.blit(self.s, self.r.topleft)
        #print("Draw bg")

    def display(self):
        global update_display
        #Erase elements by drawing menu again, then display each element
        self.draw_menu()
        for e in self.menu_elements:
            e.display()
        update_display = False



#------------------------------------------------------------------Menu Elements------------------------------------------------------------------
class menu_element:
    def __init__(self, pos : c, align : str) -> None:
        self.p = pos
        self.a = align
    def aligned_pos(self, dimensions : c):
        if self.a=="nw":
            return self.p
        elif self.a=="ne":
            return self.p-c(dimensions.x, 0)
        elif self.a=="se":
            return self.p-dimensions
        elif self.a=="sw":
            return self.p-c(0, dimensions.y)
        elif self.a=="center":
            return self.p+c(dimensions.x/2, -dimensions.y/2)
        else:
            print(f"ERROR: Invalid alignment '{self.a}'")
            return None
    def update(self, mouse_pos : c, clicking : bool, key_down = None):
        pass #Update appearence
    def display(self):
        pass #Display
class button(menu_element):
    def __init__(self, pos: c, align: str, dimensions : c, action, *, col = (200,200,200), highlight_col = (240,240,240), border_width = 20, border_color = (0,0,0), text = "Button", font : pygame.font.Font = f1, text_col = (0,0,0), inflate_on_hightlight = 2, inflate_on_click = 4, multiple_calls = False) -> None:
        super().__init__(pos, align)
        self.d = dimensions
        p = self.aligned_pos(self.d)
        self.o_r = pygame.Rect(p.x, display_dimensions[1]-p.y, self.d.x, self.d.y)
        self.r = self.o_r

        self.o_col = col
        self.col = self.o_col
        self.h_col = highlight_col
        self.b_w = border_width
        self.b_col = border_color

        self.t = text
        self.t_col = text_col
        self.f = font
        self.func = action

        self.i_h = inflate_on_hightlight
        self.i_c = inflate_on_click
    def update(self, mouse_pos: c, clicking: bool, key_down=None):
        global update_display
        #If mouse hovering
        if self.r.collidepoint(mouse_pos[0], mouse_pos[1]):
            if not self.r==self.o_r.inflate(self.i_h, self.i_h):
                self.r = self.o_r.inflate(self.i_h, self.i_h)
                self.col = self.h_col
                update_display = True
            #If button clicked
            if clicking and not self.r==self.o_r.inflate(self.i_c, self.i_c):
                self.r = self.o_r.inflate(self.i_c, self.i_c)
                self.func()
                update_display = True

        elif not self.r==self.o_r:
            self.col = self.o_col
            self.r = self.o_r
            update_display = True
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        pygame.draw.rect(screen, self.b_col, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100))
        #Draw button
        pygame.draw.rect(screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            screen.blit(pygame.transform.scale(self.f.render(self.t, True, self.t_col), self.r.size), self.r)
        #print("Draw button")


#--------------------------------------------------------------------------------------Put it together-----------------------------------------------------------------------

def init(display_d : tuple):
    global display_dimensions, screen
    display_dimensions = display_d
    screen = pygame.display.set_mode(display_dimensions)

def init_menus(start_menus : list, start_menu : int = 0):
    global menus, current_menu
    menus = start_menus
    current_menu = start_menu

def main(mouse_pos : c, clicking : bool, key_down = None):
    global redraw_stuff
    menus[current_menu].update(mouse_pos, clicking, key_down)

    if update_display:
        #print("Update")
        if redraw_stuff: 
            #print("Draw menu")
            menus[current_menu].display()
        pygame.display.update(menus[current_menu].r)
        redraw_stuff = True

def mainloop():
    bg_img = pygame.image.load("bgCropped.gif")
    init((1200, 800))
    init_menus([menu([button(c(500, 500), "center", c(200, 140), say_hello)], bg_img=bg_img)])

    exit = False
    clicking = False
    key_pressed = None
    while not exit:

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                exit = True
            elif event.type==pygame.KEYDOWN:
                key_pressed = event
            elif event.type==pygame.KEYUP:
                key_pressed = None
            elif event.type==pygame.MOUSEBUTTONDOWN:
                clicking = True
            elif event.type==pygame.MOUSEBUTTONUP:
                clicking = False

        main(pygame.mouse.get_pos(), clicking, key_pressed)

        clock.tick(60)

mainloop()