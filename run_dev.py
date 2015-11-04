import atexit
import logging

from service.server import app

LOGGER = logging.getLogger(__name__)


@atexit.register
def handle_shutdown(*args, **kwargs):
    LOGGER.info('Stopped the server')

LOGGER.info('Starting the server')
port = int(app.config.get('PORT', 8010))
app.run(host='0.0.0.0', port=port)
