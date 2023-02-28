from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView
from archives.controller import update_server_states, update_website_states, Worker
from PyQt5.QtGui import QColor, QFont, QCloseEvent
from typing import Tuple
import qdarkstyle
import json


class MainWindow(QMainWindow):
    def __init__(self):
        """
        Constructor de la clase MainWindow. Se encarga de inicializar la interfaz gráfica de usuario.
        """
        super().__init__()

        # Se define la función encargada de manejar el cierre de la ventana
        self.closeEvent = self.close_event_handler

        # Obtener la resolución de la pantalla
        screen_resolution = QApplication.desktop().screenGeometry()

        # Porcentaje de altura usada por la tabla
        height_percentage = 0.9

        # Calcular el tamaño de la ventana en función del porcentaje deseado
        window_width = screen_resolution.width()
        window_height = screen_resolution.height() * height_percentage

        # Configurar la posición y el tamaño de la ventana usando setGeometry
        self.setGeometry(0, 0, int(window_width), int(window_height))
        self.setWindowTitle("Status de servidores y websites.")
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        # Se setea el path the los json con la información para los servidores y para los websites
        json_server_path = "servers.json"
        json_website_path = "websites.json"

        # Crear tabla de servidores y websites
        self.server_tableWidget, self.website_tableWidget = \
            self.create_tables(json_server_path, json_website_path, window_width, window_height)

        # Crear y correr el hilo del trabajador
        self.server_worker = Worker(json_server_path, "ip", update_server_states)
        self.server_worker.update_signal.connect(self.update_server_i_state)
        self.server_worker.start()

        self.website_worker = Worker(json_website_path, "url", update_website_states)
        self.website_worker.update_signal.connect(self.update_website_i_state)
        self.website_worker.start()

        # Maximiza la ventana al abrir
        self.showMaximized()

    
    def close_event_handler(self, event: QCloseEvent) -> None:
        """
        Define el comportamiento del programa al cerrarse.

        Args:
            event (QCloseEvent): El evento que indica que la ventana se cerrará.
        """
        # Oculta la ventana
        self.hide()

        # Se detienen los Workers
        self.server_worker.stop_works()
        self.website_worker.stop_works()

        # Eliminar objetos del trabajador
        del self.server_worker
        del self.website_worker

        event.accept()


    def create_tables(self, json_server_path: str, json_website_path: str, window_width: int, window_height: int) \
        -> Tuple[QTableWidget, QTableWidget]:
        """
        Crea y devuelve la tabla de servidores y la table de sitios web.

        Args:
        - json_server_path (str): la ruta del archivo JSON que contiene información sobre los servidores.
        - json_website_path (str): la ruta del archivo JSON que contiene información sobre los sitios web.
        - window_width (int): el ancho de la ventana de la aplicación.
        - window_height (int): la altura de la ventana de la aplicación.

        Returns:
        - tuple(QTableWidget, QTableWidget): una tupla de dos objetos QTableWidget que representan las tablas de 
        servidores y sitios web, respectivamente.
        """
        # Crear cabeceras de la tabla
        headers_server_table = ["Nombre", "IP", "Estado"]
        headers_website_table = ["Nombre", "URL", "Estado"]
        # Crear datos de la tabla
        server_data = self.prepare_data(json_server_path, "ip")
        website_data = self.prepare_data(json_website_path, "url")
        #
        table_width = window_width * 0.45
        table_height = window_height - 50
        top_margin = window_height * 0.05
        x_margin = (window_width - 2 * table_width) / 4

        # Crear tabla de servidores
        server_table = \
            self.create_table(
            table_width, 
            table_height, 
            server_data, 
            headers_server_table, 
            x_margin, 
            top_margin
            )

        # Crear tabla
        website_table = \
            self.create_table(
            table_width, 
            table_height, 
            website_data, 
            headers_website_table, 
            window_width - table_width - x_margin, 
            top_margin
            )
        
        return (server_table, website_table)


    def prepare_data(self, jsonpath: str, identifier_tag: str) -> list:
        """
        Crea una lista de datos para una tabla a partir de un archivo JSON que contiene información de varios 
        servidores o sitios web.

        Args:
        - jsonpath (str): la ruta del archivo JSON que contiene la información.
        - identifier_tag (str): el nombre del campo que se usará como identificador único para cada servidor o 
        sitio web.

        Returns:
        - list: una lista de listas, donde cada lista interna representa una fila de la tabla y contiene los 
        valores correspondientes de nombre, identificador y estado inicial para cada servidor o sitio web.
        """
        # Crea una lista vacía para almacenar las listas de datos de cada servidor
        datos = []
        # Lee el archivo JSON con información de varios servidores
        with open(jsonpath, "r") as json_file:
            review_list = json.load(json_file)
        # Crea un item de tabla para usarlo como estado inicial
        initial_state = QTableWidgetItem("LOADING")
        font = QFont()
        font.setBold(True)
        initial_state.setFont(font)
        initial_state.setForeground(QColor(232, 127, 0))
        #
        for review_object in review_list:
            review_datos = [review_object["nombre"], review_object[identifier_tag], initial_state]
            datos.append(review_datos)
        return datos


    def create_table(self, width: int, height: int, table_data: list, headers: list, xpos: int, ypos: int) \
        -> QTableWidget:
        """
        Crea una tabla de datos utilizando los datos y encabezados proporcionados y devuelve el objeto QTableWidget 
        resultante.

        Args:
        - width (int): el ancho de la tabla.
        - height (int): la altura de la tabla.
        - table_data (list): una lista de listas que contiene los datos a mostrar en la tabla.
        - headers (list): una lista de cadenas que representan los encabezados de las columnas de la tabla.
        - xpos (int): la posición x en la que se ubicará la tabla en la ventana de la aplicación.
        - ypos (int): la posición y en la que se ubicará la tabla en la ventana de la aplicación.

        Returns:
        - QTableWidget: el objeto QTableWidget que representa la tabla creada.
        """
        # Crear tabla
        tableWidget = QTableWidget(self)
        tableWidget.setGeometry(int(xpos), int(ypos), int(width), int(height))
        tableWidget.setRowCount(len(table_data))
        tableWidget.setColumnCount(len(headers))

        # Setear cabeceras de la tabla
        tableWidget.setHorizontalHeaderLabels(headers)

        # Agregar datos a la tabla
        for i in range(len(table_data)):
            for j in range(len(headers)):
                item = QTableWidgetItem(table_data[i][j])
                tableWidget.setItem(i, j, item)

        # Hacer que el ancho de las columnas de la tabla use todo el espacio disponible
        header = tableWidget.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        return tableWidget


    def update_i_state(self, table: QTableWidget, row: int , new_state: str) -> None:
        """
        Actualiza el estado de un servidor o sitio web específico en la tabla proporcionada.

        Args:
        - table (QTableWidget): el objeto QTableWidget que representa la tabla en la que se actualizará el estado.
        - row (int): el índice de la fila en la que se actualizará el estado.
        - new_state (str): la cadena que representa el nuevo estado del servidor o sitio web.
        """
        # Actualizar valores de la tabla
        item = table.item(row, 2)
        item.setText(new_state)
        if new_state=="ONLINE":
            # establecer el estilo del texto de la celda
            item.setForeground(QColor(0, 158, 0))
        else:
            # establecer el estilo del texto de la celda
            item.setForeground(QColor(218, 0, 0))


    def update_server_i_state(self, row: int , new_state: str) -> None:
        """
        Actualiza el estado de la fila row de la tabla de servidor con el nuevo estado especificado.

        Args:
        - row (int): el índice de la fila en la que se actualizará el estado.
        - new_state (str): El nuevo estado que se mostrará en la celda correspondiente a la fila row.
        """
        self.update_i_state(self.server_tableWidget, row, new_state)


    def update_website_i_state(self, row: int , new_state: str) -> None:
        """
        Actualiza el estado de la fila row de la tabla de sitios web con el nuevo estado especificado.

        Args:
            row (int): El índice de la fila que se actualizará.
            new_state (str): El nuevo estado que se mostrará en la celda correspondiente a la fila row.
        """
        self.update_i_state(self.website_tableWidget, row, new_state)
