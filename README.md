README en français :


# Retrouver la commande Vcan0 pour ouvrir une portière d'une voiture

## Introduction

L'objectif est d'utiliser un simulateur CAN et des outils comme ICSim, **`candump`**, et **`cansend`** pour retrouver la commande spécifique qui ouvre une portière d'une voiture. Voici les étapes détaillées suivies pour accomplir cette tâche.

## Étapes

### 1. Installation d'ICSim

Pour commencer, il est nécessaire d'installer le simulateur **ICSim**. Ce dernier permet de simuler un bus CAN pour une voiture. 

Vous pouvez installer les dépendances nécessaires, cloner le dépôt GitHub d'ICSim et suivre les instructions pour l'installer :

```bash
sudo apt-get install libsdl2-dev libsdl2-image-dev can-utils  
git clone https://github.com/zombieCraig/ICSim.git
cd ICSim/buildir/
```

### 2. Configuration de l'interface `vcan0`

Avant de lancer le simulateur, il est important de configurer l'interface **réseau virtuelle CAN (`vcan0`)**. Voici comment configurer l'interface :

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

Pour générer des messages aléatoires sur le bus CAN, utilisez l'outil **`cangen`**. Cette étape est importante pour obtenir un volume important de messages CAN, parmi lesquels se trouvera la commande qui ouvre la portière.

```bash
cangen vcan0 
```

### 5. Capturer le trafic CAN avec `candump`

Ensuite, il est temps de capturer le trafic généré sur le bus CAN en utilisant **`candump`**. Cette commande va enregistrer tout le trafic dans un fichier log :

```bash
candump -l vcan0
```

Attendez que la portière de la voiture s'ouvre, puis stoppez la capture avec `Ctrl+C`. Ce fichier de log contient tous les messages CAN échangés sur le bus.

