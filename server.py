#!/usr/bin/env python3
import bluetooth
from contextlib import closing

'''

```console
sudo hciconfig hci0 piscan
sudo setcap cap_net_raw+eip $(eval readlink -f `which python3`)
sudo chmod o+rw /var/run/sdp
```

'''

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid, name = "00001101-0000-1000-8000-00805f9b34fb", "SerialServer"
options = {
    "service_id": uuid,
    "service_classes": [uuid, bluetooth.SERIAL_PORT_CLASS],
    "profiles": [bluetooth.SERIAL_PORT_PROFILE]
}

bluetooth.advertise_service(server_sock, name, **options)

print(f"Waiting for connection on RFCOMM channel {port}")

client_sock, (client_addr, client_port) = server_sock.accept()
with closing(client_sock) as client_sock:
    print(f"Accepted connection from {client_addr}/{client_port}")
    server_sock.close()
    try:
        while True:
            data = client_sock.recv(990)
            if not data:
                break
            print(data)
    except OSError:
        pass

print("Disconnected.")