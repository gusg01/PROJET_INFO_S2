# ihm.py

import matplotlib.pyplot as plt

def tracer_historique(historique):
    plt.figure(figsize=(10, 6))
    for piece, temperatures in historique.items():
        plt.plot(temperatures, label=piece)

    plt.xlabel('Temps (minutes)')
    plt.ylabel('Température (°C)')
    plt.title('Évolution des températures par pièce')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
