import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.SysFont('Helvetica', 20)

plava = (0, 150, 255)
crvena = (238,75,43)
zelena = (206,252,186)
crna = (0,0,0)
bela = (255, 255, 255)

Tacka = namedtuple('Tacka', 'x, y')
brzina = 80
METRIKA = 20


class StranaSveta(Enum):
    gore = 1
    dole = 2
    desno = 3
    levo = 4



class ZmijicaAI:
    
    def __init__(self, sirina = 640, visina = 480):
        self.sirina = sirina
        self.visina = visina
        self.display = pygame.display.set_mode((self.sirina, self.visina))
        pygame.display.set_caption('Zmijica')

        self.sat = pygame.time.Clock()
        self.iteracija()


    def iteracija(self):


        self.frame = 0
        self.smer = StranaSveta.desno

        self.glava = Tacka(self.sirina / 2, self.visina / 2)
        self.zmija = [self.glava, Tacka(self.glava.x-METRIKA, self.glava.y), Tacka(self.glava.x - (2 * METRIKA), self.glava.y)]
        
        self.jabuka = None
        self.Broj_poena = 0
        self.StaviJabuku()


    def kretnja(self, akcija):
        svet = [StranaSveta.desno, StranaSveta.dole, StranaSveta.levo, StranaSveta.gore]
        gde = svet.index(self.smer)

        if np.array_equal([1, 0, 0], akcija):
            NoviSmer = svet[gde]
        elif np.array_equal([0, 1, 0], akcija):
            gde2 = (gde + 1) % 4
            NoviSmer = svet[gde2]
        else:
            gde2 = (gde - 1) % 4
            NoviSmer = svet[gde2]
        self.smer = NoviSmer

        x = self.glava.x
        y = self.glava.y

        if self.smer == StranaSveta.gore:
            y -= METRIKA
        elif self.smer == StranaSveta.dole:
            y += METRIKA
        elif self.smer == StranaSveta.levo:
            x -= METRIKA
        elif self.smer == StranaSveta.desno:
            x += METRIKA
            
        self.glava = Tacka(x, y)   



    def StaviJabuku(self):

        x = random.randint(0, (self.sirina-METRIKA) // METRIKA) * METRIKA 
        y = random.randint(0, (self.visina-METRIKA) // METRIKA) * METRIKA
        self.jabuka = Tacka(x, y)
        if self.jabuka in self.zmija:
            self.StaviJabuku()



    def Sudar(self, T = None):
        if T == None:
            T = self.glava

        if T.x < 0 or T.y < 0 or T.x > self.sirina - METRIKA or T.y > self.visina - METRIKA:
            return True

        if T in self.zmija[1:]:
            return True
        return False



    def UI_update(self):

        self.display.fill(zelena)
        
        for i in self.zmija:
            pygame.draw.rect(self.display, plava, pygame.Rect(i.x, i.y, METRIKA, METRIKA))
            
        pygame.draw.rect(self.display, crvena, pygame.Rect(self.jabuka.x, self.jabuka.y, METRIKA, METRIKA))
        text = font.render("Broj poena: " + str(self.Broj_poena), True, crna)
        self.display.blit(text, [0, 0])
        pygame.display.flip()



    def korak(self, akcija):

        self.frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.smer !=StranaSveta.dole:
                    self.smer = StranaSveta.gore
                elif event.key == pygame.K_DOWN and self.smer !=StranaSveta.gore:
                    self.smer = StranaSveta.dole
                elif event.key == pygame.K_LEFT and self.smer !=StranaSveta.desno:
                    self.smer = StranaSveta.levo
                elif event.key == pygame.K_RIGHT and self.smer !=StranaSveta.levo:
                    self.smer = StranaSveta.desno
        
        self.kretnja(akcija)
        self.zmija.insert(0, self.glava)
        
        nagrada = 0
        
        YOU_DIED = False
        if self.Sudar() or self.frame > len(self.zmija) * 150:
            nagrada = -10
            YOU_DIED = True
            return nagrada, YOU_DIED, self.Broj_poena
            
        if self.glava == self.jabuka:
            nagrada = 10
            self.Broj_poena += 1
            self.StaviJabuku()
        else:
            self.zmija.pop()
        
        self.UI_update()
        self.sat.tick(brzina)
        return nagrada, YOU_DIED, self.Broj_poena   


