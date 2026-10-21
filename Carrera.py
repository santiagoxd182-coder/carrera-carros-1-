import threading
import random


class Carrera:
    def __init__(self, num_carros, vueltas, velocidad_general, callback_mover, callback_fin):
        self.num_carros = num_carros
        self.vueltas = vueltas
        self.velocidad_general = velocidad_general
        self.callback_mover = callback_mover
        self.callback_fin = callback_fin
        self.resultados = []
        self.lock = threading.Lock()
        self.detener_evento = threading.Event()
        self.en_carrera = False
        self.hilos = []

    def iniciar(self):
        if self.en_carrera:
            return
        self.en_carrera = True
        self.detener_evento.clear()
        self.resultados.clear()
        self.hilos.clear()

        for i in range(self.num_carros):
            hilo = threading.Thread(target=self.mover_carro, args=(i,))
            hilo.start()
            self.hilos.append(hilo)

        monitor = threading.Thread(target=self.esperar_final)
        monitor.start()

    def detener(self):
        self.en_carrera = False
        self.detener_evento.set()

    def mover_carro(self, idx):
        base = random.uniform(60, 180)
        x = 50
        vueltas = 0
        tiempo_transcurrido = 0.0
        FINISH_X = 850
        tick = 0.02

        while not self.detener_evento.is_set() and vueltas < self.vueltas:
            if random.random() < 0.05:
                base *= random.uniform(0.8, 1.2)
            delta = base * tick * self.velocidad_general()
            x += delta
            if x >= FINISH_X:
                vueltas += 1
                if vueltas < self.vueltas:
                    x = 50
                else:
                    with self.lock:
                        self.resultados.append((idx + 1, tiempo_transcurrido))
                    break
            self.callback_mover(idx, x)
            if self.detener_evento.wait(0.01):
                break
            tiempo_transcurrido += 0.01

    def esperar_final(self):
        for h in self.hilos:
            h.join()
        self.en_carrera = False
        self.callback_fin(self.resultados)
