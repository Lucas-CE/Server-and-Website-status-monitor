from archives.pinger import ping_multiplie_tries, request_website
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Callable
import concurrent.futures
import winsound
import json
import time

class Worker(QThread):
    """
    Clase que representa un hilo en el cual se ejecutará la tarea de monitoreo de servidores o sitios web.

    Args:
        json_path (str): Ruta del archivo JSON que contiene la información de los servidores o sitios web a 
        monitorear.
        identifier_tag (str): Ruta del archivo JSON que contiene la información de los servidores o sitios web 
        a monitorear.
        updater (str): Ruta del archivo JSON que contiene la información de los servidores o sitios web a monitorear.
        parent (None, optional): Objeto padre del hilo.
    Attributes:
        update_signal (pyqtSignal): Señal que se emitirá cuando se actualice el estado de un servidor o sitio web.
        stopped (bool): Booleano que indica si se ha detenido la ejecución del hilo.
    """
    update_signal = pyqtSignal(int, str)

    def __init__(self, json_path: str, identifier_tag: str, updater: Callable[[QThread], None], parent=None) -> None:
        """
        Constructor de la clase Worker.

        Args:
            json_path (str): Ruta del archivo JSON que contiene la información de los servidores o sitios web a 
            monitorear.
            identifier_tag (str): Ruta del archivo JSON que contiene la información de los servidores o sitios web 
            a monitorear.
            updater (str): Ruta del archivo JSON que contiene la información de los servidores o sitios web a 
            monitorear.
            parent (None, optional): Objeto padre del hilo.
        """
        super().__init__(parent)
        self.json_path = json_path
        self.identifier_tag = identifier_tag
        self.updater = updater
        self.stopped = False

    def run(self):
        """
        Función que se ejecuta en el hilo. Llama a la función updater para actualizar el estado de los servidores 
        o sitios web.
        """
        self.updater(self)

    def change_state(self, index: int, new_state: str) -> None:
        """
        Función que actualiza el estado de un servidor o sitio web y emite la señal update_signal.

        Args:
            index (int): Índice del servidor o sitio web en la tabla.
            new_state (str): Nuevo estado del servidor o sitio web.
        """
        self.update_signal.emit(index, new_state)

    def stop_works(self) -> None:
        """
        Función que detiene la ejecución del hilo, y maneja el cierre de e
        """
        self.stopped = True
        self.wait()
        self.update_signal.disconnect()
        self.disconnect()


def update_server_states(worker: Worker):
    """
    Función que actualiza los estados de los servidores.

    Args:
        worker (Worker): Objeto de la clase Worker que define el hilo que ejecuta la función.
    """
    update_states(worker, ping_multiplie_tries)


def update_website_states(worker: Worker):
    """
    Función que actualiza los estados de los sitios web.

    Args:
        worker (Worker): Objeto de la clase Worker que define el hilo que ejecuta la función.
    """
    update_states(worker, request_website)


def update_states(worker: Worker, reviewer_fun: Callable[[str], bool]):
    """
    Función que actualiza los estados de los servidores o sitios web de acuerdo a la función
    reviewer_fun entregada.

    Args:
        worker (Worker): Objeto de la clase Worker que define el hilo que ejecuta la función.
        reviewer_fun (function): Función que recibe la dirección IP o URL del servidor/sitio web y retorna un 
        booleano y un mensaje con el estado actual del mismo.
    """
    with open(worker.json_path, "r") as json_file:
        review_list = json.load(json_file)

    # Crear un objeto ThreadPoolExecutor con 2 hilos (uno para cada función)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(review_list)) as executor:
        # Ejecutar las dos funciones en paralelo con sus respectivos parámetros
        for review_index_list in range(len(review_list)):
            executor.submit(
                update_state, 
                *(reviewer_fun, review_list[review_index_list][worker.identifier_tag], review_index_list, worker)
                )
            
        # Esperar a que todas las tareas se completen y luego cerrar el pool de hilos
        executor.shutdown(wait=True)


def update_state(reviewer_fun: Callable[[str], bool], identifier: str, index: int, worker: Worker) -> None:
    """
    Función que actualiza el estado de un servidor o sitio web.

    Args:
        reviewer_fun (Callable[[str], bool]): Función que recibe la dirección IP o URL del servidor/sitio web y 
        retorna un booleano y un mensaje con el estado actual del mismo.
        identifier (str): Identificador único del servidor o sitio web a actualizar.
        index (int): Índice del servidor o sitio web en la tabla.
        worker (Worker): Objeto de la clase Worker que define el hilo que ejecuta la función.
    """
    actual_response = None 
    while not worker.stopped:
        time.sleep(2)
        successful = reviewer_fun(identifier)
        if actual_response != successful:
            actual_response = successful
            if successful:
                worker.change_state(index, "ONLINE")
            else:
                worker.change_state(index, "OFFLINE")
                winsound.Beep(300, 600)
                winsound.Beep(300, 600)
                winsound.Beep(300, 600)