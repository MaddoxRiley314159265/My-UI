import pygame
from textwrap import fill
from VectorUtil import *
from VectorUtil import c
pygame.init()
f1 = pygame.font.SysFont("Helvetica", 500)

display_dimensions = (-1, -1)
screen : pygame.Surface = -1
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

#----------------------------------------------------------Handy Functions-------------------------------------------------\
'''
def fit_text_to_rect(text : str, font_col, font : pygame.font.Font, fit_rect : pygame.Rect):
    newline_index = 1
    split_points = text.split(" ")
    i=0
    for word in split_points:
        my_r = font.render(word, True, font_col)
        w_to_h = my_r.get_rect().width/my_r.get_rect().height
        while fit_rect.height*w_to_h>fit_rect.width:
            #print(f"{}")
            #Word is too long

            split_p = i+len(word)-newline_index
            text = text[:split_p+1]+"\n"+text[split_p+1:]
            word = word[:len(word)-newline_index+1]+"\n"+word[-newline_index:]

            my_r = font.render(word, True, font_col)
            print(word)
            print(f"Width: {my_r.get_rect().width}, Height: {my_r.get_rect().height}")
            w_to_h = my_r.get_rect().width/my_r.get_rect().height
            newline_index+=1

        i+=len(word)+1

    def_rect = font.render(text, True, font_col).get_rect()
    w_to_h = def_rect.width/def_rect.height

    newline_index = 2
    while fit_rect.height*w_to_h>fit_rect.width:
        if newline_index==len(split_points):
            #All words have been shifted down
            break

        text = ""
        for i, word in enumerate(split_points):
            if i>len(split_points)-newline_index:
                ending = "\n"
            else: ending = " "

            text+=word+ending

        newline_index+=1
        def_rect = font.render(text, True, font_col).get_rect()
        w_to_h = def_rect.width/def_rect.height

    return pygame.transform.scale(font.render(text, True, font_col), (fit_rect.height*w_to_h, fit_rect.height))
'''
def fit_text_to_rect(text : str, font_col, font : pygame.font.Font, fit_rect : pygame.Rect, text_height : int = None):
    wrap = len(text)-1
    if text_height==None: t_h = fit_rect.height
    else: 
        t_h = text_height

    formatted_text = text
    while paragraph_dim(formatted_text, font_col, font, t_h)[0]>fit_rect.width:
        if wrap<=0:
            break
        formatted_text = fill(text, wrap)

        wrap-=1

    if wrap<0:
        print("ERROR: could not wrap text:", text)
        return
    return render_paragraph(formatted_text, font_col, font, fit_rect, t_h)
def paragraph_dim(text : str, font_col, font : pygame.font.Font, height):
    width = 0
    for line in text.split("\n"):
        w, h = font.render(line, True, font_col).get_rect().size

        w_to_h = w/h
        h = height/(1+text.count("\n"))

        if h*w_to_h>width: width = h*w_to_h
    return width, height*(1+text.count("\n"))
def render_paragraph(text : str, font_col, font : pygame.font.Font, target_rect : pygame.Rect, height : int = None):
    for i, line in enumerate(text.split("\n")):
        if height==None: height = target_rect.height
        w, h = paragraph_dim(text, font_col, font, height)
        screen.blit(pygame.transform.scale(font.render(line, True, font_col), (w,h)), (target_rect.left, target_rect.top+i*h))

#-------------------------------------------------------Menu and Transitions---------------------------------------------------------------

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

    def update(self, mouse_pos : c, clicking : bool, key_event = None):
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
                e.update(mouse_pos, clicking, key_event)

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
    def update(self, mouse_pos : c, clicking : bool, key_event = None):
        pass #Update appearence
    def display(self):
        pass #Display
