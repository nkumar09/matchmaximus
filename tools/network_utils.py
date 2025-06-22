import socket

def check_internet_connection(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Attempts to connect to a known DNS server (Google). Returns True if successful.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False