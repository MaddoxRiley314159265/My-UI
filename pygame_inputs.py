import pygame

def int_input(prompt, range = None, positive = False):
    while True:
        i = input(prompt)
        try:
            i = int(i)
        except:
            print("Invalid integer input!")
        else: 
            if not range==None and (i<range[0] or i>range[1]): continue
            elif i>=0 or not positive: break
    return i
def choice_input(prompt, choices):
    while True:
        i = input(prompt)
        if i.lower() in choices: break
def color_input(prompt) -> pygame.Color:
    print(prompt+":")
    ui = int_input("Would you like to provide color name(0) or set rgb values(1)? ", (0,1))
    if ui==0:
        while True:
            cn = input("Color name: ")
            try:
                c = pygame.Color(cn)
            except ValueError:
                print("Invalid color name!")
            else: break
        return c
    elif ui==1:
        r = int_input("Red val: ", (0,255))
        g = int_input("Green val: ", (0,255))
        b = int_input("Blue val: ", (0,255))
        return pygame.Color((r,g,b))
def img_input(prompt):
    while True:
        ui = input(prompt+" image name (None for none): ")
        if ui.lower()=="none": return None
        try:
            i = pygame.image.load(ui)
        except:
            print("Invalid image name!")
        else:
            break
    return ui
def font_input():
    while True:
        ui = input("Font name: ")
        if not font_name_to_font(ui)==None: break

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

#Color to tuple
def c_t(color : pygame.Color | tuple):
    return (color[0], color[1], color[2])