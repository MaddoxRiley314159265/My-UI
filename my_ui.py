import pygame
from textwrap import fill
from VectorUtil import *
from VectorUtil import c
import ui_config
from json import loads, dumps

pygame.init()
f1 = pygame.font.SysFont("Helvetica", 500)

alignments = ["center", "nw", "sw", "ne", "se"]

bg_img_name = "bgCropped.gif"
bg_img = pygame.image.load(bg_img_name)

#----------------------------------------------------Basic button commands-------------------------------------------
#Basic button command to switch to next menu
def next_menu():
    ui_config.next_menu_index = ui_config.current_menu_index+1

    if ui_config.next_menu_index>=len(ui_config.menus):
        ui_config.next_menu_index = 0

    ui_config.menus[ui_config.current_menu_index].switching_out = True
def prev_menu():
    ui_config.next_menu_index = ui_config.current_menu_index-1

    if ui_config.next_menu_index<0:
        ui_config.next_menu_index = len(ui_config.menus)-1
    ui_config.menus[ui_config.current_menu_index].switching_out = True

def say_hello():
    print("Hello!")

def exit():
    pygame.quit()
    quit()

#----------------------------------------------------------Handy Functions-------------------------------------------------\
def save(save_file : str):
    f = open(save_file, "a")

    f.write("\n")

    #Save file format version
    f.write(dumps(0))

    #Save screen size
    f.write(dumps(ui_config.display_dimensions))
    #Save current menu
    f.write(dumps(ui_config.current_menu_index))
    #Save menus
    f.write([obj_to_args(m) for m in ui_config.menus])

    f.close()

def load(save_file : str, index : int):
    f = open(save_file, "r")

    all_saves = f.read().split("\n\n")


def obj_to_args(obj):
    if isinstance(obj, Menu):
        return ([obj_to_args(o) for o in obj.__menu_elements], (obj.r.left, obj.r.top, obj.r.width, obj.r.height), obj_to_args(obj.in_transition), obj_to_args(obj.out_transition), obj.get_bg_col(), obj.get_bg_img_name())
    elif isinstance(obj, Fade_Transition):
        return (obj.l, obj.get_fade_setting(), obj.get_col(), obj.get_fade_modifier())
    elif isinstance(obj, Button):
        return (obj.get_pos(), obj.get_alignment(), obj.get_dimensions(), obj.get_action(), obj.get_col(), obj.get_img_name(), obj.get_highlight_col(), obj.get_highlight_img_name(), obj.get_border_width(), obj.get_border_col(), obj.get_border_img_name(), obj.get_text(), obj.get_font(), obj.get_text_col(), obj.get_highlight_inflation(), obj.get_click_inflation(), obj.get_multiple_calls())
    elif isinstance(obj, Label):
        return (obj.get_pos(), obj.get_alignment(), obj.get_dimensions(), obj.get_col(), obj.get_img_name(), obj.get_border_width(), obj.get_border_col(), obj.get_border_img_name(), obj.get_text(), obj.get_font(), obj.get_text_col())
    elif isinstance(obj, Text):
        return (obj.get_pos(), obj.get_alignment(), obj.get_dimensions(), obj.get_height(), obj.get_text(), obj.get_text_col(), obj.get_font(), obj.get_highlight_col())
    elif isinstance(obj, Entry):
        return (obj.get_pos(), obj.get_alignment(), obj.get_dimensions(), obj.get_height(), obj.get_col(), obj.get_img_name(), obj.get_border_width(), obj.get_border_col(), obj.get_border_img_name(), obj.get_highlight_col(), obj.get_highlight_img_name(), obj.get_text(), obj.get_font(), obj.get_text_col(), obj.get_if_clamp())
    
def font_name_to_font(font_name : str):
    try:
        f = pygame.font.Font(font_name, 500)
    except:
        try:
            f = pygame.font.SysFont(font_name, 500)
        except:
            print(f"ERROR: could not find font '{font_name}'")
            f = None
    return f
    

