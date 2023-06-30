import pygame
from textwrap import fill
from pygame_inputs import pygame
import ui_config
from json import loads, dumps
from pygame_inputs import *

pygame.init()
f1 = pygame.font.SysFont("Helvetica", 500)

alignments = ["center", "nw", "sw", "ne", "se"]
transitions = ["fade transition"]

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
button_funcs = {"next_menu" : next_menu, "prev_menu" : prev_menu, "say_hello" : say_hello, "exit" : exit}

#----------------------------------------------------------Handy Functions-------------------------------------------------\
def get_key(key_val_pair): return list(key_val_pair.keys())[0]
def get_val(key_val_pair): return list(key_val_pair.values())[0]

file_version = 1
def save(save_file : str):
    r_f = open(save_file, "r")

    saves = r_f.read()
    fallback = saves

    if not saves=="": saves = loads(saves)
    else: saves = {}

    r_f.close()


    save_name = input("Save name? (Nothing to not save): ")
    if save_name=="": return

    saves.update({save_name : {
    #Save file format version
    "file_version" : file_version,

    #Save screen size
    "screen_size" : ui_config.display_dimensions,
    #Save current menu
    "open_menu" : ui_config.current_menu_index,
    #Save menus
    "menus" : [serialize(m) for m in ui_config.menus]

    }} )

    '''print(saves[save_name]["menus"][0]["elements"])
    
    print(dumps(saves, indent=4))'''
    f = open(save_file, "w")
    try:
        json = dumps(saves, indent=4)
    except:
        print("ERROR: could not convert to JSON")
        f.write(fallback)
    else:
        f.write(json)
    f.close()
def load(save_file : str, save_name : str):
    f = open(save_file, "r")

    try:
        my_save = loads(f.read())[save_name]
    except:
        print(f"Invalid save name '{save_name}'")
        return -1

    if not my_save["file_version"]==file_version:
        #File version
        print(f"WARNING: current version is {file_version} while this file's version is {my_save['file_version']}")

    #Display dimensions
    ui_config.display_dimensions = my_save["screen_size"]
    ui_config.screen = pygame.display.set_mode(ui_config.display_dimensions)

    ui_config.current_menu_index = my_save["open_menu"]

    my_menus = my_save["menus"]

    ui_config.menus = [None]*len(my_menus)
    #Menus
    for mi in range(len(my_menus)):
        #Menu
        ui_config.menus[mi] = deserialize(my_menus[mi])
    return 0

