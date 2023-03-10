import pygame
from pygame.locals import *
import sys
import random
import time


pygame.init()
pygame.mixer.init()
vec = pygame.math.Vector2  # dwuwymiarowy wektor

HEIGHT = 900  # Wysokosc Ekranu
WIDTH = 800  # Szerokosc Ekranu
ACC = 0.5  # Przyspieszenie
FRIC = -0.12  # Wartosc Tarcia
FPS = 60  # Czestotliwosc odswiezania ekranu
PLATFORMNUMBER = 15  # Ilosc platform na ekranie
WYNIK = 0
f = open("best_score.txt", "r")
NAJLEPSZY_WYNIK = int(f.read())
START_TIME = time.time()


FramePerSec = pygame.time.Clock()
okno = pygame.display.set_mode((WIDTH, HEIGHT))  # Inicjalizacja okna
pygame.display.set_caption("PyClimber")

tloObraz = pygame.image.load("background.png")  # Dodanie tła
tlo = pygame.transform.scale(tloObraz, (WIDTH, HEIGHT))


class Gracz(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.jumpanimation = [pygame.image.load("gracz1.png"), pygame.image.load("gracz2.png"),
                              pygame.image.load("gracz3.png"), pygame.image.load("gracz4.png"),
                              pygame.image.load("graczlewo.png"), pygame.image.load("graczprawo.png")]
        self.surf = pygame.image.load("gracz1.png")
        self.rect = self.surf.get_rect()

        # Inicjalizacja zmiennych
        self.pos = vec((WIDTH / 2, HEIGHT - 20))  # Pozycja gracza
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.czySkacze = False
        self.czyRuch = False
        self.wynik = 0
        self.moveframe = 0

    def ruch(self):
        self.acc = vec(0, 0.5)  # Grawitacja
        nacisniete_klawisze = pygame.key.get_pressed()
        if not self.czyRuch and not self.czySkacze and not nacisniete_klawisze[K_LEFT] and not \
                nacisniete_klawisze[K_RIGHT]:
            self.moveframe = 0
        if nacisniete_klawisze[K_LEFT]:  # Nadanie przyspieszenia po nacisnieciu klawisza
            self.moveframe = 4
            self.acc.x = -ACC
        if nacisniete_klawisze[K_RIGHT]:
            self.moveframe = 5
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:  # Teleportacja gracza na druga strone
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def skok(self):  # Skok
        kolizja = pygame.sprite.spritecollide(self, platformy, False)
        self.moveframe = random.randint(1, 3)
        if kolizja and not self.czySkacze:
            self.surf = self.jumpanimation[self.moveframe]
            self.czySkacze = True
            pygame.mixer.Sound.play(skokDzwiek)
            self.vel.y = -15

    def anulujSkok(self):  # Anulowanie skoku przy puszczeniu klawisza
        if self.czySkacze:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        kolizja = pygame.sprite.spritecollide(self, platformy, False)
        self.surf = self.jumpanimation[self.moveframe]
        if self.vel.y > 0:
            if kolizja:
                if self.pos.y < kolizja[0].rect.bottom:
                    if kolizja[0].point:
                        kolizja[0].point = False
                        self.wynik += 1
                        global WYNIK
                        WYNIK += 1
                    self.pos.y = kolizja[0].rect.top + 1
                    self.vel.y = 0
                    self.czySkacze = False


class Moneta(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # wczytanie i odpowiednie wyskalowanie grafiki monety
        self.imageLoad = pygame.image.load("moneta.png")
        self.image = pygame.transform.scale(self.imageLoad, (25, 25))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self):
        if self.rect.colliderect(G1.rect):
            G1.wynik += 5
            global WYNIK
            WYNIK += 5
            pygame.mixer.Sound.play(monetaDzwiek)
            self.kill()


class Platforma(pygame.sprite.Sprite):
    def __init__(self, width=0, height=18):
        super().__init__()

        if width == 0:
            width = random.randint(100, 200)

        self.czyPlatformaPrzeskoczona = False
        self.image = pygame.image.load("platform.png")
        self.surf = pygame.transform.scale(self.image, (width, height))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 30)))

        self.point = True
        self.czyRuch = True
        # Generujemy predkosc poruszania sie platformy, wartosci ujemne to poruszanie sie 'w lewo', wartosci dodanie
        # 'w prawo', zero oznacza brak ruchu
        # Generujemy wartosc z zakresu [-1, 1] i mnozymy przez wynik a nastepnie 0.025
        # w celu stopniowego zwiekszania predkosci poruszania sie platform
        self.speed = random.randint(-1, 1) * (WYNIK + 5) * 0.01
        self.szansaMonety = random.randint(0, 4)  # Szansa na pojawienie się monety
        if self.speed == 0:
            self.czyRuch = False

    def ruch(self):  # Ruch platform
        kolizja = self.rect.colliderect(G1.rect)
        if self.czyRuch == True:
            # Jesli self.speed jest w zakresie [-1, 1] unieruchamiamy
            # platforme nadajac self.speed wartosc 0
            if 1 > self.speed > -1 and self.speed != 0:
                self.speed = 0
            self.rect.move_ip(self.speed, 0)
            if kolizja:
                G1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH

    def generujMonety(self):
        if self.speed == 0 and self.szansaMonety == 0:  # Generacja monety gdy platforma jest statyczna
            monety.add(Moneta((self.rect.centerx, self.rect.centery - 50)))


