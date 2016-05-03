#!/usr/bin/env python
import threading
import sys
import gi
import time
import logging
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstRtspServer

TEST_PIPELINE = (
    'jackaudiosrc client-name={name} '
    '! audioconvert '
    '! audioresample '
    '! opusenc {encoding_options} '
    '! rtpopuspay name=pay0 ')


DEFAULT_PIPELINE = (
    'jackaudiosrc client-name={name} '
    '! audioconvert '
    '! audioresample '
    '! tee name="splitter" '
    '! queue '
    '! opusenc {encoding_options} '
    '! rtpopuspay name=pay0 splitter. '
    '! queue '
    '! wavenc '
    '! filesink location="{filename}.wav"')


class Emitter():
    """ Audio emitter. """

    def __init__(self, *args, **kwargs):
        self.ip = kwargs.get("ip", '0.0.0.0')
        self.port = str(kwargs.get("port", "8554"))
        self.mount = kwargs.get("mount", "stream")
        self.name = kwargs.get("name", "emitter")
        self.encoding_options = kwargs.get("encoding_options", "")
        self.record = kwargs.get("record", False)
        if self.record:
            logging.info("Recording ON")
            self.pipeline = kwargs.get("pipeline", DEFAULT_PIPELINE).format(name=self.name,
                                                                            encoding_options=self.encoding_options,
                                                                            filename="-".join(time.asctime().split()))
        else:
            logging.info("NOT recording")
            self.pipeline = kwargs.get("pipeline", TEST_PIPELINE).format(name=self.name,
                                                                         encoding_options=self.encoding_options)

    def __call__(self):
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(self.port)
        self.server.set_address(self.ip)
        self.factory = GstRtspServer.RTSPMediaFactory()
        self.factory.set_launch("( {} )".format(self.pipeline))
        self.factory.set_shared(True)
        self.factory.props.latency = 50
        self.server.get_mount_points().add_factory("/{}".format(self.mount), self.factory)
        self.server_id = self.server.attach(None)
        if self.server_id == 0:
            logging.debug("Return value: {}".format(self.server_id))
            logging.debug("SNAFU. Exiting...")
            sys.exit(-1)
        logging.info("stream ready at rtsp://{}:{}/{}".format(self.server.get_address(),
                                                              self.server.get_service(),
                                                              self.mount))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    GObject.threads_init()
    Gst.init(None)
    loop = GObject.MainLoop()
    emitter = Emitter(record=True)
    emitter()
    try:
        logging.debug("Started main loop")
        loop.run()
    except KeyboardInterrupt:
        logging.debug("Caught keyboard interrupt")
        loop.quit()
        logging.debug("Mainloop Stopped")