def fit_text_to_rect(text : str, font_col, font_name : str, fit_rect : pygame.Rect, text_height : int = None, flex_text : bool = True, display : bool = True):
    if text=="": return ""
    if flex_text: max_width_over = 200
    else: max_width_over = 0

    wrap = len(text)-1
    if text_height==None: t_h = fit_rect.height
    else: 
        t_h = text_height

    formatted_text = text
    while paragraph_dim(formatted_text, font_col, font_name, t_h, flex_text)[0]-fit_rect.width>max_width_over:
        if wrap<=0:
            break
        formatted_text = fill(text, wrap)

        wrap-=1

    if wrap<0:
        print("ERROR: could not wrap text:", text)
        return
    if display: return render_paragraph(formatted_text, font_col, font_name, fit_rect, t_h, flex_text)
    else: return formatted_text
def line_width(text : str, font_col, font : str, height):
    w, h = font.render(text, True, font_col).get_rect().size
    w_to_h = w/h

    return height*w_to_h
def paragraph_dim(text : str, font_col, font_name : str, height, flex_text : bool = True):
    font = font_name_to_font(font_name)
    width = 0
    if flex_text: height = height/(1+text.count("\n"))
    for line in text.split("\n"):
        w = line_width(line, font_col, font, height)

        if w>width: width = w
    return width, height*(1+text.count("\n"))
def render_paragraph(text : str, font_col, font_name : str, target_rect : pygame.Rect, height : int = None, flex_text : bool = True):
    font = font_name_to_font(font_name)
    if flex_text: height = height/(1+text.count("\n"))
    for i, line in enumerate(text.split("\n")):
        if height==None: height = target_rect.height
        w = line_width(line, font_col, font, height)
        if w>target_rect.width and flex_text: w = target_rect.width
        ui_config.screen.blit(pygame.transform.scale(font.render(line, True, font_col), (w,height)), (target_rect.left, target_rect.top+i*height))

#-------------------------------------------------------Menu and Transitions---------------------------------------------------------------

#When switching between menus display this
class Transition:
    def __init__(self, life : int) -> None:
        self.l = life
        self.c = life
    def update(self):
        self.c-=1
        #Update and display using life/counter lerp

class Fade_Transition(Transition):
    def __init__(self, life: int, fade_out : bool = True, color : tuple = (0,0,0), fade_modifier = 0) -> None:
        super().__init__(life)
        self.__col = color
        self.__fo = fade_out
        self.__fm = fade_modifier
    def update(self, menu_rect : pygame.Rect):
        global screen
        #Get surface that supports transparent drawing
        s = pygame.Surface(menu_rect.size, pygame.SRCALPHA)

        t = self.c/self.l
        #Fast
        if self.__fm==0: d=t
        elif self.__fm==1: d = t*t*t
        #Slow then fast
        elif self.__fm==2: d = 1-(1-t)**3
        #elif self.fm==3: d = 4*t*t*t*(1-t)+t*(1-4*(1-t)**3)

        life_tint = int(d*255)
        if not self.__fo: life_tint = 255-life_tint
        c = (self.__col[0], self.__col[1], self.__col[2], life_tint)

        s.fill(c)
        ui_config.screen.blit(s, menu_rect)
        ui_config.update_display = True
        ui_config.redraw_stuff = False
        #print("Draw transition")

        self.c-=1
        print(self.c)

    def get_fade_setting(self):
        return self.__fo
    def get_fade_modifier(self):
        return self.__fm
    def get_col(self):
        return (self.__col[0], self.__col[1], self.__col[2])