def check(platform, grupy):  # Funkcja sprawdza, czy w otoczeniu X jednostek znajduje się platforma
    if pygame.sprite.spritecollideany(platform, grupy):
        return True
    else:
        for obiekt in grupy:
            if obiekt == platform:
                continue
            if (abs(platform.rect.top - obiekt.rect.bottom) < 40) and (
                    abs(platform.rect.bottom - obiekt.rect.top) < 40):
                return True
        C = False


def generacjaPlatform():
    while len(platformy) < PLATFORMNUMBER:
        width = random.randrange(50, 100)
        p = None
        C = True

        while C:
            p = Platforma()
            p.rect.center = (random.randrange(0, WIDTH - width),
                             random.randrange(-50, 0))
            C = check(p, platformy)

        p.generujMonety()
        platformy.add(p)
        wszystkie_sprity.add(p)


wszystkie_sprity = pygame.sprite.Group()
platformy = pygame.sprite.Group()
monety = pygame.sprite.Group()

PT1 = Platforma(WIDTH, 80)
PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))
PT1.czyRuch = False
PT1.point = False

G1 = Gracz()

wszystkie_sprity.add(PT1)
wszystkie_sprity.add(G1)
platformy.add(PT1)

# Dzwiek
muzykaTlo = pygame.mixer.music.load("bgm.mp3")  # Wczytanie muzyki odtwarzanej w tle
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

monetaDzwiek = pygame.mixer.Sound("moneta.mp3")  # Dzwiek zebrania monety
skokDzwiek = pygame.mixer.Sound("skok.mp3")

# Wstepna generacja platform
for x in range(random.randint(PLATFORMNUMBER - 2, PLATFORMNUMBER - 1)):
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

        if G1.rect.top > HEIGHT:  # Funkcja wykonuje się, gdy gracz spadnie pod mapę
            for entity in wszystkie_sprity:
                with open('best_score.txt', 'w') as s:
                    s.write(str(NAJLEPSZY_WYNIK))
                entity.kill()
                time.sleep(1)
                okno.fill((255, 0, 0))
                t = pygame.font.SysFont("Arial", 35)
                time_played = t.render("Czas gry: "+ str(int(time.time() - START_TIME))+ "s", True, (0, 0, 0))
                okno.blit(time_played, (WIDTH / 2 - 80, HEIGHT / 2 - 110))
                a = pygame.font.SysFont("Arial", 35)
                score = a.render("Twój wynik: " + str(WYNIK), True, (0, 0, 0))
                okno.blit(score, (WIDTH / 2 - 80, HEIGHT / 2 - 40))
                b = pygame.font.SysFont("Arial", 35)
                best_score = b.render("Najlepszy wynik: " + str(NAJLEPSZY_WYNIK), True, (0, 0, 0))
                okno.blit(best_score, (WIDTH / 2 - 80, HEIGHT / 2 - 80))
                d = pygame.font.SysFont("Arial", 35)
                dead = d.render("Koniec gry", True, (0, 0, 0))
                okno.blit(dead, (WIDTH / 2 - 80, HEIGHT / 2))
                pygame.display.update()
                time.sleep(5)
                pygame.quit()
                sys.exit()

    if G1.rect.top <= HEIGHT / 3:  # Scrollowanie ekranu
        G1.pos.y += abs(G1.vel.y)
        for plat in platformy:
            plat.rect.y += abs(G1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()
                WYNIK += 1

        for moneta in monety:
            moneta.rect.y += abs(G1.vel.y)
            if moneta.rect.top >= HEIGHT:
                moneta.kill()

    if WYNIK > NAJLEPSZY_WYNIK:
        NAJLEPSZY_WYNIK = WYNIK
    generacjaPlatform()
    okno.blit(tlo, (0, 0))
    f1 = pygame.font.SysFont("Verdana", 20)
    f2 = pygame.font.SysFont("Verdana", 20)
    f3 = pygame.font.SysFont("Verdana", 20)
    # Wyswietlanie wyniku
    g1 = f1.render("Wynik: " + str(WYNIK) + "pkt", True, (0, 0, 0))
    # Wyswietlanie najlepszego wyniku
    g2 = f2.render("Najlepszy wynik: " + str(NAJLEPSZY_WYNIK) + "pkt", True, (0, 0, 0))
    # Wyswietlanie czasu gry
    g3 = f3.render("Czas gry: " + str(int(time.time() - START_TIME)) + "s", True, (0, 0, 0))
    okno.blit(g1, (WIDTH / 2 - 70, 10))
    okno.blit(g2, (WIDTH - 300, 10))
    okno.blit(g3, (100, 10))

    for obiekt in wszystkie_sprity:
        okno.blit(obiekt.surf, obiekt.rect)
        okno.blit(obiekt.surf, obiekt.rect)
        obiekt.ruch()

    for moneta in monety:
        okno.blit(moneta.image, moneta.rect)
        moneta.update()

    pygame.display.update()
    FramePerSec.tick(FPS)
