from my_ui import *
from VectorUtil import c
from pygame_inputs import int_input
import ui_config
import pygame

save_file = "ui_saves.json"
unsaved_changes = False

new_thingies = [k.lower() for k in classes.keys()]
for nt in new_thingies:
    if "transition" in nt.lower():
        new_thingies.remove(nt)

pygame.init()

#'''
while True:
    load_name = input("Load save? (Don't type to start new save): ")
    if not load_name=="": 
        if load(save_file, load_name)>=0: break
    else:
        dd = (int(int_input("Screen width: ")), int(int_input("Screen height: ")))
        ui_config.bg_col = color_input("Background color")
        init_menus(dd)
        break
        #ui_config.menus.append(Menu())
        #'''

'''
init_menus((1000, 800))

ui_config.menus.extend([Menu([Button(pygame.Rect(500, 700, 200, 400), "center", "next_menu", border_img_name=bg_img_name), Label(pygame.Rect(0, 600, 400, 100), "nw"), Text(pygame.Rect(500,800, 50,1), "se", "Hello World"), Entry(pygame.Rect(500, 800, 300, 300), "nw", 50, clamp_text=False)], bg_img_name=bg_img_name), 
            Menu([Label(pygame.Rect(200, 200, 200, 100), "nw", text="Welcome to menu 2"), Button(pygame.Rect(500, 500, 300, 100), "center", "prev_menu", text="If we could turn back time")], bg_col=(200, 200, 100))])
'''
    
print("Press n to create a new menu or menu element")

def click(pos):
    global edit_element
    clicked_element = False
    if ui_config.menus[ui_config.current_menu_index].r.collidepoint(pos):
        #Click is inside menu
        if not edit_element==None and edit_element.r.collidepoint(pos):
            #Click the already clicked element, deselect everything
            edit_element = None
            print("Deselect")
            clicked_element = True
        else:
            for e in ui_config.menus[ui_config.current_menu_index].menu_elements:
                if e.r.collidepoint(pos):
                    edit_element = e
                    print("Selected", edit_element)
                    clicked_element = True
        if not clicked_element:
            if edit_element==ui_config.menus[ui_config.current_menu_index]: 
                print("Deselect menu")
                edit_element = None
            else:
                edit_element = ui_config.menus[ui_config.current_menu_index]
                print("Selected current menu")

def act(a, coord, move_mult):
    global unsaved_changes
    unsaved_changes = True
    if a%4==0: return (coord+c(0,-1)*move_mult).t()
    elif a%4==1: return (coord+c(-1,0)*move_mult).t()
    elif a%4==2: return (coord+c(0,1)*move_mult).t()
    elif a%4==3: return (coord+c(1,0)*move_mult).t()

key_acts = {pygame.K_w : 0, pygame.K_a : 1, pygame.K_s : 2, pygame.K_d : 3, pygame.K_UP : 4, pygame.K_LEFT : 5, pygame.K_DOWN : 6, pygame.K_RIGHT : 7}

current_acts = []
fine_tune = False

copy_thing = None

edit_element = None
while not ui_config.exit_loop:
    if edit_element==None: select_rect = None
    else: select_rect = edit_element.r

    for event in main(True,select_rect):
        if event.type==pygame.QUIT:
            ui_config.exit_loop = True
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_n:
                #Create new thingy
                new_thing = ""
                while not new_thing in new_thingies and not new_thing.lower()=="none":
                    new_thing = input("What would you like to add? (None to cancel): ").lower()
                if not new_thing.lower()=="none":
                    unsaved_changes = True
                    new_thingy(new_thing)
            elif not key_acts.get(event.key)==None:
                current_acts.append(key_acts.get(event.key))
            elif event.key==pygame.K_LSHIFT:
                fine_tune = True
            elif event.key==pygame.K_c:
                print("Copied", edit_element)
                copy_thing = serialize(edit_element)
            elif event.key==pygame.K_v:
                unsaved_changes = True
                paste_thing = deserialize(copy_thing)
                print("Pasted", paste_thing)
                if isinstance(paste_thing, Menu):
                    ui_config.menus.append(paste_thing)
                else:
                    ui_config.menus[ui_config.current_menu_index].menu_elements.append(paste_thing)
            elif event.key==pygame.K_p:
                save(save_file)

        elif event.type==pygame.KEYUP:
            if not key_acts.get(event.key)==None:
                current_acts.remove(key_acts.get(event.key))
            elif event.key==pygame.K_LSHIFT:
                fine_tune = False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if len(ui_config.menus)>0: click(pygame.mouse.get_pos())
        #elif event.type==pygame.MOUSEBUTTONUP:

    if not edit_element==None:
        if fine_tune: move_mult = 1
        else: move_mult = 5
        p = c(edit_element.r.topleft)
        d = c(edit_element.r.size)
        if len(current_acts)>0:
            for a in current_acts:
                if a<4: edit_element.r.topleft = act(a, p, move_mult)

                else: edit_element.r.size = act(a, d, move_mult)
            if isinstance(edit_element, Menu):
                #If moving menu, also move its elements
                for e in edit_element.menu_elements:
                    p = c(e.r.topleft)
                    d = c(e.r.size)
                    for a in current_acts:
                        if a<4: e.r.topleft = act(a, p, move_mult)
                        else: e.r.size = act(a, d, move_mult)

if unsaved_changes: 
    print("\nUnsaved Changes Detected")
    save(save_file)