class Menu:
    def __init__(self, me : list = list(), rect : pygame.Rect = None, in_t : Transition = Fade_Transition(100, fade_modifier=2), out_t : Transition = Fade_Transition(100, False, fade_modifier=2), *, bg_col : pygame.Color = pygame.Color("white"), bg_img : pygame.Surface = None, bg_img_name : str = None) -> None:
        if rect==None: rect = ui_config.screen.get_rect()
        self.r = rect
        self.__s = pygame.Surface(self.r.size)

        self.__menu_elements = me
        self.in_transition = in_t
        self.out_transition = out_t

        self.switching_out = False
        self.ready_to_hide = False

        self.__bg_col = bg_col
        self.__bg_img = bg_img
        self.__bg_img_n = bg_img_name
        if self.__bg_img==None and not self.__bg_img_n==None:
            self.__bg_img = pygame.image.load(self.__bg_img_n)
        elif self.__bg_img_n==None and not self.__bg_img==None:
            raise Exception("Error, must provide image file name when providing image")

        #self.draw_menu()

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
            for e in self.__menu_elements:
                e.update(mouse_pos, clicking, key_event)

    def draw_menu(self):
        if self.__bg_img==None:
            self.__s.fill(self.__bg_col)
        else:
            #screen.fill((255,255,255))
            self.__s.blit(pygame.transform.scale(self.__bg_img, self.r.size), (0,0))

        ui_config.screen.blit(self.__s, self.r.topleft)
        #print("Draw bg")

    def display(self):
        global update_display
        #Erase elements by drawing menu again, then display each element
        self.draw_menu()
        for e in self.__menu_elements:
            e.display()
        update_display = False

    def get_bg_col(self):
        return (self.__bg_col[0], self.__bg_col[1], self.__bg_col[2])
    def get_bg_img_name(self):
        return self.__bg_img_n



#------------------------------------------------------------------Menu Elements------------------------------------------------------------------
class Menu_Element:
    def __init__(self, pos : c, align : str) -> None:
        self.__p = pos
        self.__a = align
    def aligned_pos(self, dimensions : c):
        if self.__a=="nw":
            return self.__p
        elif self.__a=="ne":
            return self.__p-c(dimensions.x, 0)
        elif self.__a=="se":
            return self.__p-dimensions
        elif self.__a=="sw":
            return self.__p-c(0, dimensions.y)
        elif self.__a=="center":
            return self.__p+c(dimensions.x/2, -dimensions.y/2)
        else:
            print(f"ERROR: Invalid alignment '{self.__a}'")
            return None
    def update(self, mouse_pos : c, clicking : bool, key_event = None):
        pass #Update appearence
    def display(self):
        pass #Display
    def get_pos(self):
        return self.__p
    def get_alignment(self):
        return self.__a
class Text_Element(Menu_Element):
    def __init__(self, pos: c, align: str, dimensions : c, text : str = "Press Me", font_name : str = "Helvetica", text_col = (0,0,0)) -> None:
        super().__init__(pos, align)
        self.__d = dimensions
        p = self.aligned_pos(self._Text_Element__d)
        self.__r = pygame.Rect(p.x, ui_config.display_dimensions[1]-p.y, self._Text_Element__d.x, self._Text_Element__d.y)

        self.__t = text
        self.__t_col = text_col
        self.__f_n = font_name
        self.__f = None
        if not text=="":
            self.__f = font_name_to_font(self.__f_n)
    def get_dimensions(self):
        return self._Text_Element__d
    def get_text(self):
        return self.__t
    def get_font(self):
        return self.__f_n
    def get_text_col(self):
        return (self.__t_col[0], self.__t_col[1], self.__t_col[2])
class Text_Box_Element(Text_Element):
    def __init__(self, pos: c, align: str, dimensions: c, 
                 
                 text: str = "Press Me", font_name: str = "Helvetica", text_col=(0, 0, 0),
                 
                 col = (200,200,200), img_name : str = None,
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None) -> None:
        super().__init__(pos, align, dimensions, text, font_name, text_col)
        self.__col = col

        self.__i_n = img_name
        self.__i = None
        if not self.__i_n==None:
            try:
                self.__i = pygame.image.load(self.__i_n)
            except:
                print(f"ERROR: could not load image '{img_name}")

        self.__b_w = border_width
        self.__b_col = border_color
        self.__b_i_n = border_img_name
        self.__b_i = None
        if not self.__b_i_n==None:
            try:
                self.__b_i = pygame.image.load(self.__b_i_n)
            except:
                print(f"ERROR: could not load image '{border_img_name}")
    def get_col(self):
        return (self.__col[0], self.__col[1], self.__col[2])
    def get_border_col(self):
        return (self.__b_col[0], self.__b_col[1], self.__b_col[2])
    def get_img_name(self):
        return self.__i_n
    def get_border_img_name(self):
        return self.__b_i_n
    def get_border_width(self):
        return self.__b_w
