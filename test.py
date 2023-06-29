import pygame

ss = (800, 1000)
s = pygame.display.set_mode(ss)

i = pygame.transform.scale(pygame.image.load("blueberry_muffin.gif"), ss)
s.blit(i, (0,0))
pygame.display.update(i.get_rect())

exit_loop = False
while not exit_loop:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            exit_loop = True