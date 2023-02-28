from datetime import datetime, timedelta
from email.message import EmailMessage 
import urllib.request as req
import subprocess as sub
from typing import Tuple
import smtplib
import time

def ping_server(host, name) -> int:
    """
    Corre el comando de consola ping, con {host} como argumento y retorna la respuesta.

    Además de lo anterior, imprime en consola que se está corriendo el ping, detallando para
    que servidor, y cual es el nombre de este.

    Args:
        host (str): URL o IP del servidor.
        name (str): Nombre del servidor.
    Returns:
        int: La respuesta de correr ping en la consola, con host de argumento y -w 10 como flag.

    """
    print(f"Intentando hacer ping a {host} ({name})")
    return sub.getstatusoutput(f"ping -w 10 {host}")[0]
    #Usar este return en caso de desear ver info de ping
    #return os.system(f"ping -w 10 {host}")

def ping_multiplie_tries(host, max_attempts = 3, wait_time = 3) -> Tuple[int, str]:
    """
    Hace ping multiples veces sobre la ip, y retorna la respuesta al ping, y un string comentando
    si fue exitoso o no.

    Corre la función ping_server(host) múltiples veces. Si al menos una de las respuestas
    es exitosa, retorna 0 y un string diciendo que fue exitosa, si no retorna 1 y un string 
    diciendo que falló.

    Args:
        host (list(str, str)): IP y nombre del servidor.
        max_attempts (int) optional: Número de intentos permitidos de correr ping con resultado fallido.
                                     Valor por defecto: 3.
        wait_time (int) optional: Tiempo de espera para correr ping de nuevo si falló.
                                  Valor por defecto: 3.

    Returns:
        Tuple[int,str]: El primer valor es la respuesta de correr ping en consola (0 o 1).
                        El segundo valor es un string que indica si el ping fue exitoso o no.
    """
    sv_IP = host[0]
    sv_name = host[1]
    res = ping_server(sv_IP, sv_name)
    attempt = 1

    while res != 0 and attempt < max_attempts:
        print(f"Intento {attempt} de ping {sv_IP} falló.\n")
        time.sleep(wait_time)
        res = ping_server(sv_IP, sv_name)
        attempt += 1

    if res == 0:
        msg = f'<li>El servidor <b>{sv_IP} ({sv_name})</b> ha respondido correctamente al ping.</li>'
        print(f"Intento {attempt} de ping exitoso.\n")
    else:
        output_message = sub.getoutput(f"ping -w 10 {sv_IP}")
        msg = f'<li>El servidor <b>{sv_IP} ({sv_name})</b> no responde ante el ping.<br>\
                    OUTPUT: {output_message}</li>'
        print(f"Intento {attempt} de ping {sv_IP} falló.\n")

    return (res,msg)


def create_ping_email_text(fail_msg, successful_msg) -> str:
    """
    Retorna un string que contiene la información sobre si los servidores respondieron correctamente
    o con fallas al ping, con etiquetas html.

    Args:
        fail_msg (str): Información sobre que servidores fallarón el ping y su mensaje de error.
        successful_msg (str): Información sobre que servidores tuvieron ping exitoso.

    Returns:
        str: Información general sobre cuales servidores corrieron ping correctamente, y cuales con
             falla.
    """
    title = '<h3>Información sobre servidores:</h3>'
    info = ''
    if fail_msg != '':
        info += f'</p>Los siguientes servidores no respondieron correctamente al ping:<p>'
        info += f'<ul>{fail_msg}</ul>'
        info += '<br>'
    if successful_msg != '':
        info += f'<p>Los siguientes servidores respondieron correctamente al ping:</p>'
        info += f'<ul>{successful_msg}</ul>'
    return title + info


def create_website_email_text(fail_msg, successful_msg) -> str:
    """
    Retorna un string que contiene la información sobre si los websites respondieron correctamente
    o con fallas al intentar abrirla, con etiquetas html.

    Args:
        fail_msg (str): Información sobre que websites fallarón al intentar abrirlos y su código de
                        estado.
        successful_msg (str): Información sobre que websites tuvieron éxito al intentar entrar.

    Returns:
        str: Información general sobre cuales websites lograrón ser abiertas con exito, y cuales
             con falla.
    """
    title = '<h3>Información sobre las páginas web:</h3>'
    info = ''
    if fail_msg != '':
        info += '<p>Los siguientes websites respondieron con código de error:</p>'
        info += f'<ul>{fail_msg}</ul>'
        info += '<br>'
    if successful_msg != '':
        info += '<p>Los siguientes websites respondieron con código sin error:</p>'
        info += f'<ul>{successful_msg}</ul>'
    return title + info