class Button(Text_Box_Element):
    def __init__(self, pos: c, align: str, dimensions : c, action, *, col = (200,200,200), 
                 
                 img_name : str = None, highlight_col = (240,240,240), highlight_img_name : str = None, 
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, 
                 
                 text : str = "Press Me", font_name : str = "Helvetica", text_col = (0,0,0), 
                 
                 inflate_on_hightlight = 2, inflate_on_click = 4, multiple_calls = False) -> None:
        super().__init__(pos, align, dimensions, text, font_name, text_col, col, img_name, border_width, border_color, border_img_name)
        self.__p = self._Menu_Element__p
        self.__a = self._Menu_Element__a
        self.__r = self._Text_Element__r

        self.__d = self._Text_Element__d
        self.__t = self._Text_Element__t
        self.__f_n = self._Text_Element__f_n
        self.__t_col = self._Text_Element__t_col
        self.__col = self._Text_Box_Element__col
        self.__i = self._Text_Box_Element__i
        self.__b_w = self._Text_Box_Element__b_w
        self.b_col = self._Text_Box_Element__b_col
        self.__b_i = self._Text_Box_Element__b_i


        self.__o_r = self.__r
        self.__o_i = self.__i
        

        self.__h_i_n = highlight_img_name
        self.__h_i = None
        if not self.__h_i_n==None:
            try:
                self.__h_i = pygame.image.load(self.__h_i_n)
            except:
                print(f"ERROR: could not load image '{highlight_img_name}")

        self.__o_col = self.__col
        self.__h_col = highlight_col

        self.__func = action


        self.__i_h = inflate_on_hightlight
        self.__i_c = inflate_on_click

        self.__m_c = multiple_calls
        self.acitvate_on_click = True
    def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display
        
        #If mouse hovering
        if self.__r.collidepoint(mouse_pos[0], mouse_pos[1]):
            if not self.__r==self.__o_r.inflate(self.__i_h, self.__i_h):
                self.__r = self.__o_r.inflate(self.__i_h, self.__i_h)

                if self.__h_i==None: self.__col = self.__h_col
                else: self.__i = self.__h_i
                update_display = True
            #If button clicked
            if clicking and self.acitvate_on_click:
                if not self.__r==self.__o_r.inflate(self.__i_c, self.__i_c):
                    self.__r = self.__o_r.inflate(self.__i_c, self.__i_c)
                    update_display = True
                self.__func()
                #Only activate once
                if not self.__m_c:
                    self.acitvate_on_click = False
            elif not clicking and not self.acitvate_on_click:
                #Reset to activate once clicked again
                self.acitvate_on_click = True

        elif not self.__r==self.__o_r:
            self.__col = self.__o_col
            self.__i = self.__o_i
            self.__r = self.__o_r
            update_display = True
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.t__b_w>0:
            if self.__b_i==None:
                pygame.draw.rect(ui_config.screen, self.__b_col, self.__r.inflate(1+self.__b_w/self.__d.x*100, 1+self.__b_w/self.__d.y*100))
            else:
                ui_config.screen.blit(pygame.transform.scale(self.__b_i, self.__r.inflate(1+self.__b_w/self.__d.x*100, 1+self.__b_w/self.__d.y*100).size), (self.__r.left-(1+self.__b_w/self.__d.x*100)/2, self.__r.top-(1+self.__b_w/self.__d.y*100)/2))
        #Draw button
        if not self.__i==None:
            #If has image, draw image instead
            ui_config.screen.blit(pygame.transform.scale(self.__i, self.__r.size), self.__r.topleft)
        else: pygame.draw.rect(ui_config.screen, self.__col, self.__r)
        #Draw text
        if not self.__t=="":
            fit_text_to_rect(self.__t, self.__t_col, self.__f_n, self.__r), self.__r.topleft
        #print("Draw button")
    def get_action(self):
        return self.__func
    def get_highlight_col(self):
        return (self.__h_col[0], self.__h_col[1], self.__h_col[2])
    def get_highlight_img_name(self):
        return self.__h_i_n
    def get_highlight_inflation(self):
        return self.__i_h
    def get_click_inflation(self):
        return self.__i_c
    def get_multiple_calls(self):
        return self.__m_c
