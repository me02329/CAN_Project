# Mini Project: CAN Bus Hacking on a Car

## Introduction

In this project, the goal was to manipulate the **CAN** (Controller Area Network) bus of a **real car** in order to trigger specific actions, such as unlocking a door, by sending the correct messages over the network. Unlike a simulation environment, we accessed the CAN bus directly via a **cable connected to one of the car’s headlights**.

## Project Steps

### 1. Accessing the CAN Bus

We gained access to the CAN bus by connecting a **cable** directly to the **front headlight** circuit of the car. This connection allowed us to communicate with the bus and both send and receive CAN messages. Once the connection was established, we configured the virtual network interface **vcan0**.

### 2. Launching Control Interfaces

Next, we launched a customized **dashboard** and a **control tool** to monitor the messages flowing through the CAN bus. These tools allowed us to observe, in real-time, the data being exchanged across the vehicle’s network, particularly the signals from different vehicle systems.

### 3. Generating Random CAN Messages

To start exploring different CAN frames, we used the **`cangen`** command. This tool generates random CAN messages and sends them over the bus, simulating communications between the vehicle's various modules.

### 4. Capturing CAN Messages

The next step was to capture the messages exchanged on the CAN bus using **`candump`**. We ran the following command:

```bash
candump -l > capture.log
