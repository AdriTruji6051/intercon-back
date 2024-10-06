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

def send_ticket_to_printer(ticket_struct = '', printer = {}, open_drawer = False):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((printer['ipv4'], 12345))
    print_info = {
        'printerName': printer['name'],
        'text': ticket_struct,
        'openDrawer': open_drawer
    }

    print_info = json.dumps(print_info)
    client_socket.sendall(print_info.encode('utf-8'))

    data = client_socket.recv(1024)
    print(f"Respuesta del servidor: {data.decode()}")
    client_socket.close()

    return data.decode('utf-8')

def create_ticket_struct(products, total, subtotal, notes, date):
    ticketLen = 29
    try:
        ticketTxt = 'Tel: 373 734 9861'.center(ticketLen, ' ') + '#-#'
        ticketTxt += 'Cel: 33 1076 7498'.center(ticketLen, ' ') + '#-#'
        ticketTxt += 'Independencia #106. Col Centro'.center(ticketLen, ' ') + '#-#'
        ticketTxt += 'Servicio a domicilio!...'.center(ticketLen, ' ') + '#-#'
        ticketTxt += f'{date}'.center(ticketLen, ' ') + '#-#'

        if (notes): ticketTxt += '#-#' + f'Notas: {notes}' + '#-#----------------------------------------------->#-##-#' 
        else: ticketTxt += '#-#-----------------------------------------------#-#'

        for prod in products:
            description = prod['description']
            cantity = round(prod['cantity'],3)
            rowImport = round(prod['import'],1)

            productRow = str(cantity) + ' ' + str(description)
            if(len(productRow) > 19): productRow = productRow[:18]
            ticketTxt += "{:24}{:>5}".format(productRow, rowImport) + '#-#'
        
        change = total - subtotal
        ticketTxt += f'-----------------------------------------------#-##-#Total: {subtotal}'
        ticketTxt += f'#-#Cambio:  {change}' if change else ' '
        ticketTxt += '#-##-#'
        ticketTxt += 'Gracias por su compra!...'.center(ticketLen, ' ') + '#-#'
        ticketTxt = ticketTxt.upper()
        return ticketTxt
    except Exception as e:
        print(e)