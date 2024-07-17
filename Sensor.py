import tkinter as tk
import pandas as pd
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import threading

import matplotlib.pyplot as plt

# Crear la ventana principal
window = tk.Tk()
window.geometry("900x700")
window.title('Sensor')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
KEY = 'key.json'
# Escribe aquí el ID de tu documento:
SPREADSHEET_ID = '1CJj1lkOOMc9jA93byH2AiZ0u9hAKLdwkWkdPnpkoZiA'

creds = None
creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

def obtener_datos_api(rango):
	result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=rango).execute()
	values = result.get('values', [])
	values = [int(value[0]) for value in values]
	return values

#Funciones
def update_data():
	global values_C, values_T, values_S, values_AT, d1, d2, d3
	values_C = obtener_datos_api('Hoja 1!A2:A')
	values_T = obtener_datos_api('Hoja 1!B2:B')
	values_S = obtener_datos_api('Hoja 1!C2:C')
	values_AT = obtener_datos_api('Hoja 1!D2:D')
	d1 = obtener_datos_api('Hoja 1!E2:E')
	d2 = obtener_datos_api('Hoja 1!F2:F')
	d3 = obtener_datos_api('Hoja 1!G2:G')
	threading.Timer(5, update_data).start()

update_data()

def crear_graficos():
	# Obtener los datos de interés
	consumo = pd.Series(values_C)
	t_sierra = pd.Series(values_T)
	delta_sierra = pd.Series(values_S)
	avance_tabla = pd.Series(values_AT)

	# Crear una figura con subplots
	fig, axs = plt.subplots(2, 2, figsize=(12, 8))

	# Gráfico de consumo
	axs[0, 0].plot(consumo, label="Consumo")
	axs[0, 0].set_xlabel("Tiempo")
	axs[0, 0].set_ylabel("Consumo (W)")
	axs[0, 0].set_title("Gráfico de Consumo")
	axs[0, 0].legend()

	# Gráfico de temperatura de la sierra
	axs[0, 1].plot(t_sierra, label="T° Sierra")
	axs[0, 1].set_xlabel("Tiempo")
	axs[0, 1].set_ylabel("Temperatura (°C)")
	axs[0, 1].set_title("Gráfico de Temperatura de la Sierra")
	axs[0, 1].legend()

	# Gráfico de variación de recorrido de la sierra
	axs[1, 0].plot(delta_sierra, label="Δ Sierra")
	axs[1, 0].set_xlabel("Tiempo")
	axs[1, 0].set_ylabel("Variación de recorrido (m/min)")
	axs[1, 0].set_title("Gráfico de Variación de Recorrido de la Sierra")
	axs[1, 0].legend()

	# Gráfico de avance de la tabla
	axs[1, 1].plot(avance_tabla, label="Avance Tabla")
	axs[1, 1].set_xlabel("Tiempo")
	axs[1, 1].set_ylabel("Avance de la Tabla (mm/s)")
	axs[1, 1].set_title("Gráfico de Avance de la Tabla")
	axs[1, 1].legend()

	# Ajustar el espaciado entre subplots
	plt.tight_layout()

	# Mostrar la figura con todos los gráficos
	plt.show()

def calcular_promedio_excel():
	global update_text_thread
	
	# Detener el threading de update_text
	update_text_thread.cancel()

	# Calcular el promedio de los datos de interés
	promedio_consumo = pd.Series(values_C).mean()
	promedio_t_sierra = pd.Series(values_T).mean()
	promedio_delta_sierra = pd.Series(values_S).mean()
	promedio_avance_tabla = pd.Series(values_AT).mean()

	# Actualizar los textos de los labels
	CajaTexto1.config(state="normal")
	CajaTexto1.delete("0", tk.END)
	CajaTexto1.insert(tk.END, f"{promedio_consumo} W")
	CajaTexto1.config(state="disabled")

	CajaTexto2.config(state="normal")
	CajaTexto2.delete("0", tk.END)
	CajaTexto2.insert(tk.END, f" {promedio_t_sierra} °C")
	CajaTexto2.config(state="disabled")

	CajaTexto3.config(state="normal")
	CajaTexto3.delete("0", tk.END)
	CajaTexto3.insert(tk.END, f" {promedio_delta_sierra} m/min")
	CajaTexto3.config(state="disabled")

	CajaTexto4.config(state="normal")
	CajaTexto4.delete("0", tk.END)
	CajaTexto4.insert(tk.END, f"{promedio_avance_tabla} mm/s")
	CajaTexto4.config(state="disabled")

def crear_nueva_ventana():
	# Ocultar la ventana actual
	window.withdraw()
	
	# Crear una nueva ventana
	nueva_ventana = tk.Toplevel(window)
	nueva_ventana.geometry("400x300")
	nueva_ventana.title("Nueva Ventana")
	
	# Crear un botón para volver a la ventana anterior
	boton_volver = tk.Button(nueva_ventana, text="Volver", command=lambda: volver_ventana(nueva_ventana))
	boton_volver.place(x=150, y=200, width=100, height=30)
	
	# Ejecutar el bucle principal de la nueva ventana
	nueva_ventana.mainloop()

def volver_ventana(ventana):
	# Mostrar la ventana anterior
	window.deiconify()
	
	# Cerrar la ventana actual
	ventana.destroy()

