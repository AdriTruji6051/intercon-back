import socket
import json

def get_printers(ipv4):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ipv4, 12345))
    client_socket.sendall(b'GET PRINTERS')

    data = client_socket.recv(1024)
    client_socket.close()
    data = json.loads(data.decode('utf-8'))
    return data

def send_ticket_to_printer(ticket_struct, printer = {}, open_drawer = False):
    ticketsPrint = []
    for i in range(0, len(ticket_struct), 50):
        ticketsPrint.append(ticket_struct[i:i + 50])
    
    for ticket in ticketsPrint:
        print_info = {
            'printerName': printer['name'],
            'text': ticket,
            'openDrawer': open_drawer 
        }

        send_ticket(print_info, printer['ipv4'])

def send_ticket(print_info,printer):
    print_info = json.dumps(print_info)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((printer, 12345))
    client_socket.sendall(print_info.encode('utf-8'))

    data = client_socket.recv(1024)
    print(f"Respuesta del servidor: {data.decode()}")

    client_socket.close()

def open_drawer(printer = {}):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((printer['ipv4'], 12345))
    print_info = {
        'printerName': printer['name'],
        'text': 'OPEN DRAWER',
    }

    print_info = json.dumps(print_info)
    client_socket.sendall(print_info.encode('utf-8'))

    data = client_socket.recv(1024)
    print(f"Respuesta del servidor: {data.decode()}")
    client_socket.close()

    return data.decode('utf-8')

def create_ticket_struct(products, total, subtotal, notes, date, productCount, wholesale):
    ticketLen = 29
    ticketLines = []
    try:
        #Ticket header
        header = [
            'Tel: 373 734 9861'.center(ticketLen, ' '), 
            'Cel: 33 1076 7498'.center(ticketLen, ' '), 
            'Independencia #106. Col Centro'.center(ticketLen, ' '),
            'Servicio a domicilio!...'.center(ticketLen, ' '),
            f'{date}'.center(ticketLen, ' ')
            ]
        
        if (notes):
            header.append('#-#Notas:#-#')
            for i in range(0, len(notes), ticketLen):
                header.append(f'{notes[i:i + ticketLen]}')
        
        header.append('-------------------------------')

        for line in header:
            ticketLines.append([['Lucida Console', 30, 1200 ], line.upper()])

        #Ticket products
        for prod in products:
            description = prod['description']
            cantity = round(prod['cantity'],3)
            rowImport = round(prod['import'],1)

            productRow = str(cantity) + ' ' + str(description)
            if(len(productRow) > 19): productRow = productRow[:19]

            ticketLines.append([['Lucida Console', 38, 1500], "{:19}{:>4}".format(productRow, rowImport).upper()])
        
        change = total - subtotal

        #Ticket footer
        footer = [
            '--------------------------------------------------------------------',
            f'Total: $ {subtotal}',
            f'Cambio: $ {change}' if change else ' ',
            f'Productos: {productCount}',
            f'Descuento: $ {wholesale}' if wholesale else ''
            'Gracias por su compra!...'.center(ticketLen, ' ') 
        ]

        for line in footer:
            ticketLines.append([['Arial', 45, 1300], line.upper()])

        return ticketLines
    except Exception as e:
        print(e)