def serialize(obj):
    if isinstance(obj, classes["Menu"]):
        #Menu contructor arguments
        return {"elements" : [serialize(e) for e in obj.menu_elements], "rect" : (obj.r.left, obj.r.top, obj.r.width, obj.r.height), "in_transition" : serialize(obj.in_transition), "out_transition" : serialize(obj.out_transition), "bg_color" : c_t(obj.bg_col), "bg_image_name" : obj.bg_img_n}
    elif isinstance(obj, classes["Fade_Transition"]):
        #Fade transition contructor arguments
        return {"Fade_Transition" :  {"life" : obj.l, "fade_setting" : obj.get_fade_setting(), "color" : c_t(obj.col), "fade_modifier" : obj.get_fade_modifier()}}
    elif isinstance(obj, classes["Button"]):
        #Button contructor arguments
        return {"Button" : {"rect" : (obj.r.left, obj.r.top, obj.r.width, obj.r.height), "alignment" : obj.a,"action_name" : obj.get_action_name(), "color" : c_t(obj.col), "image_name" : obj.i_n, "highlight_col" : obj.get_highlight_col(), "highlight_image_name" : obj.get_highlight_img_name(), "border_width" : obj.b_w, "border_color" : c_t(obj.b_col), "border_image_name" : obj.b_i_n, "text" : obj.t, "font" : obj.f_n, "text_color" : c_t(obj.t_col), "highlight_inflation" : obj.get_highlight_inflation(), "click_inflation" : obj.get_click_inflation(), "continuous_call" : obj.get_multiple_calls(), "align_pos" : False}}
    elif isinstance(obj, classes["Label"]):
        #Label contructor arguments
        return {"Label" : {"rect" : (obj.r.left, obj.r.top, obj.r.width, obj.r.height), "alignment" : obj.a, "color" : c_t(obj.col), "image_name" : obj.i_n, "border_width" : obj.b_w, "border_color" : c_t(obj.b_col), "border_image_name" : obj.b_i_n, "text" : obj.t, "font" : obj.f_n, "text_color" : c_t(obj.t_col), "align_pos" : False}}
    elif isinstance(obj, classes["Text"]):
        #Text contructor arguments
        return {"Text" : {"rect" : (obj.r.left, obj.r.top, obj.r.width, obj.r.height), "alignment" : obj.a, "text" : obj.t, "font" : obj.f_n, "text_color" : c_t(obj.t_col), "highlight_col" : obj.get_highlight_col(), "recalculate text bounds" : False, "align_pos" : False}}
    elif isinstance(obj, classes["Entry"]):
        #Entry contructor arguments
        return {"Entry" : {"rect" : (obj.r.left, obj.r.top, obj.r.width, obj.r.height), "alignment" : obj.a, "text_height" : obj.get_text_height(), "color" : c_t(obj.col), "image_name" : obj.i_n, "border_width" : obj.b_w, "border_color" : c_t(obj.b_col), "border_image_name" : obj.b_i_n, "highlight_col" : obj.get_highlight_col(), "highlight_image_name" : obj.get_highlight_img_name(), "text" : obj.t, "font" : obj.f_n, "text_color" : c_t(obj.t_col), "clamp_text" : obj.get_if_clamp(), "align_pos" : False}}
    
def deserialize(obj):
    if get_key(obj)=="elements":
        #Menu
        my_elements = [None]*len(obj["elements"])
        for me_i, me in enumerate(obj["elements"]):
            my_elements[me_i] = deserialize(me)
                
        return Menu(my_elements, obj["rect"], classes[get_key(obj["in_transition"])](*list(get_val(obj["in_transition"]).values())), classes[get_key(obj["out_transition"])](*list(get_val(obj["out_transition"]).values())), *list(obj.values())[4:])
    else:
        my_element_name = get_key(obj)
        if classes.get(my_element_name)==None:
            print(f"ERROR: no class type '{my_element_name}'")
        else:
            return classes[my_element_name](*list(get_val(obj).values()))
    

def fit_text_to_rect(text : str, font_col, font : pygame.font.Font, fit_rect : pygame.Rect, text_height : int = None, flex_text : bool = True, display : bool = True):
    if text=="": return ""
    if flex_text: max_width_over = 200
    else: max_width_over = 0

    wrap = len(text)-1
    if text_height==None: t_h = fit_rect.height
    else: 
        t_h = text_height

    formatted_text = text
    while paragraph_dim(formatted_text, font_col, font, t_h, flex_text)[0]-fit_rect.width>max_width_over:
        if wrap<=0:
            break
        formatted_text = fill(text, wrap)

        wrap-=1

    if wrap<0:
        print("ERROR: could not wrap text:", text)
        return
    return formatted_text
def line_width(text : str, font_col, font : str, height):
    w, h = font.render(text, True, font_col).get_rect().size
    w_to_h = w/h

    return height*w_to_h
def paragraph_dim(text : str, font_col, font : pygame.font.Font, height, flex_text : bool = True):
    width = 0
    if flex_text: height = height/(1+text.count("\n"))
    for line in text.split("\n"):
        w = line_width(line, font_col, font, height)

        if w>width: width = w
    return width, height*(1+text.count("\n"))
def render_paragraph(text : str, font_col, font : pygame.font.Font, target_rect : pygame.Rect, height : int = None, flex_text : bool = True):
    if flex_text: height = height/(1+text.count("\n"))
    for i, line in enumerate(text.split("\n")):
        if height==None: height = target_rect.height
        w = line_width(line, font_col, font, height)
        if w>target_rect.width and flex_text: w = target_rect.width
        ui_config.screen.blit(pygame.transform.scale(font.render(line, True, font_col), (w,height)), (target_rect.left, target_rect.top+i*height))

