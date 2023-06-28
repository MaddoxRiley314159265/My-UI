from my_ui import *
import ui_config
import pygame

save_file = "ui_saves.json"

new_thingies = list(classes.keys())
for nt in new_thingies:
    if "transition" in nt.lower():
        new_thingies.remove(nt)

pygame.init()

#'''
load_name = input("Load save? (Don't type to start new save): ")
if not load_name=="": load(save_file, "Demo")
else:
    dd = (int(input("Screen width: ")), int(input("Screen height: ")))
    init_menus(dd)
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
    finish = False
    if ui_config.menus[ui_config.current_menu_index].r.collidepoint(pos):
        #Click is inside menu
        if not edit_element==None and edit_element.r.collidepoint(pos):
            #Click the already clicked element, deselect everything
            edit_element = None
            print("Deselect")
            finish = True
        else:
            for i, e in enumerate(ui_config.menus[ui_config.current_menu_index].menu_elements):
                if e.r.collidepoint(pos):
                    edit_element = e
                    print("Selected", edit_element)
                    finish = True
        if not finish:
            if edit_element==ui_config.menus[ui_config.current_menu_index]: 
                print("Deselect menu")
                edit_element = None
            else:
                edit_element = ui_config.menus[ui_config.current_menu_index]
                print("Selected current menu")

key_acts = {pygame.K_w : 0, pygame.K_a : 1, pygame.K_s : 2, pygame.K_d : 3, pygame.K_UP : 4, pygame.K_LEFT : 5, pygame.K_DOWN : 6, pygame.K_RIGHT : 7}

current_acts = []
fine_tune = False

edit_element = None
while not ui_config.exit_loop:
    if edit_element==None: select_rect = None
    else: select_rect = edit_element.r

    events = main(True,select_rect)
    for event in events:
        if event.type==pygame.QUIT:
            ui_config.exit_loop = True
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_n:
                #Create new thingy
                new_thing = ""
                while not new_thing in new_thingies and not new_thing.lower()=="none":
                    new_thing = input("What would you like to add? (None to cancel): ")
                if not new_thingy.lower()==None:
                    new_thingy(new_thing)
            elif not key_acts.get(event.key)==None:
                current_acts.append(key_acts.get(event.key))
            elif event.key==pygame.K_LSHIFT:
                fine_tune = True

        elif event.type==pygame.KEYUP:
            if not key_acts.get(event.key)==None:
                current_acts.remove(key_acts.get(event.key))
            elif event.key==pygame.K_LSHIFT:
                fine_tune = False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            click(pygame.mouse.get_pos())
        #elif event.type==pygame.MOUSEBUTTONUP:

    if not edit_element==None:
        if fine_tune: move_mult = 1
        else: move_mult = 5
        p = c(edit_element.r.topleft)
        d = c(edit_element.r.size)
        if len(current_acts)>0:
            ui_config.update_display = True
            for a in current_acts:
                if a==0: edit_element.r.topleft = (p+c(0,-1)*move_mult).t()
                if a==1: edit_element.r.topleft = (p+c(-1,0)*move_mult).t()
                if a==2: edit_element.r.topleft = (p+c(0,1)*move_mult).t()
                if a==3: edit_element.r.topleft = (p+c(1,0)*move_mult).t()

                if a==4: edit_element.r.size = (d+c(0,-1)*move_mult).t()
                if a==5: edit_element.r.size = (d+c(-1,0)*move_mult).t()
                if a==6: edit_element.r.size = (d+c(0,1)*move_mult).t()
                if a==7: edit_element.r.size = (d+c(1,0)*move_mult).t()

save(save_file)