def create_email(body, sender, receiver) -> str:
    """
    Retorna un correo con cuerpo, emisor, y receptor del correo según los argumentos de la función,
    interpretando el cuerpo en HTML.

    Primero crea un texto en formato de mensaje de email, luego se setea que su cuerpo sea el
    argumento {body}, interpretandolo en html, se agrega un asunto sobre el status de los servidores
    y websites, y se setea el emisor y receptor del email según los argumentos {sender} y {receiver}
    de la función.

    Finalmente, se retorna el email creado, pero transformado en string.

    Args:
        body (str): El cuerpo del correo
        sender (str): Quién envia el correo
        receiver (str): Quienes reciben el correo

    Returns:
        str: El email formato email con la información de los argumentos pero en tipo string.
    """
    email = EmailMessage()
    email.set_content(body, subtype="html")
    email['Subject'] = 'Status servidores y websites'
    email['From'] = sender
    email['To'] = receiver
    return email.as_string()


def send_email(failed_servers, successful_servers, failed_websites, successful_websites, error = True):
    """
    Crea un mail con la información de los status de los servers y websites, y lo envia a una
    lista de receptores.

    Se usan las funciones de create_ping_email_text y create_website_email_text para obtener los
    strings con la información de el status de los servidores y los websites.

    Se usa la función create_email para crear el mail con toda la información de los servidores y
    los websites, quien envia el mail, y quienes lo reciben.

    Luego se ingresa a la cuenta de email de alertas de Lucas Diesel, usando una librearia que usa
    el protocolo SMTP, envia el mail creado e imprime en la pantalla que el mail fue enviado. En
    caso de que esta parte falle, se imprimie en pantalla que no se pudo enviar.

    Args:
        failed_servers (str): Información sobre que servidores fallarón el ping y su mensaje de error.
        successful_servers (str): Información sobre que servidores tuvieron ping exitoso.
        failed_websites (str): Información sobre que websites fallarón al intentar abrirlos, y su
                               código de estado.
        successful_websites (str): Información sobre que websites tuvieron éxito al intentar entrar.
    """
    email_address = "alertas_log@lucasdiesel.cl"
    email_password = "..."
    sender = email_address
    receivers = 'name@lucasdiesel.cl'

    ping_body = create_ping_email_text(failed_servers, successful_servers)
    websites_body = create_website_email_text(failed_websites, successful_websites)
    if error:
        email = create_email(f'{ping_body}<br>{websites_body}', sender, receivers)
    else:
        email = create_email(
            f'<h1>Análisis sin errores.<h1>{ping_body}<br>{websites_body}', sender, receivers
            )

    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(email_address, email_password)
        smtp.sendmail(sender, receivers, email)
        smtp.quit()
        print(f"Email sent to {receivers}\n\n")
    except smtplib.SMTPAuthenticationError:
        print("The server didn't accept the username password combination.\n")
        print("The email could not be sent.\n")
    except smtplib.SMTPRecipientsRefused:
        print("The server rejected ALL recipients (no mail was sent).\n")
        print("The email could not be sent.\n")
    except smtplib.SMTPSenderRefused:
        print("The server didn't accept the from_address.\n")
        print("The email could not be sent.\n")
    except:
        print("Something went wrong. The email could not be sent.\n")


def check_pings(hosts) -> Tuple[str, str]:
    """
    Corre el comando ping para los servidores de la lista hosts, y retorna mensajes de cuales
    servidores lo corrieron de forma exitosa y cuales fallaron.

    Primero se setean que servidores se probaran y cuantos intentos maximos hay para correr el ping.

    Luego, se corre la función ping_multiple_tries para cada uno de los servidores, y se guarda
    la respuesta del ping, y el mensaje devuelto por la función, donde se establece si el ping
    funcionó.

    Finalmente se retorna una tupla, con la union de los mensajes de falla en la primera coordenada
    y la union de los mensajes de exito en la segunda coordenada.

    Args:
        hosts (list(list(str, str))): IPs de los servidores con sus nombres.

    Returns:
        Tuple[str,str]: La primera coordenada es la información sobre que servidores fallaron el ping,
                        y la segunda coordenada es la información sobre que servidores tuvieron ping
                        exitoso.
    """
    print("\nVERIFICACIÓN DE PINGS DE SERVIDORES:\n")

    fail_msg = ''
    successful_msg = ''

    for host in hosts:
        (res, msg) = ping_multiplie_tries(host)
        if res == 0:
            successful_msg += msg
        else:
            fail_msg += msg

    return (fail_msg, successful_msg)