def new_thingy(choice : str, trans_out = None):
    if choice.lower()=="menu":
        print("Creating menu...")
        ui_config.menus.append(Menu(list(), pygame.Rect(int_input("Menu x (0(left)->screen width): ", (0,ui_config.display_dimensions[0])), int_input("Menu y (0(top)->screen height)", (0,ui_config.display_dimensions[1])), int_input("Menu width: ", (1,ui_config.display_dimensions[0])), int_input("Menu height: ", (1,ui_config.display_dimensions[1]))), new_thingy(choice_input("Type of transition for switching to this menu: ", transitions),True), new_thingy(choice_input("Type of transition for switching from this menu: ", transitions),True), color_input("Background color"), img_input("Background")))
    elif choice.lower()=="fade transition":
        return Fade_Transition(int_input("Transition duration (def 100): "), trans_out, color_input("Color"), int_input("Transition smoothing: ", (0,3)))
    #More transitions
    elif choice.lower()=="button":
        ui_config.menus[ui_config.current_menu_index].menu_elements.append(Button(pygame.Rect(int_input("Pos x: ",(0,ui_config.display_dimensions[0])), int_input("Pos y: ",(0,ui_config.display_dimensions[1])), int_input("Width: ",(0,ui_config.display_dimensions[0])), int_input("Height: ",(0,ui_config.display_dimensions[1]))), choice_input("Alignment: ", alignments), choice_input("Action name: ", button_funcs.keys()), color_input("Color"), img_input("Background"), color_input("Highlight color"), img_input("Background when highlighted"), int_input("Border widith: "), color_input("Border color"), img_input("Border image"), input("Button text: "), font_input(), color_input("Text color"), int_input("Inflate button on highlight: "), int_input("Inflate button on click: ")))
    elif choice.lower()=="label":
        ui_config.menus[ui_config.current_menu_index].menu_elements.append(Label(pygame.Rect(int_input("Pos x: ",(0,ui_config.display_dimensions[0])), int_input("Pos y: ",(0,ui_config.display_dimensions[1])), int_input("Width: ",(0,ui_config.display_dimensions[0])), int_input("Height: ",(0,ui_config.display_dimensions[1]))), choice_input("Alignment: ", alignments), color_input("Color"), img_input("Background"), int_input("Border widith: "), color_input("Border color"), img_input("Border image"), input("Label text: "), font_input(), color_input("Text color")))
    elif choice.lower()=="text":
        ui_config.menus[ui_config.current_menu_index].menu_elements.append(Text(pygame.Rect(int_input("Pos x: ",(0,ui_config.display_dimensions[0])), int_input("Pos y: ",(0,ui_config.display_dimensions[1])), int_input("Width: ",(0,ui_config.display_dimensions[0])), int_input("Height: ",(0,ui_config.display_dimensions[1]))), choice_input("Alignment: ", alignments), input("Text: "), font_input(), color_input("Text color"), color_input("Highlight color")))
    elif choice.lower()=="entry":
        ui_config.menus[ui_config.current_menu_index].menu_elements.append(Entry(pygame.Rect(int_input("Pos x: ",(0,ui_config.display_dimensions[0])), int_input("Pos y: ",(0,ui_config.display_dimensions[1])), int_input("Width: ",(0,ui_config.display_dimensions[0])), int_input("Height: ",(0,ui_config.display_dimensions[1]))), choice_input("Alignment: ", alignments), int_input("Text height: "), color_input("Color"), img_input("Background"), int_input("Border widith: "), color_input("Border color"), img_input("Border image"), color_input("Highlight color"), img_input("Background when highlighted"), input("Entry text: "), font_input(), color_input("Text color")))
    elif choice.lower()=="paragraph":
        ui_config.menus[ui_config.current_menu_index].menu_elements.append(Paragraph(pygame.Rect(int_input("Pos x: ",(0,ui_config.display_dimensions[0])), int_input("Pos y: ",(0,ui_config.display_dimensions[1])), int_input("Width: ",(0,ui_config.display_dimensions[0])), int_input("Height: ",(0,ui_config.display_dimensions[1]))), choice_input("Alignment: ", alignments), int_input("Text height: "), input("Text: "), font_input(), color_input("Text color")))
    
    print("\nComplete!\n")

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
        ui_config.screen.blit(s, menu_rect)
        ui_config.redraw_stuff = False
        #print("Draw transition")

        self.c-=1

    def get_fade_setting(self):
        return self.fo
    def get_fade_modifier(self):
        return self.fm

