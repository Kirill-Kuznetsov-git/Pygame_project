import pygame

pygame.init()

sc = pygame.display.set_mode((400, 300))


pygame.mixer.pre_init(frequency=44100, size=-16, channels=8, buffer=4096)
pygame.init()

sound1 = pygame.mixer.Sound('gun.wav')

while 1:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            exit()
        elif i.type == pygame.KEYUP:
            if i.key == pygame.K_1:
                pygame.mixer.music.pause()
                # pygame.mixer.music.stop()
            elif i.key == pygame.K_2:
                pygame.mixer.music.unpause()
                # pygame.mixer.music.play()
                pygame.mixer.music.set_volume(0.5)
            elif i.key == pygame.K_3:
                pygame.mixer.music.unpause()
                # pygame.mixer.music.play()
                pygame.mixer.music.set_volume(1)
    pygame.time.delay(20)
