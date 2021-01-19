import logging



LOG_STDOUT_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"


def init_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(stream_handler)


log = logging.getLogger()
