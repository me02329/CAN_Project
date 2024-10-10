
# Retrouver la commande Vcan0 pour ouvrir une portière d'une voiture

## Introduction

L'objectif est d'utiliser un simulateur CAN et des outils comme ICSim, `candump`, et `cansend` pour retrouver la commande spécifique qui ouvre une portière d'une voiture. Voici les étapes détaillées suivies pour accomplir cette tâche.

## Étapes

### 1. Installation d'ICSim

Pour commencer, il est nécessaire d'installer le simulateur ICSim. Ce dernier permet de simuler un bus CAN pour une voiture. 

Vous pouvez installer les dépendances nécessaires, cloner le dépôt GitHub d'ICSim et suivre les instructions pour l'installer :
```bash
sudo apt-get install libsdl2-dev libsdl2-image-dev can-utils  
git clone https://github.com/zombieCraig/ICSim.git
cd ICSim
make
```

### 2. Configuration de l'interface `vcan0`

Avant de lancer le simulateur, il est important de configurer l'interface réseau virtuelle CAN (`vcan0`). Voici comment configurer l'interface :

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

Cela crée une interface virtuelle sur laquelle le simulateur pourra échanger les messages CAN.

### 3. Lancement du tableau de bord et des contrôles

Une fois ICSim installé et `vcan0` configurée, il est possible de lancer le tableau de bord et les contrôles du véhicule avec ces commandes :

```bash
./icsim vcan0  # Lancer le tableau de bord
./controls vcan0  # Lancer les contrôles du véhicule
```

Le tableau de bord permet de visualiser l'état des portes, des phares, etc., tandis que les contrôles permettent de simuler des actions comme ouvrir et fermer les portes.

### 4. Lancer `cangen` pour générer du trafic

Pour générer des messages aléatoires sur le bus CAN, utilisez l'outil `cangen`. Cette étape est importante pour obtenir un volume important de messages CAN, parmi lesquels se trouvera la commande qui ouvre la portière.

```bash
cangen vcan0 
```

Ici, l'option `-g 10` génère des messages à un intervalle de 10 ms.

### 5. Capturer le trafic CAN avec `candump`

Ensuite, il est temps de capturer le trafic généré sur le bus CAN en utilisant `candump`. Cette commande va enregistrer tout le trafic dans un fichier log :

```bash
candump -l vcan0
```

Attendez que la portière de la voiture s'ouvre, puis stoppez la capture avec `Ctrl+C`. Ce fichier de log contient tous les messages CAN échangés sur le bus.

![Capture d'écran 2024-09-30 200146](https://github.com/user-attachments/assets/ec9a87b0-f0e6-405a-bc05-4959e3f5954f)
![Capture d'écran 2024-09-30 200156](https://github.com/user-attachments/assets/4d693d15-b30c-4ab3-a51c-430a979f9790)
![Capture d'écran 2024-09-30 200348](https://github.com/user-attachments/assets/4146be59-f0c1-4e5e-b746-8f7f392608fe)


### 6. Création d'un fichier de logs propre avec `awk`

Avant de tester les commandes du fichier de log, il est utile de créer un fichier de logs propre, où seules les données CAN pertinentes sont conservées. Pour cela, j'ai utilisé la commande `awk` pour extraire les colonnes nécessaires (les colonnes 2 et 3) du fichier de capture généré par `candump` :

```bash
awk '{print $2, $3}' candump-2024-09-30_200034.log > /home/martial/Documents/can.log
```
![Capture d'écran 2024-09-30 200816](https://github.com/user-attachments/assets/e93e2291-4309-4794-a6e8-8c00734d6d49)
![Capture d'écran 2024-10-10 195550](https://github.com/user-attachments/assets/dc89567e-3bed-43c5-9451-9d46815290b1)

Cela permet de simplifier le fichier de logs et de n'avoir que les informations cruciales pour la suite du traitement, en enlevant les informations superflues comme les horodatages.

### 7. Test des commandes avec un script Python

Une fois le fichier de logs propre obtenu, j'ai utilisé un script Python pour envoyer les commandes CAN au simulateur et observer quand la portière s'ouvre. Le script envoie les commandes par lots de 10 avec une pause d'une seconde entre chaque lot.

Voici le script Python utilisé :

![Capture d'écran 2024-10-10 201126](https://github.com/user-attachments/assets/270ec438-fd6f-488c-a83f-72295cd0ed28)


```python
import subprocess
import time

# Lecture des commandes depuis le fichier can.log
with open('/home/martial/Documents/can.log', 'r') as f:
    commands = [line.strip() for line in f.readlines()]

def send_commands():
    # Parcours des commandes par lots de 10
    for i in range(0, len(commands), 10):
        batch = commands[i:i+10]
        
        for command in batch:
            # Séparation de la commande en arguments pour subprocess
            cmd_list = command.split()
            print(f"Executing command: {cmd_list}")
            try:
                # Exécution de la commande avec subprocess
                subprocess.run(cmd_list, check=True)
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while executing the command: {e}")
            except FileNotFoundError as e:
                print(f"FileNotFoundError: {e}")

        # Pause de 1 seconde entre chaque batch
        time.sleep(1)

if __name__ == "__main__":
    send_commands()
```

Le script utilise `subprocess.run()` pour exécuter chaque commande du fichier de logs. Le traitement est fait par lots de 10 commandes, avec une pause d'une seconde entre chaque lot pour observer à quel moment la portière s'ouvre. Si une erreur survient, elle est capturée et affichée dans la console.

Lorsque la portière s'ouvre, j'ai interrompu l'exécution avec `Ctrl+C` pour identifier précisément quelle commande a causé l'ouverture.

![Capture d'écran 2024-10-01 142536](https://github.com/user-attachments/assets/a71bcc6b-6c92-447b-adbd-28be81345793)

Maintenant que nous savons que la commande qui ordonne a la portière de s'ouvrir se trouve parmis les 10 dernières commandes executées par le script. Nous avons juste à exécuter un cansend avec les commandes une par une jusqu'à tomber sur la commande qui nous intéresse.

![Capture d'écran 2024-10-01 150928](https://github.com/user-attachments/assets/b34a6414-c408-4f79-a299-bd7fdc355d4f)


### Conclusion

En suivant ces étapes, il est possible de retrouver la commande spécifique qui ouvre la portière d'une voiture en utilisant le simulateur CAN et des outils comme ICSim, `candump`, et `cansend`.
