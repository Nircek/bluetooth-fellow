#!/usr/bin/env python3
import PySimpleGUI as sg
import bluetooth
from contextlib import closing
from datetime import datetime

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
    server_sock.close()

    sg.theme('Light Brown 3')
    def receiving_thread(window):
        try:
            while True:
                data = client_sock.recv(990)
                if not data:
                    break
                msg = data.decode().replace("\r\n", "\n")
                msg = f'{datetime.now().isoformat()} {msg}'
                window.write_event_value(('-THREAD-', msg), None)
        except OSError:
            pass


    layout = [
        [sg.Image(), sg.VSeperator(), sg.Column([
            [sg.Multiline(size=(127, 30), disabled=True, autoscroll=True, reroute_stdout=True)],
            [
                sg.Input(size=(127-50-3, 1), key="-input-"),
                sg.Submit(size=(50, 1), bind_return_key=True)
            ]
        ])]
    ]
    sg.theme('Light Purple')
    window = sg.Window(name, layout, finalize=True)

    print(f"Accepted connection from {client_addr}/{client_port}\n")
    window.start_thread(lambda: receiving_thread(window), ('-THREAD-', None))
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == 'Submit':
            msg = window['-input-'].get() + '\n'
            client_sock.send(msg.encode())
            print(f'{datetime.now().isoformat()} {msg}')
            window['-input-'].update('')
        elif event[0] == '-THREAD-':
            if event[1] is None:
                break
            print(event[1])

print("Disconnected.")