def update_text():
	global values_C, values_T, values_S, values_AT, d1, d2, d3, update_text_thread

	CajaTexto1.config(state="normal")
	CajaTexto1.delete(0, tk.END)
	for dato in values_C[::-1]:
		CajaTexto1.insert(tk.END, f"{dato} W\n")
	CajaTexto1.config(state="disabled")

	CajaTexto2.config(state="normal")
	CajaTexto2.delete(0, tk.END)
	for dato in values_T[::-1]:
		CajaTexto2.insert(tk.END, f"{dato} °C\n")
	CajaTexto2.config(state="disabled")

	CajaTexto3.config(state="normal")
	CajaTexto3.delete(0, tk.END)
	for dato in values_S[::-1]:
		CajaTexto3.insert(tk.END, f"{dato} m/min\n")
	CajaTexto3.config(state="disabled")

	CajaTexto4.config(state="normal")
	CajaTexto4.delete(0, tk.END)
	for dato in values_AT[::-1]:
		CajaTexto4.insert(tk.END, f"{dato} mm/s\n")
	CajaTexto4.config(state="disabled")

	CajaD1.config(state="normal")
	CajaD1.delete("1.0", tk.END)
	CajaD1.insert(tk.END, f"{d1[-1]} cm")
	CajaD1.config(state="disabled")

	CajaD2.config(state="normal")
	CajaD2.delete("1.0", tk.END)
	CajaD2.insert(tk.END, f"{d2[-1]} cm")
	CajaD2.config(state="disabled")

	CajaD3.config(state="normal")
	CajaD3.delete("1.0", tk.END)
	CajaD3.insert(tk.END, f"{d3[-1]} cm")
	CajaD3.config(state="disabled")

	update_text_thread = threading.Timer(5, update_text)
	update_text_thread.start()

update_text_thread = threading.Timer(5, update_text)
update_text_thread.start()

#Imagen
img = tk.PhotoImage(file="Imagen.png")
label=tk.Label(window,image=img)
label.place(x=50,y=150)

#Textos no editables
Texto = tk.Label(window, text="Proceso Aserrio",font=20)
Texto.place(x=420, y=30, width=150, height=15)

Texto1 = tk.Label(window, text="Consumo")
Texto1.place(x=700, y=50, width=80, height=15)
Texto2 = tk.Label(window, text="T° Sierra")
Texto2.place(x=700, y=180, width=80, height=15)
Texto3 = tk.Label(window, text="Δ Sierra")
Texto3.place(x=700, y=310, width=80, height=15)
Texto4 = tk.Label(window, text="Avance Tabla")
Texto4.place(x=700, y=440, width=80, height=15)

Texto5 = tk.Label(window, text="d1(ANCHO)")
Texto5.place(x=520, y=130, width=70, height=15)
Texto6 = tk.Label(window, text="d2(ALTO)")
Texto6.place(x=520, y=230, width=70, height=15)
Texto7 = tk.Label(window, text="d3(LARGO)",background="white")
Texto7.place(x=410, y=360, width=70, height=15)

#Cajas de texto
CajaTexto1 = tk.Listbox(window, state="disabled")
CajaTexto1.place(x=650, y=70, width=200, height=100)
scrollbar1 = tk.Scrollbar(window)
scrollbar1.place(x=850, y=70, height=100)
CajaTexto1.config(yscrollcommand=scrollbar1.set)
scrollbar1.config(command=CajaTexto1.yview)

CajaTexto2 = tk.Listbox(window, state="disabled")
CajaTexto2.place(x=650, y=200, width=200, height=100)
scrollbar2 = tk.Scrollbar(window)
scrollbar2.place(x=850, y=200, height=100)
CajaTexto2.config(yscrollcommand=scrollbar2.set)
scrollbar2.config(command=CajaTexto2.yview)

CajaTexto3 = tk.Listbox(window, state="disabled")
CajaTexto3.place(x=650, y=330, width=200, height=100)
scrollbar3 = tk.Scrollbar(window)
scrollbar3.place(x=850, y=330, height=100)
CajaTexto3.config(yscrollcommand=scrollbar3.set)
scrollbar3.config(command=CajaTexto3.yview)

CajaTexto4 = tk.Listbox(window, state="disabled")
CajaTexto4.place(x=650, y=460, width=200, height=100)
scrollbar4 = tk.Scrollbar(window)
scrollbar4.place(x=850, y=460, height=100)
CajaTexto4.config(yscrollcommand=scrollbar4.set)
scrollbar4.config(command=CajaTexto4.yview)

#Texto dimension de tablas
CajaD1 = tk.Text(window, state="disabled")
CajaD1.place(x=500, y=150, width=70, height=20)
CajaD2 = tk.Text(window, state="disabled")
CajaD2.place(x=500, y=250, width=70, height=20)
CajaD3 = tk.Text(window, state="disabled")
CajaD3.place(x=410, y=380, width=70, height=20)

# Crear un botón
boton = tk.Button(window, text="Promedio", command=lambda: [calcular_promedio_excel()] )
boton.place(x=50, y=50, width=100, height=30)

# Crear otro botón
boton_mostrar_lista = tk.Button(window, text="Mostrar Lista", command=lambda: [update_text() ])
boton_mostrar_lista.place(x=160, y=50, width=100, height=30)

# Crear otro botón para llamar a la función crear_graficos
boton_crear_graficos = tk.Button(window, text="Ver Gráficos", command=lambda: crear_graficos())
boton_crear_graficos.place(x=270, y=50, width=100, height=30)

# Crear un botón para llamar a la función crear_nueva_ventana
boton_nueva_ventana = tk.Button(window, text="Mas Datos", command=crear_nueva_ventana)
boton_nueva_ventana.place(x=700, y=580, width=100, height=30)

# Ejecutar el bucle principal de la ventana
window.mainloop()