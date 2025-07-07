import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import unicodedata
import subprocess

cartas = [
    "El Gallo", "El Diablito", "La Dama", "El Catrín", "El Paraguas", "La Sirena",
    "La Escalera", "La Botella", "El Barril", "El Árbol", "El Melón", "El Valiente",
    "El Gorrito", "La Muerte", "La Pera", "La Bandera", "El Bandolón", "El Violoncello",
    "La Garza", "El Pájaro", "La Mano", "La Bota", "La Luna", "El Cotorro",
    "El Borracho", "El Negrito", "El Corazón", "La Sandía", "El Tambor", "El Camarón",
    "Las Jaras", "El Músico", "La Araña", "El Soldado", "La Estrella", "El Cazo",
    "El Mundo", "El Apache", "El Nopal", "El Alacrán", "La Rosa", "La Calavera",
    "La Campana", "El Cantarito", "El Venado", "El Sol", "La Corona", "La Chalupa",
    "El Pino", "El Pescado", "La Palma", "La Maceta", "El Arpa", "La Rana"
]


def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto


def obtener_ruta_imagen(nombre_carta):
    carpeta = "barajas"
    nombre_carta_norm = normalizar(nombre_carta)
    for archivo in os.listdir(carpeta):
        nombre_archivo, ext = os.path.splitext(archivo)
        if ext.lower() == ".jpg":
            nombre_archivo_norm = normalizar(nombre_archivo)
            if nombre_archivo_norm.endswith(nombre_carta_norm):
                return os.path.join(carpeta, archivo)
    return None


voz_actual = None
submenu_voz = None


