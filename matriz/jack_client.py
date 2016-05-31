import logging
import jack


class JackClient:

    def __init__(self):
        self.client = jack.Client("matriz-client")
        logging.info(self.client.get_ports())

    def __call__(self):
        logging.info("Hi")

