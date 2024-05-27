import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):


    def __init__(self, UNOS_LAYER, SKRIVEN_LAYER, IZLAZ_LAYER):
        super().__init__()
        self.linear1 = nn.Linear(UNOS_LAYER, SKRIVEN_LAYER)
        self.linear2 = nn.Linear(SKRIVEN_LAYER, IZLAZ_LAYER)


    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x


    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)


        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class Qtrener:


    def __init__(self, model, Stopa_Ucenja, popust):

        self.Stopa_Ucenja = Stopa_Ucenja
        self.popust = popust
        self.model = model
        self.optimizacija = optim.Adam(model.parameters(), lr = self.Stopa_Ucenja)
        self.Srednja_Kvadratna_Greska = nn.MSELoss()


    def Treniraj(self, stanje, akcija, nagrada, Stanje_Sledece, GGWP):
        
        stanje = torch.tensor(stanje, dtype=torch.float)
        Stanje_Sledece = torch.tensor(Stanje_Sledece, dtype=torch.float)
        akcija = torch.tensor(akcija, dtype=torch.long)
        nagrada = torch.tensor(nagrada, dtype=torch.float)


        if len(stanje.shape) == 1:

            stanje = torch.unsqueeze(stanje, 0)
            Stanje_Sledece = torch.unsqueeze(Stanje_Sledece, 0)
            akcija = torch.unsqueeze(akcija, 0)
            nagrada = torch.unsqueeze(nagrada, 0)
            GGWP = (GGWP, )

        Mreza_izlaz = self.model(stanje)
        Ciljna_Vrednost = Mreza_izlaz.clone()

        NewQ = nagrada[0]
        if not GGWP[0]:
            NewQ = nagrada[0] + self.popust * torch.max(self.model(Stanje_Sledece[0]))

        Ciljna_Vrednost[0][torch.argmax(akcija[0]).item()] = NewQ
    
        self.optimizacija.zero_grad()

        Funkcija_Gubitka = self.Srednja_Kvadratna_Greska(Ciljna_Vrednost, Mreza_izlaz)
        Funkcija_Gubitka.backward()

        self.optimizacija.step()