class Label(Text_Box_Element):
    def __init__(self, pos: c, align: str, dimensions : c, *, 
                 
                 col = (200,200,200), img_name : str = None, 
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, 
                 
                 text = "Awesome Label", font_name : str = "Helvetica", text_col = (0,0,0)) -> None:
        super().__init__(pos, align, dimensions, text, font_name, text_col, col, img_name, border_width, border_color, border_img_name)
        self.__p = self._Menu_Element__p
        self.__a = self._Menu_Element__a
        self.__r = self._Text_Element__r

        self.__d = self._Text_Element__d
        self.__t = self._Text_Element__t
        self.__f_n = self._Text_Element__f_n
        self.__t_col = self._Text_Element__t_col
        self.__col = self._Text_Box_Element__col
        self.__i = self._Text_Box_Element__i
        self.__b_w = self._Text_Box_Element__b_w
        self.b_col = self._Text_Box_Element__b_col
        self.__b_i = self._Text_Box_Element__b_i

    '''def update(self, mouse_pos: c, clicking: bool, key_event=None):
        '''
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.__b_w>0:
            if self.__b_i==None:
                pygame.draw.rect(ui_config.screen, self.__b_col, self.__r.inflate(1+self.__b_w/self.__d.x*100, 1+self.__b_w/self.__d.y*100))
            else:
                ui_config.screen.blit(pygame.transform.scale(self.__b_i, self.__r.inflate(1+self.__b_w/self.__d.x*100, 1+self.__b_w/self.__d.y*100).size), (self.__r.left-(1+self.__b_w/self.__d.x*100)/2, self.__r.top-(1+self.__b_w/self.__d.y*100)/2))
        #Draw button
        if not self.__i==None:
            #If has image, draw image instead
            ui_config.screen.blit(pygame.transform.scale(self.__i, self.__r.size), self.__r.topleft)
        else: pygame.draw.rect(ui_config.screen, self.__col, self.__r)
        #Draw text
        if not self.__t=="":
            fit_text_to_rect(self.__t, self.__t_col, self.__f, self.__r), self.__r.topleft
        #print("Draw label")
class Text(Text_Element):
    def __init__(self, pos: c, align: str, height : int, 
                 
                 text = "Awesome Label", text_col = (0,0,0), font_name : str = "Helvetica", 
                 
                 highlight_col = (240,240,240)) -> None:
        super().__init__(pos, align, c(0,0), text, font_name, text_col)
        #kjdfghdlkjfgjkldfgjlkdfljgldkjfglkdfjglkjdfglkjdfkljgoieu5096tu4yihgolkfdhjnikolehfdyt89g4ey0hjuorlkhjfglkhjlkfghj
        #kljhdfhgoihgfiohgf

        w, h = paragraph_dim(text, text_col, font_name, height)
        self.__p = self.aligned_pos(c(w/h*height, height))
        self.__r = pygame.Rect(self.__p.x, ui_config.display_dimensions[1]-self.__p.y, w/h*height, height)

        self.__h_col = highlight_col
        self.__o_col = self._Text_Element__t_col

    def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display
        if self.__r.collidepoint(mouse_pos):
            #Text being highlighted
            self.__col = self.__h_col
        else:
            #Text not being highlighted
            self.__col = self.__o_col
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw Text
        if not self._Text_Box_Element__t=="":
            ui_config.screen.blit(self.__f.render(self._Text_Box_Element__t, True, self.__col), self.__r.topleft)
        #print("Draw text")
    def get_height(self):
        return self.__r.height
    def get_highlight_col(self):
        return (self.__h_col[0], self.__h_col[1], self.__h_col[2])