def reproducir_audio(nombre_carta):
    if voz_actual.get() == "Katy":
        carpeta_audio = "barajas-audio"
    else:
        carpeta_audio = "barajas-audio-2"
    nombre_archivo = normalizar(nombre_carta) + ".mp3"
    ruta_audio = os.path.join(carpeta_audio, nombre_archivo)
    if os.path.exists(ruta_audio):
        try:
            if os.name == "nt":
                subprocess.Popen(
                    ['mpg123', '-q', ruta_audio],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                subprocess.Popen(['mpg123', '-q', ruta_audio])
        except Exception as e:
            print(f"No se pudo reproducir el audio: {e}")
    else:
        print(f"Audio no encontrado: {ruta_audio}")


velocidad_ms = 1500


def animar_miniaturas(labels):
    def flash(lbl, count):
        if count > 0:
            lbl.config(bg="#ffe066" if count % 2 == 0 else "#ffffff")
            lbl.after(60, flash, lbl, count - 1)
        else:
            lbl.config(bg="#ffffff")
    for lbl in labels:
        flash(lbl, 4)


def set_velocidad(segundos):
    global velocidad_ms
    velocidad_ms = int(float(segundos) * 1000)


def cantar_carta():
    global indice, after_id, imagen_actual, pausado, contador_registro, miniaturas_imgs
    if indice < len(cartas):
        texto = f"Carta: {cartas[indice]}"
        etiqueta.config(text=texto)
        # print(texto)
        ruta_imagen = obtener_ruta_imagen(cartas[indice])
        if ruta_imagen and os.path.exists(ruta_imagen):
            img = Image.open(ruta_imagen)
            img = img.resize((300, 450), Image.LANCZOS)
            imagen_actual = ImageTk.PhotoImage(img)
            etiqueta_imagen.config(image=imagen_actual, text="")

            mini_img = Image.open(ruta_imagen).resize((60, 90), Image.LANCZOS)
            mini_img_tk = ImageTk.PhotoImage(mini_img)
            miniaturas_imgs.insert(0, mini_img_tk)

            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            labels = []
            for idx, img_tk in enumerate(miniaturas_imgs):
                row = idx // 6
                col = idx % 6
                lbl = tk.Label(scrollable_frame, image=img_tk, bg="#ffffff")
                lbl.grid(row=row, column=col, padx=2, pady=2)
                if idx < 6:
                    labels.append(lbl)
            animar_miniaturas(labels)
        else:
            etiqueta_imagen.config(image='', text="Imagen no encontrada")
        reproducir_audio(cartas[indice])
        indice += 1
        after_id = root.after(velocidad_ms, cantar_carta)
    else:
        etiqueta.config(text="¡Fin del juego!")
        etiqueta_imagen.config(image='', text='')
        boton_iniciar.config(state=tk.NORMAL)
        boton_stop.config(state=tk.DISABLED)
        boton_pausar.config(state=tk.DISABLED)
        boton_reanudar.config(state=tk.DISABLED)
        pausado = False
        submenu_voz.entryconfig(0, state="normal")
        submenu_voz.entryconfig(1, state="normal")


def iniciar():
    global indice, after_id, pausado, contador_registro, miniaturas_imgs
    random.shuffle(cartas)
    indice = 0
    pausado = False
    contador_registro = 1
    boton_iniciar.config(state=tk.DISABLED)
    boton_stop.config(state=tk.NORMAL)
    boton_pausar.config(state=tk.NORMAL)
    boton_reanudar.config(state=tk.DISABLED)
    submenu_voz.entryconfig(0, state="disabled")
    submenu_voz.entryconfig(1, state="disabled")
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    miniaturas_imgs.clear()
    cantar_carta()


def detener():
    global after_id, pausado
    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None
    etiqueta.config(text="Juego detenido")
    etiqueta_imagen.config(image='', text='')
    boton_iniciar.config(state=tk.NORMAL)
    boton_stop.config(state=tk.DISABLED)
    boton_pausar.config(state=tk.DISABLED)
    boton_reanudar.config(state=tk.DISABLED)
    pausado = False
    submenu_voz.entryconfig(0, state="normal")
    submenu_voz.entryconfig(1, state="normal")


def pausar():
    global after_id, pausado
    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None
        pausado = True
        etiqueta.config(text="Juego en pausa")
        boton_pausar.config(state=tk.DISABLED)
        boton_reanudar.config(state=tk.NORMAL)
        boton_iniciar.config(state=tk.DISABLED)
        boton_stop.config(state=tk.NORMAL)
        submenu_voz.entryconfig(0, state="normal")
        submenu_voz.entryconfig(1, state="normal")


def reanudar():
    global pausado
    if pausado:
        pausado = False
        etiqueta.config(text="Reanudando...")
        boton_pausar.config(state=tk.NORMAL)
        boton_reanudar.config(state=tk.DISABLED)
        boton_iniciar.config(state=tk.DISABLED)
        boton_stop.config(state=tk.NORMAL)
        submenu_voz.entryconfig(0, state="disabled")
        submenu_voz.entryconfig(1, state="disabled")
        root.after(500, cantar_carta)


def mostrar_acerca_de():
    ventana = tk.Toplevel(root)
    ventana.title("Acerca de")
    ventana.resizable(False, False)
    ventana.configure(bg="#ffffff")
    ventana.geometry("350x120")
    ventana.attributes('-topmost', True)
    label = tk.Label(
        ventana,
        text="Creado por el\nI.S.C. Freddy Ruben Franco Lugo\n\n© Todos los derechos reservados.",
        font=("Arial", 12),
        justify="center",
        bg="#ffffff"
    )
    label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    ventana.grab_set()


root = tk.Tk()
root.title("Lotería Mexicana de la Dirección de Fomento Económico y Turismo")
root.resizable(False, False)
root.configure(bg="#ffffff")

# Color para la franja de menú (gris muy claro)
COLOR_MENU = "#f5f5f5"

voz_actual = tk.StringVar(value="Katy")  # coloque la voz de Katy por defecto

menu_principal = tk.Menu(root, bg=COLOR_MENU, fg="#000000",
                         activebackground="#e0e0e0", activeforeground="#000000")
root.config(menu=menu_principal)
submenu_velocidad = tk.Menu(menu_principal, tearoff=0, bg=COLOR_MENU,
                            fg="#000000", activebackground="#e0e0e0", activeforeground="#000000")
menu_principal.add_cascade(label="Velocidad", menu=submenu_velocidad)
velocidades = [x * 0.5 for x in range(2, 11)]

velocidad_var = tk.DoubleVar(value=velocidad_ms / 1000)

for segundos in velocidades:
    submenu_velocidad.add_radiobutton(
        label=f"{segundos:.1f} segundos",
        value=segundos,
        variable=velocidad_var,
        command=lambda s=segundos: set_velocidad(s)
    )

submenu_voz = tk.Menu(menu_principal, tearoff=0, bg=COLOR_MENU,
                      fg="#000000", activebackground="#e0e0e0", activeforeground="#000000")
menu_principal.add_cascade(label="Voz", menu=submenu_voz)
submenu_voz.add_radiobutton(
    label="Katy", value="Katy", variable=voz_actual)
submenu_voz.add_radiobutton(
    label="Sistema", value="Sistema", variable=voz_actual)

# Menú Ayuda
submenu_ayuda = tk.Menu(menu_principal, tearoff=0, bg=COLOR_MENU,
                        fg="#000000", activebackground="#e0e0e0", activeforeground="#000000")
menu_principal.add_cascade(label="Ayuda", menu=submenu_ayuda)
submenu_ayuda.add_command(label="Acerca de", command=mostrar_acerca_de)

icono_path = os.path.join("assets", "icono.png")
if os.path.exists(icono_path):
    try:
        icono_img = Image.open(icono_path)
        icono_photo = ImageTk.PhotoImage(icono_img)
        root.iconphoto(True, icono_photo)
    except Exception as e:
        print(f"No se pudo cargar el icono: {e}")

main_frame = tk.Frame(root, bg="#ffffff")
main_frame.pack(fill=tk.BOTH, expand=True)

miniaturas_frame = tk.Frame(main_frame, bg="#ffffff")
miniaturas_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

canvas = tk.Canvas(miniaturas_frame, width=400, height=600,
                   bg="#ffffff", highlightthickness=0)
scrollbar = tk.Scrollbar(
    miniaturas_frame, orient="vertical", command=canvas.yview, bg=COLOR_MENU, troughcolor=COLOR_MENU, activebackground="#e0e0e0", highlightbackground=COLOR_MENU
)
scrollable_frame = tk.Frame(canvas, bg="#ffffff")


def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all(
    "<MouseWheel>", _on_mousewheel))
scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all"),
        width=400
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="y", expand=True)
scrollbar.pack(side="right", fill="y")

miniaturas_imgs = []

frame_derecho = tk.Frame(main_frame, bg="#ffffff")
frame_derecho.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

etiqueta = tk.Label(
    frame_derecho, text="Presiona 'Iniciar' para comenzar", font=("Arial", 24), bg="#ffffff")
etiqueta.pack(pady=20)

etiqueta_imagen = tk.Label(frame_derecho, bg="#ffffff")
etiqueta_imagen.pack(pady=10)

frame_botones = tk.Frame(frame_derecho, bg="#ffffff")
frame_botones.pack(pady=20)

boton_iniciar = tk.Button(
    frame_botones,
    text="Iniciar",
    font=("Arial", 18),
    command=iniciar,
    bg="#4CAF50",
    fg="white",
    activebackground="#388E3C",
    activeforeground="white"
)
boton_iniciar.pack(side=tk.LEFT, padx=10)

boton_pausar = tk.Button(
    frame_botones,
    text="Pausar",
    font=("Arial", 18),
    command=pausar,
    state=tk.DISABLED,
    bg="#FFC107",
    fg="black",
    activebackground="#FFA000",
    activeforeground="black"
)
boton_pausar.pack(side=tk.LEFT, padx=10)

boton_reanudar = tk.Button(
    frame_botones,
    text="Reanudar",
    font=("Arial", 18),
    command=reanudar,
    state=tk.DISABLED,
    bg="#2196F3",
    fg="white",
    activebackground="#1565C0",
    activeforeground="white"
)
boton_reanudar.pack(side=tk.LEFT, padx=10)

boton_stop = tk.Button(
    frame_botones,
    text="Stop",
    font=("Arial", 18),
    command=detener,
    state=tk.DISABLED,
    bg="#F44336",
    fg="white",
    activebackground="#B71C1C",
    activeforeground="white"
)
boton_stop.pack(side=tk.LEFT, padx=10)

leyenda = tk.Label(
    frame_derecho,
    text="Exclusivo de la Direccion de Fomento Económico y Turismo de Macuspana, Tabasco, \n ya que estos huevones no tienen nada que hacer. \n Periodo 2024-2027",
    font=("Arial", 10, "italic"),
    anchor="e",
    justify="center",
    bg="#ffffff"
)
leyenda.pack(side=tk.BOTTOM, anchor="e", padx=10, pady=10, fill=tk.X)

indice = 0
after_id = None
imagen_actual = None
pausado = False
contador_registro = 1

root.mainloop()