class Menu:
    def __init__(self, me : list = list(), rect : pygame.Rect = None, in_t : Transition = Fade_Transition(100, fade_modifier=2), out_t : Transition = Fade_Transition(100, False, fade_modifier=2), #*, 
                 bg_col : pygame.Color = pygame.Color("white"), bg_img_name : str = None) -> None:
        if rect==None: rect = ui_config.screen.get_rect()
        elif not isinstance(rect, pygame.Rect): rect = pygame.Rect(rect)
        self.r = rect
        self.__s = pygame.Surface(self.r.size)

        self.menu_elements = me
        self.in_transition = in_t
        self.out_transition = out_t

        self.switching_out = False
        self.ready_to_hide = False

        self.bg_col = bg_col
        self.bg_img = None
        self.bg_img_n = bg_img_name
        if self.bg_img==None and not self.bg_img_n==None:
            self.bg_img = pygame.image.load(self.bg_img_n)
        elif self.bg_img_n==None and not self.bg_img==None:
            raise Exception("Error, must provide image file name when providing image")

        #self.draw_menu()

    def update(self, mouse_pos : tuple, clicking : bool, key_event = None):
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
            self.__s.fill(self.bg_col)
        else:
            #screen.fill((255,255,255))
            self.__s.blit(pygame.transform.scale(self.bg_img, self.r.size), (0,0))

        ui_config.screen.blit(self.__s, self.r.topleft)
        #print("Draw bg")

    def display(self):
        global update_display
        #Erase elements by drawing menu again, then display each element
        self.draw_menu()
        for e in self.menu_elements:
            e.display()
        update_display = False



#------------------------------------------------------------------Menu Elements------------------------------------------------------------------
class Menu_Element:
    def __init__(self, rect : pygame.Rect, align : str, align_pos = True) -> None:
        if not isinstance(rect, pygame.Rect): rect = pygame.Rect(rect)
        self.r = rect
        self.a = align
        if align_pos: self.align()
    def align(self):
        if self.a=="nw":
            pass
        elif self.a=="ne":
            self.r.topleft = (self.r.left-self.r.w)
        elif self.a=="se":
            self.r.topleft = (self.r.left-self.r.w, self.r.top-self.r.h)
        elif self.a=="sw":
            self.r.topleft = (self.r.left, self.r.top-self.r.h)
        elif self.a=="center":
            self.r.topleft = (self.r.left-self.r.w/2, self.r.top-self.r.h/2)
        else:
            print(f"ERROR: Invalid alignment '{self.a}'")

    def update(self, mouse_pos : tuple, clicking : bool, key_event = None):
        pass #Update appearence
    def display(self):
        pass #Display
class Text_Element(Menu_Element):
    def __init__(self, rect : pygame.Rect, align : str, 
                 
                 text : str = "Press Me", font_name : str = "Helvetica", text_col = (0,0,0), align_pos = True) -> None:
        super().__init__(rect, align, align_pos)

        self.t = text
        self.t_col = text_col
        self.f_n = font_name
        self.f = font_name_to_font(self.f_n)
