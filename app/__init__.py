from flask import Flask
from flask_assistant import Assistant

# pylint: disable-msg=C0103
app = Flask(__name__)

assist = Assistant(app, route='/assist')

import logging
import os
logger = logging.getLogger('prayer-pal')
logger.addHandler(logging.StreamHandler())
_is_debug = os.environ.get('DEBUG', False)
if logger.level == logging.NOTSET:
    logger.setLevel(
        logging.DEBUG if _is_debug else logging.INFO
    )

if _is_debug:
    logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

from app import views
from app import assistant
