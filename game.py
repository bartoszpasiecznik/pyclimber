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
vec = pygame.math.Vector2 #dwuwymiarowy wektor

HEIGHT = 900 #Wysokosc Ekranu
WIDTH = 800 #Szerokosc Ekranu
ACC = 0.5 #Przyspieszenie
FRIC = -0.12 #Wartosc Tarcia
FPS = 60 #Czestotliwosc odswiezania ekranu

muzykaTlo = pygame.mixer.music.load("bgm.mp3") #Wczytanie muzyki odtwarzanej w tle
pygame.mixer.music.play(-1)
monetaDzwiek = pygame.mixer.Sound("moneta.mp3") #Dzwiek zebrania monety

FramePerSec = pygame.time.Clock()
okno = pygame.display.set_mode((WIDTH, HEIGHT)) # Inicjalizacja okna
pygame.display.set_caption("PyClimber")

tloObraz = pygame.image.load("background.png") #Dodanie tła
tlo = pygame.transform.scale(tloObraz, (WIDTH, HEIGHT))

class Gracz(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("papa.png")
        self.rect = self.surf.get_rect()

        #Inicjalizacja zmiennych
        self.pos = vec((HEIGHT - 50, WIDTH/2 )) #Pozycja gracza
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.czySkacze = False
        self.wynik = 0

    def ruch(self):
        self.acc = vec(0, 0.5) #Grawitacja
        nacisniete_klawisze = pygame.key.get_pressed()

        if nacisniete_klawisze[K_LEFT]: #Nadanie przyspieszenia po nacisnieciu klawisza
            self.acc.x = -ACC
        if nacisniete_klawisze[K_RIGHT]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH: #Teleportacja gracza na druga strone
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def skok(self):
        kolizja = pygame.sprite.spritecollide(self, platformy, False)
        if kolizja and not self.czySkacze:
            self.czySkacze = True
            self.vel.y = -15

    def anulujSkok(self):
        if self.czySkacze:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        kolizja = pygame.sprite.spritecollide(self, platformy, False)
        if self.vel.y > 0:
            if kolizja:
                if self.pos.y < kolizja[0].rect.bottom:
                    if kolizja[0].point:
                        kolizja[0].point = False
                        self.wynik += 1
                    self.pos.y = kolizja[0].rect.top + 1
                    self.vel.y = 0
                    self.czySkacze = False

class Moneta(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.imageLoad = pygame.image.load("moneta.png")
        self.image = pygame.transform.scale(self.imageLoad, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self):
        if self.rect.colliderect(G1.rect):
            G1.wynik += 5
            pygame.mixer.Sound.play(monetaDzwiek)
            self.kill()

class Platforma(pygame.sprite.Sprite):
    def __init__(self, width = 0, height = 18):
        super().__init__()

        if width == 0:
            width = random.randint(100, 200)

        self.image = pygame.image.load("platform.png")
        self.surf = pygame.transform.scale(self.image, (width, height))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 30)))

        self.point = True
        self.czyRuch = True
        self.speed = random.randint(-1, 1)


        if self.speed == 0:
            self.czyRuch = False

    def ruch(self):
        kolizja = self.rect.colliderect(G1.rect)
        if self.czyRuch == True:
            self.rect.move_ip(self.speed, 0)

            if kolizja:
                G1.pos += (self.speed, 0)

            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0

            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH

    def generujMonety(self):
        if self.speed == 0:
            monety.add(Moneta((self.rect.centerx, self.rect.centery - 50)))

def check(platform, grupy):   # Funkcja sprawdza, czy w otoczeniu X jednostek znajduje się platforma
    if pygame.sprite.spritecollideany(platform, grupy):
        return True
    else:
        for obiekt in grupy:
            if obiekt == platform:
                continue
        if (abs(platform.rect.top - obiekt.rect.bottom) < 50) and (
                        abs(platform.rect.bottom - obiekt.rect.top) < 50):
            return True
    C = False

def generacjaPlatform():
    while len(platformy) < 15:
        width = random.randrange (50, 100)
        p = None
        C = True

        while C:
            p = Platforma()
            p.rect.center = (random.randrange(0, WIDTH - width),
                             random.randrange(-40, 0))
            C = check(p, platformy)

        p.generujMonety()
        platformy.add(p)
        wszystkie_sprity.add(p)

wszystkie_sprity = pygame.sprite.Group()
platformy = pygame.sprite.Group()
monety = pygame.sprite.Group()

PT1 = Platforma(WIDTH, 80)
PT1.rect = PT1.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))
PT1.czyRuch = False
PT1.point = False

G1 = Gracz()

wszystkie_sprity.add(PT1)
wszystkie_sprity.add(G1)
platformy.add(PT1)

for x in range(random.randint(10,11)):
    C = True
    pl = Platforma()
    while C:
        pl = Platforma()
        C = check(pl, platformy)
        pl.generujMonety()
        platformy.add(pl)
        wszystkie_sprity.add(pl)

while True:
    G1.update()
    for event in pygame.event.get():

        # Skok, wyłączanie

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                G1.skok()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                G1.anulujSkok()

        # Ekran Śmierci

        if G1.rect.top > HEIGHT: #Funkcja wykonuje się, gdy gracz spadnie pod mapę
            for entity in wszystkie_sprity:
                entity.kill()
                time.sleep(1)
                okno.fill((255, 0, 0))
                d = pygame.font.SysFont("Comic Sans", 20)
                dead = d.render("You dead bruv", True, (0, 0, 255))
                okno.blit(dead, (WIDTH / 2, HEIGHT / 2))
                pygame.display.update()
                time.sleep(1)
                pygame.quit()
                sys.exit()

    if G1.rect.top <= HEIGHT/3: #Scrollowanie ekranu
        G1.pos.y += abs(G1.vel.y)
        for plat in platformy:
            plat.rect.y += abs(G1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()

        for moneta in monety:
            moneta.rect.y += abs(G1.vel.y)
            if moneta.rect.top >= HEIGHT:
                moneta.kill()

    generacjaPlatform()
    okno.blit(tlo, (0,0))
    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(G1.wynik), True, (123, 255, 0)) # Wyświetlanie wyniku
    okno.blit(g, (WIDTH / 2, 10))

    for obiekt in wszystkie_sprity:
        okno.blit(obiekt.surf, obiekt.rect)
        obiekt.ruch()

    for moneta in monety:
        okno.blit(moneta.image, moneta.rect)
        moneta.update()

    pygame.display.update()
    FramePerSec.tick(FPS)