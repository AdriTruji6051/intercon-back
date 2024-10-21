import win32print
import win32ui


def print_ticket(lines,printer_name) -> bool:
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        hDC.StartDoc("Ticket")
        hDC.StartPage()

        y = 0
        for line in lines:
            fontConfig = line[0]
            text = line[1]

            fontFamily = fontConfig[0]
            fontSize = fontConfig[1]
            fontWeight = fontConfig[2]

            font = win32ui.CreateFont({
                "name": fontFamily,
                "height": fontSize, 
                "weight": fontWeight,
            })

            hDC.SelectObject(font)
            hDC.TextOut(10, y, text)
            y += fontSize + 10

        hDC.EndPage()
        hDC.EndDoc()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        win32print.ClosePrinter(hPrinter)

if __name__ == '__main__':
    print('Hola')
    lines = [
        # [['Lucida Console', 40, 1300] ,'ESTO ES DEBERIA SER UN PRODUCTO'],
        # [['Arial', 55, 1500 ], 'ESTO DEBERIA SER UN TOTAL'],
        # [['Calibri', 80, 1300 ], '$ ESTO DEBERIA SER UNA ETIQUETA'],
        # [['Calibri', 330, 1200 ], '0000'], #Precios de 4 cifras
        # [['Calibri', 450, 1200 ], '000'], #Precios de 3 cifras
        # [['Calibri', 625, 1200 ], '00'], #Precios de 2 < cifras

        [['Calibri', 245, 1200 ], '0000.0'], #Precios de 4 cifras con punto
        [['Calibri', 300, 1200 ], '000.0'], #Precios de 3 cifras con punto
        [['Calibri', 385, 1200 ], '00.0'], #Precios de 2 cifras con punto
        [['Calibri', 515, 1200 ], '0.0'], #Precios de 1 cifra con punto

    ]

    print_ticket(lines,'80 printer')