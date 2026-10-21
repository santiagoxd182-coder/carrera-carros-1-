import tkinter as tk
from tkinter import ttk, messagebox
from Carrera import Carrera
import os
import random
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

NUM_CARS = 10
CAR_HEIGHT = 25
CAR_GAP = 25
START_X = 50
FINISH_X = 850

class CarreraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Carreritas (Modular con main)")
        self.root.resizable(False, False)

        self.car_images = []
        self.items_carros = []
        self.resultados = []
        self.car_positions = [START_X]*NUM_CARS
        self.cargar_imagenes()
        self.crear_ui()

        # La clase Carrera se creará cuando se inicie la carrera
        self.carrera = None

    # ---------- Interfaz ----------
    def crear_ui(self):
        frame = ttk.Frame(self.root, padding=8)
        frame.grid(row=0, column=0)

        controles = ttk.Frame(frame)
        controles.grid(row=0, column=0, columnspan=2, pady=(0,8), sticky="w")

        ttk.Label(controles, text="Apuesta (1-10):").grid(row=0, column=0)
        self.apuesta = tk.IntVar(value=1)
        ttk.Spinbox(controles, from_=1, to=NUM_CARS, textvariable=self.apuesta, width=5).grid(row=0, column=1, padx=5)

        ttk.Label(controles, text="Vueltas:").grid(row=0, column=2)
        self.vueltas = tk.IntVar(value=1)
        ttk.Spinbox(controles, from_=1, to=50, textvariable=self.vueltas, width=5).grid(row=0, column=3, padx=5)

        ttk.Label(controles, text="Velocidad:").grid(row=0, column=4)
        self.velocidad_var = tk.DoubleVar(value=1.0)
        ttk.Scale(controles, from_=0.2, to=3.0, variable=self.velocidad_var, orient="horizontal", length=150).grid(row=0, column=5, padx=5)

        self.btn_iniciar = ttk.Button(controles, text="Iniciar", command=self.iniciar)
        self.btn_iniciar.grid(row=0, column=6, padx=5)
        self.btn_detener = ttk.Button(controles, text="Detener", command=self.detener, state="disabled")
        self.btn_detener.grid(row=0, column=7, padx=5)

        alto = NUM_CARS*(CAR_HEIGHT + CAR_GAP) + 40
        self.canvas = tk.Canvas(frame, width=FINISH_X+100, height=alto, bg="snow")
        self.canvas.grid(row=1, column=0)
        self.dibujar_pista()

        resultados_frame = ttk.Frame(frame)
        resultados_frame.grid(row=1, column=1, padx=(12, 0), sticky="n")
        ttk.Label(resultados_frame, text="Resultados").grid(row=0, column=0, pady=(8, 4), sticky="w")
        self.tabla = ttk.Treeview(resultados_frame, columns=("veh","tiempo"), show="headings", height=10)
        self.tabla.heading("veh", text="Vehículo")
        self.tabla.heading("tiempo", text="Tiempo (s)")
        self.tabla.column("veh", width=100, anchor="center")
        self.tabla.column("tiempo", width=100, anchor="center")
        self.tabla.grid(row=1, column=0, sticky="n")

    def dibujar_pista(self):
        for i in range(NUM_CARS):
            y = 20 + i*(CAR_HEIGHT + CAR_GAP)
            self.canvas.create_line(START_X-10, y+CAR_HEIGHT//2, FINISH_X+50, y+CAR_HEIGHT//2, dash=(3,6))
            if self.car_images[i] is not None:
                item = self.canvas.create_image(START_X, y, anchor="nw", image=self.car_images[i])
            else:
                rect = self.canvas.create_rectangle(START_X, y, START_X+60, y+CAR_HEIGHT, fill=self.color_aleatorio(i))
                txt = self.canvas.create_text(START_X+30, y+CAR_HEIGHT//2, text=str(i+1), fill="white")
                item = (rect, txt)
            self.items_carros.append((item, y))
        self.canvas.create_line(FINISH_X, 0, FINISH_X, self.canvas.winfo_reqheight(), width=4, fill="red")

    def cargar_imagenes(self):
        carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehiculos")
        for i in range(1, NUM_CARS+1):
            ruta = os.path.join(carpeta, f"{i}.png")
            if PIL_AVAILABLE and os.path.exists(ruta):
                im = Image.open(ruta).resize((60, 60))
                self.car_images.append(ImageTk.PhotoImage(im))
            else:
                self.car_images.append(None)

    def color_aleatorio(self, seed):
        random.seed(seed + 1234)
        return f'#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}'

    # ---------- Eventos ----------
    def iniciar(self):
        self.btn_iniciar.config(state="disabled")
        self.btn_detener.config(state="normal")

        # crear carrera
        self.carrera = Carrera(
            num_carros=NUM_CARS,
            vueltas=self.vueltas.get(),
            velocidad_general=lambda: self.velocidad_var.get(),
            callback_mover=lambda i, x: self.root.after(0, self.mover_carro, i, x),
            callback_fin=lambda res: self.root.after(0, self.mostrar_resultados, res)
        )
        self.carrera.iniciar()

    def detener(self):
        if self.carrera:
            self.carrera.detener()
        self.btn_iniciar.config(state="normal")
        self.btn_detener.config(state="disabled")

    # ---------- UI Updates ----------
    def mover_carro(self, idx, x):
        item, y = self.items_carros[idx]
        if isinstance(item, tuple):
            self.canvas.coords(item[0], x, y, x+60, y+CAR_HEIGHT)
            self.canvas.coords(item[1], x+30, y+CAR_HEIGHT/2)
        else:
            self.canvas.coords(item, x, y)

    def mostrar_resultados(self, resultados):
        for i in self.tabla.get_children():
            self.tabla.delete(i)
        resultados.sort(key=lambda r: r[1])
        for pos, (carro, tiempo) in enumerate(resultados, start=1):
            self.tabla.insert("", "end", values=(f"{carro} (#{pos})", f"{tiempo:.3f}"))
        if resultados:
            ganador = resultados[0][0]
            if ganador == self.apuesta.get():
                messagebox.showinfo("¡Ganaste!", f"Tu apuesta ({ganador}) fue correcta 🎉")
            else:
                messagebox.showinfo("Resultado", f"Ganó el vehículo {ganador}. Tu apuesta no acertó.")
        self.btn_iniciar.config(state="normal")
        self.btn_detener.config(state="disabled")
