import matplotlib.pyplot as plt
from IPython import display


plt.ion()

def plot(Broj_Poena, Srednji_Broj_Poena):

    display.clear_output(wait = True)
    display.display(plt.gcf())

    plt.clf()
    plt.xlabel('Epizoda')
    plt.ylabel('Broj poena')
    plt.title('Treniranje u toku')

    plt.plot(Broj_Poena)
    plt.plot(Srednji_Broj_Poena)

    plt.ylim(ymin = 0)
    plt.text(len(Broj_Poena) - 1, Broj_Poena[-1], str(Broj_Poena[-1]))
    plt.text(len(Srednji_Broj_Poena) - 1, Srednji_Broj_Poena[-1], str(Srednji_Broj_Poena[-1]))
    plt.show(block = False)
    plt.pause(.1)
