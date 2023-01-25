import pygame
from pygame.locals import *
import sys
import random
import time

#TODO:
# Przetłumaczyć zmienne na Polski
# Dodać komentarze do tego, co robią dane funkcje
# Neutralne assety dodać xd

pygame.init()
pygame.mixer.init()
wek = pygame.math.Vector2 #Dwuwymiarowy wektor

WYSOKNA = 900
SZEROKNA = 800
PRZYSP = 0.5
TARCIE = -0.12
FPS = 60

FramesPerSec = pygame.time.Clock()
okno = pygame.display.set_mode((WYSOKNA, SZEROKNA))
pygame.display.set_caption("PyClimber")

tloObraz = pygame.image.load("background.png")
tlo = pygame.transform.scale(tloObraz, (WYSOKNA, SZEROKNA))

class Gracz(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pole = pygame.image.load("papa.png")
        self.granica = self.pole.get_rect()

        self.pozycja = wek((WYSOKNA - 40 ,SZEROKNA/2))
        self.predkosc = wek(0,0)
        self.przyspieszenie = wek(0,0)
        self.skacze = False
        self.wynik = 0

    def ruch(self):
        self.przyspieszenie = wek(0,0.5)

        nacisniety_klawisz = pygame.key.get_pressed()

        if nacisniety_klawisz[K_LEFT]:
            self.przyspieszenie = -PRZYSP
        if nacisniety_klawisz[K_RIGHT]:
            self.przyspieszenie = PRZYSP

        self.przyspieszenie.x += self.predkosc.x * TARCIE
        self.predkosc += self.przyspieszenie
        self.pozycja += self.predkosc + 0.5 * self.przyspieszenie

        if self.pozycja.x > SZEROKNA:
            self.pozycja.x = 0
        if self.pozycja.x < 0:
            self.pozycja.x = SZEROKNA

        self.granica.midbottom = self.pozycja

    def skok(self):
        kolizja = pygame.sprite.spritecollide(self, platformy, False)
        if kolizja and not self.skacze:
            self.skacze = True
            self.predkosc.y = -15

    def anuluj_skok(self):
        if self.skacze:
            if self.predkosc.y < -3:
                self.predkosc.y = -3

    def aktualizacja(self):
        kolizja = pygame.sprite.spritecollide(self, platformy, False)
        if self.predkosc.y > 0:
            if kolizja:
                if self.pozycja.y < kolizja[0].rect.bottom:
                    if kolizja[0].point == True:
                        kolizja[0].point = False
                        self.wynik += 1
                    self.pozycja.y = kolizja.rect.top + 1
                    self.predkosc.y = 0
                    self.skacze = False

class Moneta(pygame.sprite.Sprite):
    def __init__(self, pozycja):
        super().__init__()

        self.obraz = pygame.image.load("moneta.png")
        self.granica = self.image.get_rect()
        self.granica.topleft = pozycja

    def aktualizacja(self):
        if self.granica.colliderect(G1.granica):
            G1.wynik += 5
            pygame.mixer.Sound.play(dzwiekMoneta)
            self.kill()

class platforma(pygame.sprite.Sprite):
    def __init__(self, szerokosc = 0, wysokosc = 18):
        super.__init__()

        if szerokosc == 0:
            szerokosc = random.randint(100, 200)

        self.obraz = pygame.image.load("platform.png")
        self.pole = pygame.transform.scale(self.obraz, (szerokosc, wysokosc))
        self.granica = self.pole.get_rect(center = (random.randint(0, SZEROKNA - 10),
                                                    random.randint(0, WYSOKNA - 30)))
        self.punkt = True
        self.poruszaSie = True
        self.predkosc = random.randint (-1,1)

        if (self.predkosc == 0):
            self.poruszaSie = False

    def ruch(self):
        kolizja = self.rect.colliderect(G1.granica)
        if self.poruszaSie == True:
            self.granica.move_ip(self.predkosc, 0)
            if kolizja:
                G1.pozycja += (self.predkosc, 0)
                if self.predkosc > 0 and self.granica.left > SZEROKNA:
                    self.granica.right = 0
                if self.predkosc < 0 and self.granica.right < 0:
                    self.granica.left = SZEROKNA

    def generujMonety(self):
        if (self.predkosc == 0):
            monety.add(Moneta((self.granica.centerx, self.granica.centery - 50)))

def sprawdz(platforma,grupy):
    if pygame.sprite.spritecollideany(platforma, grupy):
        return True
    else:
        for obiekt in grupy:
            if obiekt == platforma:
                continue
            if (abs(platforma.granica.top - obiekt.granica.bottom)<40 and (
                abs(platforma.granica.bottom - obiekt.granica.top) <40)):
                return True
        C = False

def generacja_platform():
    while len(platformy) < 12:
        szerokosc = random.randrange(100,200)
        p = None
        C = True

        while C:
            p = platforma()
            p.granica.center (random.randrange(0, SZEROKNA - szerokosc),
                              random.randrange(-50, 0))
            C = sprawdz(p, platformy)

            p.generujMonety()
            platformy.add(p)
            wszystkie_sprity.add(p)

wszystkie_sprity = pygame.sprite.Group()
platformy = pygame.sprite.Group()
monety = pygame.sprite.Group()

PT1 = platforma(SZEROKNA, 80)
PT1.granica = PT1.pole.get_rect(center = (SZEROKNA/2, WYSOKNA - 10))
PT1.poruszaSie = False
PT1.punkt = False

G1 = Gracz()

wszystkie_sprity.add(PT1)
wszystkie_sprity.add(G1)
platformy.add(PT1)

muzykaTlo = pygame.mixer.music.load("bgm.mp3")
pygame.mixer.music.play(-1)

dzwiekMoneta = pygame.mixer.Sound("moneta.mp3")

for x in range(random.randint(10,11)):
    C = True
    pl = platforma()
    while C:
        pl = platforma()
        C = sprawdz(pl,platformy)
    pl.generujMonety()
    platformy.add(pl)
    wszystkie_sprity.add(pl)

while True:
    G1.aktualizacja()
    for wydarzenie in pygame.event.get():
        if wydarzenie.type == pygame.KEYDOWN:
            if wydarzenie.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if wydarzenie.type == QUIT:
                pygame.quit()
                sys.exit()
            if wydarzenie.type == pygame.KEYDOWN:
                if wydarzenie.key == pygame.K_SPACE:
                    G1.skok()
            if wydarzenie.type == pygame.KEYUP:
                if wydarzenie.key == pygame.K_SPACE:
                    G1.anuluj_skok()

            if G1.granica.top > WYSOKNA:
               for obiekt in wszystkie_sprity:
                   obiekt.kill()
                   okno.fill((255,0,0))
                   t = pygame.font.SysFont("Comic Sans", 20)
                   dead = t.render("Nie zyjesz!", True, (0,0,255))
                   okno.blit(dead, (SZEROKNA/2, WYSOKNA/2))
                   pygame.display.update()
                   time.sleep(1)
                   pygame.quit()
                   sys.exit()

    if G1.granica.top <= WYSOKNA/3:
        G1.pozycja.y += abs(G1.predkosc.y)
        for plat in platformy:
            plat.granica.y += abs(G1.predkosc.y)
            if plat.granica.top >= WYSOKNA:
                plat.kill()

        for monetki in monety:
            monetki.granica.y += abs(G1.predkosc.y)
            if monetki.granica.top >= WYSOKNA:
                monetki.kill()

    generacja_platform()
    okno.blit(tlo, (0,0))
    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(G1.score), True, (123, 255, 0))
    okno.blit(g, (SZEROKNA/2, 10))

    for obiekt in wszystkie_sprity:
        okno.blit(obiekt.pole, obiekt.granica)
        obiekt.ruch()

    for monetki in monety:
        okno.blit(monetki.obraz, monetki.granica )
        monetki.aktualizacja()

    pygame.display.update()
    FramePerSec.tick(FPS)