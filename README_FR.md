
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
cd ICSim
make
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
