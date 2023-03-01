
<div style="text-align: justify">

# Monitor de servidores y websites
Este repositorio contiene un programa que permite monitorear el estado de servidores y páginas web, a partir de archivos JSON que contienen la información de cada servidor o página web.

## Requisitos
Para ejecutar el programa es necesario instalar los siguientes paquetes:

- PyQt5: para la creación de la interfaz gráfica
- qdarkstyle: para cambiar el estilo visual de la interfaz
- requests: para realizar peticiones HTTP a las páginas web y verificar si están funcionando.

Para esto, se debe correr en la consola el siguiente comando:

`pip install PyQt5 QDarkStyle requests`

## Ejecución y cierre de ventana
Una vez instalados los paquetes, para ejecutar el programa simplemente se debe correr el archivo **run_status_bot.py**. Al abrirse la interfaz, se mostrarán dos tablas: una para el estado de los servidores y otra para el estado de las páginas web. Para cada servidor o página web, se mostrará su nombre, su IP o URL, y su estado actual, que puede ser **LOADING**, **ONLINE** o **OFFLINE**.

Al cerrar la ventana, del monitor, va a quedar la consola de python por unos segundos. Es importante que cuando esto pase, no se cierre la consola de python, esta se cerrará automaticamente despues de unos segundos.

## Archivos JSON
El archivo servers.json y websites.json son los archivos JSON que contienen la información de los servidores y páginas web, respectivamente. Cada archivo debe tener una lista de objetos, donde cada objeto contiene su nombre y su IP o URL de un servidor o página web.

## Funcionamiento
El programa también incluye un Worker, que se encarga de comprobar periódicamente el estado de los servidores y páginas web. Este Worker se ejecuta en un hilo aparte para no bloquear la interfaz gráfica. Cuando se detecta un cambio en el estado de un servidor o página web, se actualiza automáticamente la tabla correspondiente.

Para detener el programa se debe cerrar la ventana, y esperar que la consola de python se cierre automaticamente despues de un tiempo.

## Sobre el desarrollo
Este proyecto incluye fragmentos de código generados con la ayuda del modelo Chat GPT de OpenAI, que está sujeto a los Términos de servicio de la API de OpenAI.

</div>