class button(menu_element):
    def __init__(self, pos: c, align: str, dimensions : c, action, *, col = (200,200,200), img : pygame.Surface = None, highlight_col = (240,240,240), highlight_img : pygame.Surface = None, border_width = 20, border_color = (0,0,0), border_img : pygame.Surface = None, text = "Buttonkjsdfhksjdfh", font : pygame.font.Font = f1, text_col = (0,0,0), inflate_on_hightlight = 2, inflate_on_click = 4, multiple_calls = False) -> None:
        super().__init__(pos, align)
        self.d = dimensions
        p = self.aligned_pos(self.d)
        self.o_r = pygame.Rect(p.x, display_dimensions[1]-p.y, self.d.x, self.d.y)
        self.r = self.o_r

        self.o_i = img
        self.i = self.o_i
        self.h_i = highlight_img

        self.o_col = col
        self.col = self.o_col
        self.h_col = highlight_col

        self.b_w = border_width
        self.b_col = border_color
        self.b_i = border_img


        self.t = text
        self.t_col = text_col
        self.f = font
        self.func = action


        self.i_h = inflate_on_hightlight
        self.i_c = inflate_on_click

        self.m_c = multiple_calls
        self.acitvate_on_click = True
    def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display
        
        #If mouse hovering
        if self.r.collidepoint(mouse_pos[0], mouse_pos[1]):
            if not self.r==self.o_r.inflate(self.i_h, self.i_h):
                self.r = self.o_r.inflate(self.i_h, self.i_h)

                if self.h_i==None: self.col = self.h_col
                else: self.i = self.h_i
                update_display = True
            #If button clicked
            if clicking and self.acitvate_on_click:
                if not self.r==self.o_r.inflate(self.i_c, self.i_c):
                    self.r = self.o_r.inflate(self.i_c, self.i_c)
                    update_display = True
                self.func()
                #Only activate once
                if not self.m_c:
                    self.acitvate_on_click = False
            elif not clicking and not self.acitvate_on_click:
                #Reset to activate once clicked again
                self.acitvate_on_click = True

        elif not self.r==self.o_r:
            self.col = self.o_col
            self.i = self.o_i
            self.r = self.o_r
            update_display = True
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.b_w>0:
            if self.b_i==None:
                pygame.draw.rect(screen, self.b_col, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100))
            else:
                screen.blit(pygame.transform.scale(self.b_i, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100).size), (self.r.left-(1+self.b_w/self.d.x*100)/2, self.r.top-(1+self.b_w/self.d.y*100)/2))
        #Draw button
        if not self.i==None:
            #If has image, draw image instead
            screen.blit(pygame.transform.scale(self.i, self.r.size), self.r.topleft)
        else: pygame.draw.rect(screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            fit_text_to_rect(self.t, self.t_col, self.f, self.r), self.r.topleft
        #print("Draw button")
class label(menu_element):
    def __init__(self, pos: c, align: str, dimensions : c, *, col = (200,200,200), img : pygame.Surface = None, border_width = 20, border_color = (0,0,0), border_img : pygame.Surface = None, text = "Awesome Label", font : pygame.font.Font = f1, text_col = (0,0,0)) -> None:
        super().__init__(pos, align)
        self.d = dimensions
        p = self.aligned_pos(self.d)
        self.r = pygame.Rect(p.x, display_dimensions[1]-p.y, self.d.x, self.d.y)

        self.i = img

        self.col = col

        self.b_w = border_width
        self.b_col = border_color
        self.b_i = border_img


        self.t = text
        self.t_col = text_col
        self.f = font

    '''def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display'''
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.b_w>0:
            if self.b_i==None:
                pygame.draw.rect(screen, self.b_col, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100))
            else:
                screen.blit(pygame.transform.scale(self.b_i, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100).size), (self.r.left-(1+self.b_w/self.d.x*100)/2, self.r.top-(1+self.b_w/self.d.y*100)/2))
        #Draw button
        if not self.i==None:
            #If has image, draw image instead
            screen.blit(pygame.transform.scale(self.i, self.r.size), self.r.topleft)
        else: pygame.draw.rect(screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            fit_text_to_rect(self.t, self.t_col, self.f, self.r), self.r.topleft
        #print("Draw label")
class text(menu_element):
    def __init__(self, pos: c, align: str, height : int, text = "Awesome Label", text_col = (0,0,0), font : pygame.font.Font = f1, highlight_col = (240,240,240)) -> None:
        super().__init__(pos, align)
        w, h = paragraph_dim(text, text_col, font, height)
        self.p = self.aligned_pos(c(w/h*height, height))
        self.r = pygame.Rect(self.p.x, self.p.y, w/h*height, height)

        self.t = text
        self.o_col = text_col
        self.h_col = highlight_col
        self.col = self.o_col
        self.f = font

    def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display
        if self.r.collidepoint(mouse_pos):
            #Text being highlighted
            self.col = self.h_col
        else:
            #Text not being highlighted
            self.col = self.o_col
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw Text
        if not self.t=="":
            screen.blit(self.f.render(self.t, True, self.col), self.r.topleft)
        #print("Draw text")
class entry(menu_element):
    def __init__(self, pos: c, align: str, dimensions : c, text_height : int = None, *, col = (200,200,200), img : pygame.Surface = None, border_width = 20, border_color = (0,0,0), border_img : pygame.Surface = None, highlight_col = (240,240,240), highlight_img : pygame.Surface = None, text = "", font : pygame.font.Font = f1, text_col = (0,0,0), clamp_text : bool = True) -> None:
        super().__init__(pos, align)
        self.d = dimensions
        p = self.aligned_pos(self.d)
        self.r = pygame.Rect(p.x, display_dimensions[1]-p.y, self.d.x, self.d.y)
        self.t_r = None
        self.t_h = text_height

        self.o_i = img
        self.i = self.o_i
        self.h_i = highlight_img

        self.o_col = col
        self.col = self.o_col
        self.h_c = highlight_col

        self.b_w = border_width
        self.b_col = border_color
        self.b_i = border_img


        self.t = text
        self.t_col = text_col
        self.f = font

        self.selected = False

        self.acitvate_on_click = True
        self.type_cooldown = 0

        self.ct = clamp_text

    def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display
        if self.selected and self.type_cooldown<=0 and not key_event==None:
            if key_event.key==pygame.K_BACKSPACE:
                self.t = self.t[:-1]    
                update_display = True
            elif key_event.key==pygame.K_DELETE:
                self.t = ""
            elif key_event.key==pygame.K_RETURN:
                self.selected = False
            else:
                self.t+=key_event.unicode
                if self.ct and paragraph_dim(self.t, self.t_col, self.f, self.r.height)[0]>self.r.width:
                    self.t = self.t[:-1]
                else: update_display = True
            self.type_cooldown = 5

            if self.t_h==None: h = self.r.height
            else: h = self.t_h
            w, h = paragraph_dim(self.t, self.t_col, self.f, h)
            self.t_r = pygame.Rect(self.r.left, self.r.top, w, h)

        if clicking:
            if self.acitvate_on_click:
                if self.r.collidepoint(mouse_pos) and not self.selected:
                    self.selected = True
                else: self.selected = False
                self.acitvate_on_click = False
        elif not self.acitvate_on_click: 
            self.acitvate_on_click = True

        if self.selected and not (self.col==self.h_c and self.i==self.h_i):
            self.col = self.h_c
            self.i = self.h_i
            update_display = True
        elif not self.selected and not (self.col==self.o_col and self.i==self.o_i):
            self.col = self.o_col
            self.i = self.o_i
            update_display = True

        self.type_cooldown-=1
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.b_w>0:
            if self.b_i==None:
                pygame.draw.rect(screen, self.b_col, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100))
            else:
                screen.blit(pygame.transform.scale(self.b_i, self.r.inflate(1+self.b_w/self.d.x*100, 1+self.b_w/self.d.y*100).size), (self.r.left-(1+self.b_w/self.d.x*100)/2, self.r.top-(1+self.b_w/self.d.y*100)/2))
        #Draw button
        if not self.i==None:
            #If has image, draw image instead
            screen.blit(pygame.transform.scale(self.i, self.r.size), self.r.topleft)
        else: pygame.draw.rect(screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            if self.ct:
                screen.blit(pygame.transform.scale(self.f.render(self.t, True, self.t_col), self.t_r.size), self.r.topleft)
            else: fit_text_to_rect(self.t, self.t_col, self.f, self.r, self.t_h), self.r.topleft
        #print("Draw entry")


#--------------------------------------------------------------------------------------Put it together-----------------------------------------------------------------------

def init(display_d : tuple):
    global display_dimensions, screen
    display_dimensions = display_d
    screen = pygame.display.set_mode(display_dimensions)

def init_menus(start_menus : list, start_menu : int = 0):
    global menus, current_menu
    menus = start_menus
    current_menu = start_menu

def main(mouse_pos : c, clicking : bool, key_event = None):
    global redraw_stuff
    menus[current_menu].update(mouse_pos, clicking, key_event)

    if update_display:
        #print("Update")
        if redraw_stuff: 
            #print("Draw menu")
            menus[current_menu].display()
        pygame.display.update(menus[current_menu].r)
        redraw_stuff = True

def mainloop():
    global update_display
    '''f1 = False
    f2 = False'''

    bg_img = pygame.image.load("bgCropped.gif")
    init((1200, 800))
    init_menus([menu([button(c(500, 700), "center", c(200, 400), say_hello, border_img=bg_img), label(c(0, 600), "nw", c(400, 100)), text(c(100,800), "se", 50, "Hello World"), entry(c(500, 800), "nw", c(300, 300), 50, clamp_text=False)], bg_img=bg_img)])

    exit = False
    clicking = False
    key_pressed = None
    while not exit:

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                exit = True
            elif event.type==pygame.KEYDOWN:
                key_pressed = event
                '''if event.key==pygame.K_a:
                    f1 = True
                if event.key==pygame.K_d:
                    f2 = True'''
            elif event.type==pygame.KEYUP:
                key_pressed = None
                '''if event.key==pygame.K_a:
                    f1 = False
                if event.key==pygame.K_d:
                    f2 = False'''
            elif event.type==pygame.MOUSEBUTTONDOWN:
                clicking = True
            elif event.type==pygame.MOUSEBUTTONUP:
                clicking = False

        '''if f1:
            menus[current_menu].menu_elements[0].r.width-=1
            update_display = True
        if f2:
            menus[current_menu].menu_elements[0].r.width+=1
            update_display = True'''

        main(pygame.mouse.get_pos(), clicking, key_pressed)

        clock.tick(60)

mainloop()