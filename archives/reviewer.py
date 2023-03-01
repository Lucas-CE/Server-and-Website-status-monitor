import urllib.request as req
import subprocess as sub


def ping_multiplie_tries(server_ip: str, max_attempts: int = 3) -> bool:
    """
    Corre comando ping en consola multiples veces y retorna un booleano indicando si el ping fue exitoso.

    Si al correr el comando ping, arroja error, se intenta max_attempts - 1 veces más, si al menos una de 
    las respuestas es exitosa, retorna True, si no, retorna False.

    Args:
        sv_info (str): La IP del servidor y su nombre.
        max_attempts (int) optional: Número de intentos permitidos de correr ping con resultado fallido.
                                     Por defecto 3.

    Returns:
        bool: True si el ping fue exitoso. False en caso contrario.
    """
    response = sub.getstatusoutput(f"ping {server_ip}")[0]
    attempt = 1

    while response != 0 and attempt < max_attempts:
        response = sub.getstatusoutput(f"ping {server_ip}")[0]
        attempt += 1

    return True if response == 0 else False



def request_website(url: str, max_attempts: int = 2) -> bool:
    """
    Intenta abrir la página web de la url, y retorna True si el código de retorno es exitoso, y False
    en caso contrario.

    Args:
        url (str): La dirección URL de un sitio web.
        max_attempts (int) optional: Número de intentos permitidos de correr ping con resultado fallido.
                                     Por defecto 2.

    Returns:
        bool: True si el código de retorno está entre 100 y 400, y False en caso contrario.
    """
    try:
        response = req.urlopen(url).getcode()
        attempt = 1
        successful = True if response in range(100, 400) else False

        while not response and attempt < max_attempts:
            response = req.urlopen(url).getcode()
            successful = True if response in range(100, 400) else False
            attempt += 1
    except:
        successful = False

    return successful
    