def request_website(url) -> Tuple[bool, str]:
    """
    Retorna un string con el código de respuesta de estado del URL del argumento, y un booleano 
    que indica si el código es de error.

    Args:
        url (str): La dirección de un sitio web.

    Returns:
        Tuple[bool, str]: La primera coordenada es un booleano que indica si el código obtenido
                          corresponde a un error. La segunda coordenada es un mensaje que indica
                          el código de respuesta de estado y que tipo de código es.
    """
    try:
        res = req.urlopen(url).getcode()

        message_map = {
            range(100, 200): f'<li>La request a <b>{url}</b> devuelve: {res} (Respuesta informativa)</li>',
            range(200, 300): f'<li>La request a <b>{url}</b> devuelve: {res} (Respuesta satisfactoria)</li>',
            range(300, 400): f'<li>La request a <b>{url}</b> devuelve: {res} (Redirección)</li>',
            range(400, 500): f'<li>La request a <b>{url}</b> devuelve: {res} (Error de cliente)</li>',
            range(500, 600): f'<li>La request a <b>{url}</b> devuelve: {res} (Error del servidor)</li>'
        }

        for rng, message in message_map.items():
            if res in rng:
                successful = True if res in range(100, 400) else False
                msg = message

    except:
        successful = False 
        msg = f'<li>No se pudo realizar la solicitud a <b>{url}</b>.</li>'
        res = -1

    print(f"Codigo de retorno de {url}: {res}\n")

    return (successful, msg)


def check_websites(websites) -> Tuple[str, str]:
    """
    Envia una solicitud a los sitios web de la lista de websites, y retorna mensajes de cuales
    websites devolvieron códigos de respuesta de entrada exitosa, y cuales códigos de error.

    Primero se setean que sitios web se probaran.

    Luego, se corre la función request_website para cada uno de los sitios web, y se guarda
    el booleano que indica si hubo algun error, y el mensaje devuelto por la función, donde
    se establece si se pudo entrar al sitio web.

    Finalmente se retorna una tupla, con la union de los mensajes de falla en la primera coordenada
    y la union de los mensajes de exito en la segunda coordenada.

    Args:
        websites (list(str)): La lista con URLs.

    Returns:
        Tuple[str,str]: La primera coordenada es la información sobre que websites lanzaron código
                        de error y la segunda cuales no.
    """
    print("\nVERIFICACIÓN DE WEBSITES:\n")

    fail_msg = ''
    successful_msg = ''

    for website in websites:
        (successful, msg) = request_website(website)
        if successful:
            successful_msg += msg
        else:
            fail_msg += msg

    return (fail_msg, successful_msg)


def get_interval_time(send_time, dif):
    """
    Retorna una tupla con un limite superior, y uno inferior de un intervalo de rango dif minutos
    menos 30 segundos, alrededor de la fecha send_time.

    Al definir los limites superior e inferior del intervalo, se hace a ambos un ajuste de 15
    segundos. Esto es una incertidumbre para evitar cualquier tipo de error. A priori, no es
    necesario. Es importante que la suma de estas incertidumbres en segundos no puede sumar más
    o igual de 60, pues los intervalos se solaparian.

    Args:
        send_hour (datetime): Hora a la que se le desea crear un intervalo alrededor.
        dif (int): Cantidad de minutos entre cada extremo del intervalo.

    Returns:
        Tuple[datetime, datetime]: La tupla exterior representa un intervalo donde cada 
                                                tupla dentro, representa una hora y un minuto 
                                                respectivamente. Así formando un intervalo de tiempo. 
    """
    t1 = datetime.strptime(send_time, "%H:%M:%S")

    down_time = t1 - timedelta(minutes=dif, seconds=15)
    up_time = t1 + timedelta(minutes=dif-1, seconds=15) 

    return (down_time, up_time)