class Entry(Text_Box_Element):
    def __init__(self, pos: c, align: str, dimensions : c, text_height : int = None, *, 
                 
                 col = (200,200,200), img_name : str = None, 
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, 
                 
                 highlight_col = (240,240,240), highlight_img_name : str = None, 
                 
                 text = "", font_name : str = "Helvetica", text_col = (0,0,0), clamp_text : bool = True) -> None:
        super().__init__(pos, align, dimensions, text, font_name, text_col, col, img_name, border_width, border_color, border_img_name)
        self.__t_r = None
        self.__t_h = text_height

        self.__o_i = self._Text_Box_Element__i
        self.__h_i_n = highlight_img_name
        self.__h_i = None
        if not self.__h_i_n==None:
            try:
                self.__h_i = pygame.image.load(self.__h_i_n)
            except:
                print(f"ERROR: could not load image '{highlight_img_name}")

        self.__o_col = self._Text_Box_Element__col
        self.__h_col = highlight_col

        self.__selected = False

        self.__acitvate_on_click = True
        self.__type_cooldown = 0
        self.__last_key = None

        self.__ct = clamp_text

    def update(self, mouse_pos: c, clicking: bool, key_event=None):
        global update_display
        if self.__selected and not key_event==None:
            if self.__type_cooldown<=0 or not self.__last_key==key_event.key:
                if key_event.key==pygame.K_BACKSPACE:
                    self.__t = self.__t[:-1]    
                elif key_event.key==pygame.K_DELETE:
                    self.__t = ""
                elif key_event.key==pygame.K_RETURN:
                    self.__selected = False
                else:
                    self.__t+=key_event.unicode
                    if self.__ct and paragraph_dim(self.__t, self.__t_col, self.__f, self.__r.height)[0]>self.__r.width:
                        self.__t = self.__t[:-1]
                update_display = True
                self.__type_cooldown = 5

                display_text = fit_text_to_rect(self.__t, self.__t_col, self.__f, self.__r, self.__t_h, False, False)
                if self.__t_h==None: h = self.__r.height
                else: h = self.__t_h*(1+display_text.count("\n"))
                w, h = paragraph_dim(display_text, self.__t_col, self.__f, h)
                self.__t_r = pygame.Rect(self.__r.left, self.__r.top, w, h)

                self.__last_key = key_event.key

        if clicking:
            if self.__acitvate_on_click:
                if self.__r.collidepoint(mouse_pos) and not self.__selected:
                    self.__selected = True
                else: self.__selected = False
                self.__acitvate_on_click = False
        elif not self.__acitvate_on_click: 
            self.__acitvate_on_click = True

        if self.__selected and not (self.__col==self.__h_col and self.__i==self.__h_i):
            self.__col = self.__h_col
            self.__i = self.__h_i
            update_display = True
        elif not self.__selected and not (self.__col==self.__o_col and self.__i==self.__o_i):
            self.__col = self.__o_col
            self.__i = self.__o_i
            update_display = True

        self.__type_cooldown-=1
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self._Text_Box_Element__b_w>0:
            if self._Text_Box_Element__b_i==None:
                pygame.draw.rect(ui_config.screen, self.__b_col, self.__r.inflate(1+self._Text_Box_Element__b_w/self._Text_Element__d.x*100, 1+self._Text_Box_Element__b_w/self._Text_Element__d.y*100))
            else:
                ui_config.screen.blit(pygame.transform.scale(self._Text_Box_Element__b_i, self.__r.inflate(1+self._Text_Box_Element__b_w/self._Text_Element__d.x*100, 1+self._Text_Box_Element__b_w/self._Text_Element__d.y*100).size), (self.__r.left-(1+self._Text_Box_Element__b_w/self._Text_Element__d.x*100)/2, self.__r.top-(1+self._Text_Box_Element__b_w/self._Text_Element__d.y*100)/2))
        #Draw button
        if not self.__i==None:
            #If has image, draw image instead
            ui_config.screen.blit(pygame.transform.scale(self.__i, self.__r.size), self.__r.topleft)
        else: pygame.draw.rect(ui_config.screen, self.__col, self.__r)
        #Draw text
        if not self.__t=="":
            if self.__ct:
                ui_config.screen.blit(pygame.transform.scale(self.__f.render(self.__t, True, self.__t_col), self.__t_r.size), self.__r.topleft)
            else: fit_text_to_rect(self.__t, self.__t_col, self.__f, self.__r, self.__t_h, False), self.__r.topleft
        #print("Draw entry")
    def get_height(self):
        return self.__t_h
    def get_highlight_col(self):
        return (self.__h_col[0], self.__h_col[1], self.__h_col[2])
    def get_highlight_img_name(self):
        return self.__h_i_n
    def get_if_clamp(self):
        return self.__ct


