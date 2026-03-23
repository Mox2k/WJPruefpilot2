import logging


def setup_logger(log_file):
    """Initialisiert den Logger."""
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log_info(message):
    """Loggt eine Info-Nachricht."""
    logging.info(message)

# ... (Weitere Funktionen zum Loggen von Fehlern, Warnungen, etc.)
