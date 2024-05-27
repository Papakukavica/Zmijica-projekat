import torch
import random
import numpy as np
from collections import deque
from ZmijicaKod import ZmijicaAI, StranaSveta, Tacka
from model import Linear_QNet, Qtrener
from Grafik import plot


class Agent:

    def __init__(self):
        
        self.model = Linear_QNet(11, 256, 3)
        self.trener = Qtrener(self.model, Stopa_Ucenja = 0.001, popust = 0.9)
        self.memorija = deque(maxlen=100000)
        self.ExploreOrExploit = 0
        self.Broj_Epizoda = 0


    def Uzmi_stanje(self, ZmijicaKod):
        glava = ZmijicaKod.zmija[0]
        point_l = Tacka(glava.x - 20, glava.y)
        point_r = Tacka(glava.x + 20, glava.y)
        point_u = Tacka(glava.x, glava.y - 20)
        point_d = Tacka(glava.x, glava.y + 20)
        
        LEVO = ZmijicaKod.smer == StranaSveta.levo
        DESNO = ZmijicaKod.smer == StranaSveta.desno
        GORE = ZmijicaKod.smer == StranaSveta.gore
        DOLE = ZmijicaKod.smer == StranaSveta.dole

        Stanje_Trenutno = [

            (DESNO and ZmijicaKod.Sudar(point_r)) or (LEVO and ZmijicaKod.Sudar(point_l)) or (GORE and ZmijicaKod.Sudar(point_u)) or (DOLE and ZmijicaKod.Sudar(point_d)),

            (GORE and ZmijicaKod.Sudar(point_r)) or (DOLE and ZmijicaKod.Sudar(point_l)) or (LEVO and ZmijicaKod.Sudar(point_u)) or (DESNO and ZmijicaKod.Sudar(point_d)),

            (DOLE and ZmijicaKod.Sudar(point_r)) or (GORE and ZmijicaKod.Sudar(point_l)) or (DESNO and ZmijicaKod.Sudar(point_u)) or (LEVO and ZmijicaKod.Sudar(point_d)),
            
            LEVO, DESNO, GORE, DOLE,
            
            ZmijicaKod.jabuka.x < ZmijicaKod.glava.x, ZmijicaKod.jabuka.x > ZmijicaKod.glava.x, ZmijicaKod.jabuka.y < ZmijicaKod.glava.y,  ZmijicaKod.jabuka.y > ZmijicaKod.glava.y 
            ]

        return np.array(Stanje_Trenutno, dtype = int)

    def Zapamti(self, Stanje_Trenutno, Akcija, nagrada, Stanje_Sledece, GGWP):
        self.memorija.append((Stanje_Trenutno, Akcija, nagrada, Stanje_Sledece, GGWP))


    def Treniraj_DugorocnaMemorija(self):

        if len(self.memorija) > 1000:
            Uzorak = random.sample(self.memorija, 1000)
        else:
            Uzorak = self.memorija

        Stanje_SVE, Akcija_SVE, nagrada_SVE, Stanje_Sledece_SVE, GGWP_SVE = zip(*Uzorak)
        self.trener.Treniraj(Stanje_SVE, Akcija_SVE, nagrada_SVE, Stanje_Sledece_SVE, GGWP_SVE)


    def Treniraj_KratkotrajnaMemorija(self, Stanje_Trenutno, Akcija, nagrada, Stanje_Sledece, GGWP):
        self.trener.Treniraj(Stanje_Trenutno, Akcija, nagrada, Stanje_Sledece, GGWP)

    def Akcija_Izracunaj(self, Stanje_Trenutno):

        self.ExploreOrExploit = 80 - self.Broj_Epizoda

        Kretanje_Konsenzus = [0,0,0]

        if random.randint(0, 200) < self.ExploreOrExploit:
            Kretanje_Konsenzus[random.randint(0, 2)] = 1
        else:
            Tenzor = torch.tensor(Stanje_Trenutno, dtype=torch.float)
            SledeciPotez = self.model(Tenzor)
            Kretanje_Konsenzus[torch.argmax(SledeciPotez).item()] = 1

        return Kretanje_Konsenzus


if __name__ == '__main__':


    Grafik_BrojPoena = []
    Grafik_BrojPoenaProsek = []
    BrojPoena_SUMA = 0
    HighScore = 0
    agent = Agent()
    ZmijicaKod = ZmijicaAI()


    while True:

        Stanje_Staro = agent.Uzmi_stanje(ZmijicaKod)
        Kretanje_Konsenzus = agent.Akcija_Izracunaj(Stanje_Staro)

        nagrada, GGWP, BrojPoena = ZmijicaKod.korak(Kretanje_Konsenzus)
        Stanje_Novo = agent.Uzmi_stanje(ZmijicaKod)

        agent.Treniraj_KratkotrajnaMemorija(Stanje_Staro, Kretanje_Konsenzus, nagrada, Stanje_Novo, GGWP)
        agent.Zapamti(Stanje_Staro, Kretanje_Konsenzus, nagrada, Stanje_Novo, GGWP)

        if GGWP:
            ZmijicaKod.iteracija()
            agent.Broj_Epizoda += 1
            agent.Treniraj_DugorocnaMemorija()

            if BrojPoena > HighScore:
                HighScore = BrojPoena
                agent.model.save()

            print('Epizoda', agent.Broj_Epizoda, 'Broj Poena', BrojPoena, 'HighScore:', HighScore)

            Grafik_BrojPoena.append(BrojPoena)
            BrojPoena_SUMA += BrojPoena
            Prosek = BrojPoena_SUMA / agent.Broj_Epizoda
            Grafik_BrojPoenaProsek.append(Prosek)
            plot(Grafik_BrojPoena, Grafik_BrojPoenaProsek)