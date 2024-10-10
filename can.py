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