def general_check(send_only_if_error, send_times, time_between_revisions, websites, hosts):
    """
    Corre los chequeos de ping y website, y si hubo un error en alguno de ellos, o si la hora 
    actual es hora de revision, se envia un email con la información de los chequeos.

    La variable que guarda el tiempo actual representa la hora que se corre el script, pero con
    los segundos en 0.

    Args:
        send_only_if_error (bool): Indica si se desea que el correo se envie solo si hay error
                                   o no.
        send_times (list): Es una lista con las horas donde se enviaran correos independiente
                           de si hay error.
        time_between_revisions (int): Indica cada cuantos minutos se correra el bot.
        websites (list(str)): La lista con URLs.
        hosts (list(list(str, str))): IPs de los servidores con sus nombres.
    """

    now_time = datetime.strptime(datetime.now().replace(second=0).time().strftime("%H:%M:%S"), "%H:%M:%S")

    (fail_msg_website, successful_msg_website) = check_websites(websites)
    (fail_msg_ping, successful_msg_ping) = check_pings(hosts)

    if (not send_only_if_error) or fail_msg_ping != '' or fail_msg_website != '':
        send_email(fail_msg_ping, successful_msg_ping,
                    fail_msg_website, successful_msg_website) 
    
    else:
        for send_time in send_times:
            (down_time, up_time) = get_interval_time(send_time, time_between_revisions/2)
            if down_time <= now_time <= up_time:
                send_email(fail_msg_ping, successful_msg_ping,
                            fail_msg_website, successful_msg_website, False)


def main():
    """
    Chequea el estado de los servidores y websites. En caso de error envía un correo.

    Guarda en variables los websites y servidores a revisar.

    Guarda en una variable un booleano de si mandará correo solo si hay errores, o siempre.

    Guarda en una variable un entero que determina cada cuantos minutos se correrá el script.
    """
    
    
    #Usar esto como ip o url si desea probarse un error
    #www.lucasdiesel.cl > /dev/null
    websites = [
        "http://aplwms.lucasdiesel.cl:3010", 
        "http://apia.lucasdiesel.cl/diesel/",
        "https://dtparts.cl/", 
        "https://lucasdiesel.cl/"
        ]

    hosts = [ 
        ["10.10.1.4", "Servidor Aplicaciones"],
        ["10.10.1.7", "Servidor Qliksense"],
        ["10.10.1.8", "Servidor de escritorio"],
        ["10.10.1.10", "Servidor de BDs"],
        ["10.10.1.13", "Servidor Power BI"],
        ["10.10.1.14", "Servidor de AD - DNS"],
        ["10.10.1.15", "Servidor AD - DNS Secundario"],
        ["10.10.1.18", "Servidor de APIA"],
        ["10.10.1.19", "Catálogo de Bosch"],
        ["10.10.1.25", "Servidor de facturación"],
        ["10.10.1.26", "Servidor de Ocsinventory"],
        ["10.10.1.30", "Servidor de APIs Rest"],
        ["10.10.1.31", "Servidor de VM Backup"],
        ["10.10.1.32", "Servidor de VM QAs"],
        ["10.10.1.33", "Servidor de réplicas"],
        ["10.10.1.35", "Servidor de BDs QA"],
        ["10.10.1.38", "Servidor de QA DTE"],
        ["10.10.1.40", "Servidor servicios QA"],
        ["10.10.1.42", "Servidor BD APIA QA"],
        ["10.10.1.43", "Remoto"]
        ]
    
    #True para enviar correo solo si hay errores.
    #False para enviar correo despues de cada chequeo, haya error, o no.
    send_only_if_error = True

    #Horas a las que se enviara un correo independiente de si hay error o no.
    send_times = ["08:00:00", "13:00:00", "18:00:00"]

    #Cantidad de minutos entre cada corrida del script. Debe ser al menos 10 minutos.
    #Debe ser una cantidad par de minutos
    #Se recomiendan 10 minutos para esta variable
    time_between_revisions = 10
    assert(time_between_revisions%2==0)
    
    general_check(send_only_if_error, send_times, time_between_revisions, websites, hosts)


if __name__ == "__main__":
    main()