![Capture d'écran 2024-09-30 200146](https://github.com/user-attachments/assets/ec9a87b0-f0e6-405a-bc05-4959e3f5954f)
![Capture d'écran 2024-09-30 200156](https://github.com/user-attachments/assets/4d693d15-b30c-4ab3-a51c-430a979f9790)
![Capture d'écran 2024-09-30 200348](https://github.com/user-attachments/assets/4146be59-f0c1-4e5e-b746-8f7f392608fe)


### 6. Création d'un fichier de logs propre avec `awk`

Avant de tester les commandes du fichier de log, il est utile de créer un fichier de logs propre, où seules les données CAN pertinentes sont conservées. Pour cela, nous pouvons utiliser la commande `awk` pour extraire les colonnes nécessaires (les colonnes 2 et 3) du fichier de capture généré par `candump` :

```bash
awk '{print $2, $3}' candump-2024-09-30_200034.log > /home/martial/Documents/can.log
```
![Capture d'écran 2024-09-30 200816](https://github.com/user-attachments/assets/e93e2291-4309-4794-a6e8-8c00734d6d49)
![Capture d'écran 2024-10-10 195550](https://github.com/user-attachments/assets/dc89567e-3bed-43c5-9451-9d46815290b1)

Cela permet de simplifier le fichier de logs et de n'avoir que les informations cruciales pour la suite du traitement, en enlevant les informations superflues comme les horodatages.

### 7. Test des commandes avec un script Python

Une fois le fichier de logs propre obtenu, nous pouvons utiliser un script Python pour envoyer les commandes CAN au simulateur et observer quand la portière s'ouvre. Le script envoie les commandes par lots de 10 avec une pause d'une seconde entre chaque lot.

Voici le script Python utilisé :

![image](https://github.com/user-attachments/assets/b2a2f0ca-0af5-4f22-8e26-0f9fa2cd51b3)

Ici, nous mettons en commentaire la fonction **Sleep()** afin d'exécuter toute les commandes à la suite. L'idée est d'estimer grossièrement où se situe la commande qui ouvre la portière de la voiture afin de réduire le nombre de lignes de logs dans le fichiers can.log. Nous n'avons donc pas besoin d'attendre entre les commandes.

### 8. Réduction du fichier log

À ce stade, le fichier de logs peut contenir un grand nombre de messages (environ 17 000). L'objectif est de réduire ce nombre à moins de 1 000 logs, tout en conservant les messages pertinents.

Commencez par utiliser **wc -l** pour compter le nombre de lignes dans le fichier :

```bash
wc -l candump.log
```
Ensuite, utilisez **head** pour ne garder que les premières lignes, en fonction de l'instant où la portière s'est ouverte (pour réduire progressivement le fichier) :

```bash
head -n 1000 can.log > can2.log
```

L'idée est d'éxcuter le script python et de nettoyer le fichier de log autant que possible. Nous pouvons donc répeter l'action autant de fois que nous le voulons (ici 2 fois).

### 8. Envoie des commandes 10 par 10

Une fois que nous avons un fichier de log qui contient un nombre de log résonnable et la commande ouvrant la portière, nous pouvons réexécuter le script python en ajoutant cette fois la fonction Sleep().

![image](https://github.com/user-attachments/assets/76537d59-bda5-49d6-8818-c478386c7e34)

Le script utilise **`subprocess.run()`** pour exécuter chaque commande du fichier de logs. Cette fois-ci, le traitement est fait par lots de 10 commandes, avec une pause d'une seconde entre chaque lot pour observer à quel moment la portière s'ouvre. Si une erreur survient, elle est capturée et affichée dans la console.

Lorsque la portière s'ouvre, nous pouvons interrompre l'exécution avec `Ctrl+C` pour identifier précisément quelle commande a causé l'ouverture.

![Capture d'écran 2024-10-01 142536](https://github.com/user-attachments/assets/a71bcc6b-6c92-447b-adbd-28be81345793)

Maintenant que nous savons que la commande qui ordonne a la portière de s'ouvrir se trouve parmis les 10 dernières commandes executées par le script. Nous avons juste à exécuter un cansend avec les commandes une par une jusqu'à tomber sur la commande qui nous intéresse.

![Capture d'écran 2024-10-01 150928](https://github.com/user-attachments/assets/b34a6414-c408-4f79-a299-bd7fdc355d4f)


### Conclusion

Ce projet a permis d'explorer le fonctionnement des bus CAN et la manière de capturer et analyser les messages CAN pour retrouver des commandes spécifiques. Grâce à l'utilisation d'outils comme ICSim, candump, et cansend, il a été possible d'isoler la commande ouvrant la portière d'une voiture virtuelle.

En suivant une approche méthodique, du nettoyage des logs avec awk à l'utilisation d'un script Python pour automatiser les tests, nous avons pu efficacement réduire le nombre de messages à traiter et identifier la commande cible. Ce type d'analyse est essentiel dans le domaine de l'ingénierie des systèmes embarqués, notamment dans le contexte automobile.

Ce processus met en lumière l'importance de la rigueur dans l'analyse des données CAN et ouvre la voie à des applications plus complexes, comme la rétro-ingénierie des systèmes embarqués ou encore la sécurisation des communications sur les bus CAN. Le savoir-faire acquis ici peut aussi être étendu à d'autres systèmes de transport ou d'automatisation industrielle utilisant des protocoles similaires.

---

README in english :


# Finding the Vcan0 Command to Open a Car Door

## Introduction

The goal is to use a CAN simulator and tools like ICSim, candump, and cansend to find the specific command that opens a car door. Here are the detailed steps followed to accomplish this task.

## Steps

### 1. Installing ICSim

To start, it is necessary to install the ICSim simulator. This tool allows you to simulate a CAN bus for a car.

You can install the required dependencies, clone the ICSim GitHub repository, and follow the instructions to install it :

```bash
sudo apt-get install libsdl2-dev libsdl2-image-dev can-utils  
git clone https://github.com/zombieCraig/ICSim.git
cd ICSim/buildir/
```

### 2. Configuring the vcan0 Interface

Before launching the simulator, it's important to set up the virtual CAN network interface (vcan0). Here's how to configure the interface :

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

This creates a virtual interface where the simulator can exchange CAN messages.

### 3. Launching the Dashboard and Controls

Once ICSim is installed and vcan0 is configured, you can launch the vehicle's dashboard and controls with these commands :

```bash
./icsim vcan0  # Lancer le tableau de bord
./controls vcan0  # Lancer les contrôles du véhicule
```

The dashboard allows you to visualize the status of the doors, lights, etc., while the controls simulate actions such as opening and closing the doors.

### 4. Running cangen to Generate Traffic

To generate random messages on the CAN bus, use the cangen tool. This step is important to create a significant volume of CAN messages, among which the door-opening command will be found.

```bash
cangen vcan0 
```

### 5. Capturing CAN Traffic with candump

Next, it's time to capture the traffic generated on the CAN bus using candump. This command logs all the traffic into a file :

```bash
candump -l vcan0
```

Wait until the car door opens, then stop the capture with Ctrl+C. This log file contains all the CAN messages exchanged on the bus.

![Capture d'écran 2024-09-30 200146](https://github.com/user-attachments/assets/ec9a87b0-f0e6-405a-bc05-4959e3f5954f)
![Capture d'écran 2024-09-30 200156](https://github.com/user-attachments/assets/4d693d15-b30c-4ab3-a51c-430a979f9790)
![Capture d'écran 2024-09-30 200348](https://github.com/user-attachments/assets/4146be59-f0c1-4e5e-b746-8f7f392608fe)


### 6. Creating a Clean Log File with awk

Before testing the commands from the log file, it's useful to create a clean log file, keeping only the relevant CAN data. To do this, I used the awk command to extract the necessary columns (columns 2 and 3) from the capture file generated by candump :

```bash
awk '{print $2, $3}' candump-2024-09-30_200034.log > /home/martial/Documents/can.log
```
![Capture d'écran 2024-09-30 200816](https://github.com/user-attachments/assets/e93e2291-4309-4794-a6e8-8c00734d6d49)
![Capture d'écran 2024-10-10 195550](https://github.com/user-attachments/assets/dc89567e-3bed-43c5-9451-9d46815290b1)

This simplifies the log file by keeping only the essential information for the next steps, removing unnecessary details like timestamps.

### 7. Testing Commands with a Python Script

Once the clean log file is ready, I used a Python script to send CAN commands to the simulator and observe when the door opens. The script sends commands in batches of 10 with a one-second pause between each batch.

Here’s the Python script used :

![image](https://github.com/user-attachments/assets/b2a2f0ca-0af5-4f22-8e26-0f9fa2cd51b3)

In this case, the Sleep() function is commented out so that all commands are executed in sequence. The idea is to roughly estimate where the door-opening command is located in the log file to reduce the number of lines in can.log. There's no need to wait between commands.

### 8. Reducing the Log File

At this stage, the log file may contain a large number of messages (around 17,000). The goal is to reduce this to fewer than 1,000 logs while keeping the relevant messages.

Start by using **wc -l** to count the number of lines in the file :

```bash
wc -l candump.log
```

Next, use **head** to keep only the first lines, based on when the door opened (to gradually reduce the file) :

```bash
head -n 1000 can.log > can2.log
```

The idea is to run the python script and clean the log file as much as possible. So we can repeat the action as many times as we want (here 2 times).

### 9. Sending Commands in Batches of 10

Once we have a log file with a reasonable number of entries and the door-opening command, we can re-run the Python script, this time adding the Sleep() function.

![image](https://github.com/user-attachments/assets/76537d59-bda5-49d6-8818-c478386c7e34)

The script uses subprocess.run() to execute each command from the log file. This time, the process is done in batches of 10 commands, with a one-second pause between each batch to observe when the door opens. If an error occurs, it’s captured and displayed in the console.

When the door opens, we can interrupt execution with Ctrl+C to precisely identify which command caused it.

![Capture d'écran 2024-10-01 142536](https://github.com/user-attachments/assets/a71bcc6b-6c92-447b-adbd-28be81345793)

Now that we know the command to open the door is among the last 10 commands executed by the script, we just need to use cansend to send the commands one by one until we find the one we need.

![Capture d'écran 2024-10-01 150928](https://github.com/user-attachments/assets/b34a6414-c408-4f79-a299-bd7fdc355d4f)


### Conclusion

This project allowed us to explore how CAN buses work and how to capture and analyze CAN messages to find specific commands. By using tools like ICSim, candump, and cansend, we were able to isolate the command that opens the door of a virtual car.

By following a methodical approach—from cleaning the logs with awk to using a Python script to automate tests—we effectively reduced the number of messages to process and identified the target command. This type of analysis is essential in the field of embedded systems engineering, particularly in the automotive context.

This process highlights the importance of rigor in CAN data analysis and opens the door to more complex applications, such as reverse engineering embedded systems or securing communications on CAN buses. The skills gained here can also be extended to other transport systems or industrial automation using similar protocols.