#--------------------------------------------------------------------------------------Put it together-----------------------------------------------------------------------
def init_menus(display_d : tuple, start_menus : list = [], start_menu : int = 0):
    #global menus, current_menu_index, display_dimensions, screen
    ui_config.display_dimensions = display_d
    ui_config.screen = pygame.display.set_mode(ui_config.display_dimensions)
    ui_config.menus = start_menus
    ui_config.current_menu_index = start_menu

def main():
    '''f1 = False
    f2 = False'''
    #global redraw_stuff, update_display, current_menu_index, next_menu_index, clicking, exit_loop, key_pressed, menus
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            ui_config.exit_loop = True
        elif event.type==pygame.KEYDOWN:
            ui_config.key_pressed = event
            '''if event.key==pygame.K_a:
                f1 = True
            if event.key==pygame.K_d:
                f2 = True'''
        elif event.type==pygame.KEYUP:
            ui_config.key_pressed = None
            '''if event.key==pygame.K_a:
                f1 = False
            if event.key==pygame.K_d:
                f2 = False'''
        elif event.type==pygame.MOUSEBUTTONDOWN:
            ui_config.clicking = True
        elif event.type==pygame.MOUSEBUTTONUP:
            ui_config.clicking = False

    if len(ui_config.menus)==0: return

    '''if f1:
        menus[current_menu].menu_elements[0].r.width-=1
        update_display = True
    if f2:
        menus[current_menu].menu_elements[0].r.width+=1
        update_display = True'''
    
    if not ui_config.current_menu_index==ui_config.next_menu_index and ui_config.menus[ui_config.current_menu_index].ready_to_hide:
        ui_config.menus[ui_config.current_menu_index].switching_out = False
        ui_config.menus[ui_config.current_menu_index].ready_to_hide = False
        ui_config.menus[ui_config.current_menu_index].out_transition.c = ui_config.menus[ui_config.current_menu_index].out_transition.l

        ui_config.current_menu_index = ui_config.next_menu_index
        ui_config.update_display = True

        ui_config.menus[ui_config.current_menu_index].in_transition.c = ui_config.menus[ui_config.current_menu_index].in_transition.l

        print("Switch to", ui_config.current_menu_index)

    ui_config.menus[ui_config.current_menu_index].update(pygame.mouse.get_pos(), ui_config.clicking, ui_config.key_pressed)

    if ui_config.update_display:
        #print("Update")
        if ui_config.redraw_stuff: 
            #print("Draw menu")
            ui_config.menus[ui_config.current_menu_index].display()
        pygame.display.update(ui_config.menus[ui_config.current_menu_index].r)
        ui_config.redraw_stuff = True

    ui_config.clock.tick(60)

'''init((1200, 800))
init_menus([Menu([Button(c(500, 700), "center", c(200, 400), next_menu, border_img=bg_img), Label(c(0, 600), "nw", c(400, 100)), Text(c(100,800), "se", 50, "Hello World"), Entry(c(500, 800), "nw", c(300, 300), 50, clamp_text=False)], bg_img=bg_img), 
            Menu([Label(c(200, 200), "nw", c(200, 100), text="Welcome to menu 2"), Button(c(500, 500), "center", c(300, 100), prev_menu, text="If we could turn back time")], bg_col=(200, 200, 100))])


while not exit_loop:
    main()'''