class Text_Box_Element(Text_Element):
    def __init__(self, rect : pygame.Rect, align : str,
                 
                 text: str = "Press Me", font_name: str = "Helvetica", text_col=(0, 0, 0),
                 
                 col = (200,200,200), img_name : str = None,
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, align_pos = True) -> None:
        super().__init__(rect, align, text, font_name, text_col, align_pos)
        self.col = col

        self.i_n = img_name
        self.i = None
        if not self.i_n==None:
            try:
                self.i = pygame.image.load(self.i_n)
            except:
                print(f"ERROR: could not load image '{img_name}")

        self.b_w = border_width
        self.b_col = border_color
        self.b_i_n = border_img_name
        self.b_i = None
        if not self.b_i_n==None:
            try:
                self.b_i = pygame.image.load(self.b_i_n)
            except:
                print(f"ERROR: could not load image '{border_img_name}")
class Button(Text_Box_Element):
    def __init__(self, rect : pygame.Rect, align : str, action_name : str, #*, 
                 col = (200,200,200), 
                 
                 img_name : str = None, highlight_col = (240,240,240), highlight_img_name : str = None, 
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, 
                 
                 text : str = "Press Me", font_name : str = "Helvetica", text_col = (0,0,0), 
                 
                 inflate_on_hightlight = 2, inflate_on_click = 4, multiple_calls = False, align_pos = True) -> None:
        super().__init__(rect, align, text, font_name, text_col, col, img_name, border_width, border_color, border_img_name, align_pos)

        '''self.d = self._Text_Elementd
        self.t = self._Text_Elementt
        self.f = self._Text_Elementf
        self.t_col = self._Text_Elementt_col
        self.col = self._Text_Box_Elementcol
        self.__i = self._Text_Box_Element__i
        self.b_w = self._Text_Box_Elementb_w
        self.b_col = self._Text_Box_Elementb_col
        self.b_i = self._Text_Box_Elementb_i'''


        self.__o_r = self.r
        self.__o_i = self.i
        

        self.__h_i_n = highlight_img_name
        self.__h_i = None
        if not self.__h_i_n==None:
            try:
                self.__h_i = pygame.image.load(self.__h_i_n)
            except:
                print(f"ERROR: could not load image '{highlight_img_name}")

        self.__o_col = self.col
        self.__h_col = highlight_col

        self.__func_n = action_name


        self.__i_h = inflate_on_hightlight
        self.__i_c = inflate_on_click

        self.__m_c = multiple_calls
        self.__acitvate_on_click = True
    def update(self, mouse_pos: tuple, clicking: bool, key_event=None):
        global update_display
        
        #If mouse hovering
        if self.r.collidepoint(mouse_pos[0], mouse_pos[1]):
            if not self.r==self.__o_r.inflate(self.__i_h, self.__i_h):
                self.r = self.__o_r.inflate(self.__i_h, self.__i_h)

                if self.__h_i==None: self.col = self.__h_col
                else: self.i = self.__h_i
                update_display = True
            #If button clicked
            if clicking and self.__acitvate_on_click:
                if not self.r==self.__o_r.inflate(self.__i_c, self.__i_c):
                    self.r = self.__o_r.inflate(self.__i_c, self.__i_c)
                    update_display = True
                button_funcs[self.__func_n]()
                #Only activate once
                if not self.__m_c:
                    self.__acitvate_on_click = False
            elif not clicking and not self.__acitvate_on_click:
                #Reset to activate once clicked again
                self.__acitvate_on_click = True

        elif not self.r==self.__o_r:
            self.col = self.__o_col
            self.i = self.__o_i
            self.r = self.__o_r
            update_display = True
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.b_w>0:
            w, h = self.r.w, self.r.h
            if self.b_i==None:
                pygame.draw.rect(ui_config.screen, self.b_col, self.r.inflate(1+self.b_w/w*100, 1+self.b_w/h*100))
            else:
                ui_config.screen.blit(pygame.transform.scale(self.b_i, self.r.inflate(1+self.b_w/w*100, 1+self.b_w/h*100).size), (self.r.left-(1+self.b_w/w*100)/2, self.r.top-(1+self.b_w/h*100)/2))
        #Draw button
        if not self.i==None:
            #If has image, draw image instead
            ui_config.screen.blit(pygame.transform.scale(self.i, self.r.size), self.r.topleft)
        else: pygame.draw.rect(ui_config.screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            fit_text_to_rect(self.t, self.t_col, self.f, self.r)
        #print("Draw button")
    def get_action(self):
        return button_funcs[self.__func_n]
    def get_action_name(self):
        return self.__func_n
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
    def __init__(self, rect : pygame.Rect, align : str,# *, 
                 
                 col = (200,200,200), img_name : str = None, 
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, 
                 
                 text = "Awesome Label", font_name : str = "Helvetica", text_col = (0,0,0), align_pos = True) -> None:
        super().__init__(rect, align, text, font_name, text_col, col, img_name, border_width, border_color, border_img_name, align_pos)
        '''self.p = self._Menu_Elementp
        self.__a = self._Menu_Element__a
        self.r = self._Text_Elementr

        self.d = self._Text_Elementd
        self.t = self._Text_Elementt
        self.f = self._Text_Elementf
        self.t_col = self._Text_Elementt_col
        self.col = self._Text_Box_Elementcol
        self.__i = self._Text_Box_Element__i
        self.b_w = self._Text_Box_Elementb_w
        self.b_col = self._Text_Box_Elementb_col
        self.b_i = self._Text_Box_Elementb_i'''

    '''def update(self, mouse_pos: c, clicking: bool, key_event=None):
        '''
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.b_w>0:
            w, h = self.r.w, self.r.h
            if self.b_i==None:
                pygame.draw.rect(ui_config.screen, self.b_col, self.r.inflate(1+self.b_w/w*100, 1+self.b_w/h*100))
            else:
                ui_config.screen.blit(pygame.transform.scale(self.b_i, self.r.inflate(1+self.b_w/w*100, 1+self.b_w/h*100).size), (self.r.left-(1+self.b_w/w*100)/2, self.r.top-(1+self.b_w/h*100)/2))
        #Draw button
        if not self.i==None:
            #If has image, draw image instead
            ui_config.screen.blit(pygame.transform.scale(self.i, self.r.size), self.r.topleft)
        else: pygame.draw.rect(ui_config.screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            fit_text_to_rect(self.t, self.t_col, self.f, self.r)
        #print("Draw label")
class Text(Text_Element):
    def __init__(self, rect : pygame.Rect, align : str,
                 
                 text = "Awesome Label", font_name : str = "Helvetica", text_col = (0,0,0), 
                 
                 highlight_col = (240,240,240), recalc_rect = True, align_pos = True) -> None:
        super().__init__(rect, align, text, font_name, text_col, align_pos)
        
        self.__h_col = highlight_col
        self.__o_col = self.t_col

        if recalc_rect:
            w, h = paragraph_dim(text, text_col, self.f, self.r.h)
            self.r.w = w/h*self.r.h


    def update(self, mouse_pos: tuple, clicking: bool, key_event=None):
        global update_display
        if self.r.collidepoint(mouse_pos):
            #Text being highlighted
            self.t_col = self.__h_col
        else:
            #Text not being highlighted
            self.t_col = self.__o_col
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw Text
        if not self.t=="":
            ui_config.screen.blit(pygame.transform.scale(self.f.render(self.t, True, self.t_col), self.r.size), self.r.topleft)
        #print("Draw text")
    def get_highlight_col(self):
        return (self.__h_col[0], self.__h_col[1], self.__h_col[2])
class Entry(Text_Box_Element):
    def __init__(self, rect : pygame.Rect, align : str, text_height : int = None,# *, 
                 
                 col = (200,200,200), img_name : str = None, 
                 
                 border_width = 20, border_color = (0,0,0), border_img_name : str = None, 
                 
                 highlight_col = (240,240,240), highlight_img_name : str = None, 
                 
                 text = "", font_name : str = "Helvetica", text_col = (0,0,0), clamp_text : bool = True, align_pos = True) -> None:
        super().__init__(rect, align, text, font_name, text_col, col, img_name, border_width, border_color, border_img_name, align_pos)
        '''self.d = self._Text_Elementd
        self.r = self._Text_Elementr

        self.t = self._Text_Elementt
        self.f = self._Text_Elementf'''
        self.__t_r = None
        self.__t_h = text_height
        '''self.t_col = self._Text_Elementt_col

        self.__i = self._Text_Box_Element__i'''
        self.__o_i = self.i
        self.__h_i_n = highlight_img_name
        self.__h_i = None
        if not self.__h_i_n==None:
            try:
                self.__h_i = pygame.image.load(self.__h_i_n)
            except:
                print(f"ERROR: could not load image '{highlight_img_name}")

        #self.col = self._Text_Box_Elementcol
        self.__o_col = self.col
        self.__h_col = highlight_col

        '''self.b_w = self._Text_Box_Elementb_w
        self.b_col = self._Text_Box_Elementb_col
        self.b_i = self._Text_Box_Elementb_i'''

        self.__selected = False

        self.__acitvate_on_click = True
        self.__type_cooldown = 0
        self.__last_key = None

        self.__ct = clamp_text
        self.__reformat = True

    def update(self, mouse_pos: tuple, clicking: bool, key_event=None):
        global update_display
        if self.__reformat:
            #Reformat text
            display_text = fit_text_to_rect(self.t, self.t_col, self.f, self.r, self.__t_h, False)
            if self.__t_h==None: h = self.r.height
            else: h = self.__t_h*(1+display_text.count("\n"))
            w, h = paragraph_dim(display_text, self.t_col, self.f, h)
            self.__t_r = pygame.Rect(self.r.left, self.r.top, w, h)
            self.__reformat = False

        if self.__selected and not key_event==None:
            if self.__type_cooldown<=0 or not self.__last_key==key_event.key:
                if key_event.key==pygame.K_BACKSPACE:
                    self.t = self.t[:-1]    
                elif key_event.key==pygame.K_DELETE:
                    self.t = ""
                elif key_event.key==pygame.K_RETURN:
                    self.__selected = False
                else:
                    self.t+=key_event.unicode
                    if self.__ct and paragraph_dim(self.t, self.t_col, self.f, self.r.height)[0]>self.r.width:
                        self.t = self.t[:-1]
                update_display = True
                self.__type_cooldown = 5

                self.__reformat = True

                self.__last_key = key_event.key

        if clicking:
            if self.__acitvate_on_click:
                if self.r.collidepoint(mouse_pos) and not self.__selected:
                    self.__selected = True
                else: self.__selected = False
                self.__acitvate_on_click = False
        elif not self.__acitvate_on_click: 
            self.__acitvate_on_click = True

        if self.__selected and not (self.col==self.__h_col and self.i==self.__h_i):
            self.col = self.__h_col
            self.i = self.__h_i
            update_display = True
        elif not self.__selected and not (self.col==self.__o_col and self.i==self.__o_i):
            self.col = self.__o_col
            self.i = self.__o_i
            update_display = True

        self.__type_cooldown-=1
        
    def display(self):
        #self.r = pygame.Rect(100, 100, 400, 400)
        #Draw border
        if self.b_w>0:
            w, h = self.r.w, self.r.h
            if self.b_i==None:
                pygame.draw.rect(ui_config.screen, self.b_col, self.r.inflate(1+self.b_w/w*100, 1+self.b_w/h*100))
            else:
                ui_config.screen.blit(pygame.transform.scale(self.b_i, self.r.inflate(1+self.b_w/w*100, 1+self.b_w/h*100).size), (self.r.left-(1+self.b_w/w*100)/2, self.r.top-(1+self.b_w/h*100)/2))
        #Draw middle
        if not self.i==None:
            #If has image, draw image instead
            ui_config.screen.blit(pygame.transform.scale(self.i, self.r.size), self.r.topleft)
        else: pygame.draw.rect(ui_config.screen, self.col, self.r)
        #Draw text
        if not self.t=="":
            if self.__ct:
                ui_config.screen.blit(pygame.transform.scale(self.f.render(self.t, True, self.t_col), self.__t_r.size), self.r.topleft)
            else: fit_text_to_rect(self.t, self.t_col, self.f, self.r, self.__t_h, False)
        #print("Draw entry")
    def get_text_height(self):
        return self.__t_h
    def inc_text_height(self, amount):
        self.__t_h+=amount
        self.__reformat = True
    def dec_text_height(self, amount):
        self.__t_h-=amount
        self.__reformat = True

    def get_if_clamp(self):
        return self.__ct
class Paragraph(Text_Element):
    def __init__(self, rect: pygame.Rect, align: str, 
                 
                 text_height : int, text: str = "", font_name: str = "Helvetica", text_col=(0, 0, 0), align_pos=True) -> None:
        super().__init__(rect, align, text, font_name, text_col, align_pos)
        self.__t_h = text_height
        
        #Reformat text
        self.t = fit_text_to_rect(self.t, self.t_col, self.f, self.r, self.__t_h, False)
        if self.__t_h==None: h = self.r.height
        else: h = self.__t_h*(1+self.t.count("\n"))
        w, h = paragraph_dim(self.t, self.t_col, self.f, h)
        self.__t_r = pygame.Rect(self.r.left, self.r.top, w, h)

    def display(self):
        if not self.t=="":
            render_paragraph(self.t, self.t_col, self.f, self.__t_r, self.__t_h, False)


classes = {"Menu" : Menu, "Fade_Transition" : Fade_Transition, "Button" : Button, "Label" : Label, "Text" : Text, "Entry" : Entry, "Paragraph" : Paragraph}


#--------------------------------------------------------------------------------------Put it together-----------------------------------------------------------------------
def init_menus(display_d : tuple, start_menus : list = [], start_menu : int = 0):
    #global menus, current_menu_index, display_dimensions, screen
    ui_config.display_dimensions = display_d
    ui_config.screen = pygame.display.set_mode(ui_config.display_dimensions)
    ui_config.menus = start_menus
    ui_config.current_menu_index = start_menu

def main(disable_elements = False, select_rect : pygame.Rect = None):
    '''f1 = False
    f2 = False'''
    #global redraw_stuff, update_display, current_menu_index, next_menu_index, clicking, exit_loop, key_pressed, menus
    events = pygame.event.get()
    if not disable_elements:
        for event in events:
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

    if len(ui_config.menus)==0: return events

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

        ui_config.menus[ui_config.current_menu_index].in_transition.c = ui_config.menus[ui_config.current_menu_index].in_transition.l

        print("Switch to", ui_config.current_menu_index)

    ui_config.menus[ui_config.current_menu_index].update(pygame.mouse.get_pos(), ui_config.clicking, ui_config.key_pressed)

    ui_config.screen.fill(ui_config.bg_col)
    if ui_config.redraw_stuff: 
        #print("Draw menu")
        ui_config.menus[ui_config.current_menu_index].display()
    ui_config.redraw_stuff = True

    if not select_rect==None:
        pygame.draw.rect(ui_config.screen, ui_config.select_rect_col, select_rect,width=20)

    pygame.display.flip()
    ui_config.clock.tick(60)
    return events

'''init((1200, 800))
init_menus([Menu([Button(c(500, 700), "center", c(200, 400), next_menu, border_img=bg_img), Label(c(0, 600), "nw", c(400, 100)), Text(c(100,800), "se", 50, "Hello World"), Entry(c(500, 800), "nw", c(300, 300), 50, clamp_text=False)], bg_img=bg_img), 
            Menu([Label(c(200, 200), "nw", c(200, 100), text="Welcome to menu 2"), Button(c(500, 500), "center", c(300, 100), prev_menu, text="If we could turn back time")], bg_col=(200, 200, 100))])


while not exit_loop:
    main()'''