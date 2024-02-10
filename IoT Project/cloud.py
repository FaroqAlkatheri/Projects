import socket
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

# Global lists to store the sensor values
photo_values = []
poten_values = []

def handle_client(client_socket):
    """Handle client messages in a loop."""
    global photo_values, poten_values
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            json_rcv = json.loads(message.decode('utf-8'))
            photo = float(json_rcv['photo'])
            poten = float(json_rcv['poten'])
            print(f"photosensor value {photo}")
            print(f"potentiometer value {poten}")

            # Update global lists
            photo_values.append(photo)
            poten_values.append(poten)

            if photo < 500:
                state = 'on'
            else:
                state = 'off'
            data = {'state': state}
            reply = json.dumps(data)
            client_socket.sendall(reply.encode('utf-8'))
    except ConnectionResetError:
        print("Client disconnected unexpectedly.")
    finally:
        client_socket.close()

def start_server(host='192.168.100.52', port=4400):
    """Start the TCP server in a new thread."""
    def server_thread():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Server listening on {host}:{port}")
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=handle_client, args=(client_socket,)).start()

    threading.Thread(target=server_thread, daemon=True).start()

def animate(i):
    """Update function for the animation."""
    if photo_values:  # Check if there's new data
        ax1.clear()
        ax2.clear()
        ax1.plot(photo_values, label='Photosensor')
        ax2.plot(poten_values, label='Potentiometer')
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper left")

if __name__ == "__main__":
    # Start the server
    start_server()

    # Set up the plots
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ani = FuncAnimation(fig, animate, interval=1000)  # Update every second

    plt.show()
