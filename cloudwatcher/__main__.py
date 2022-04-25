import logging
import sys

from .cli import main

if __name__ == "__main__":

    _LOGGER = logging.getLogger(__name__)

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOGGER.error("Program canceled by user!")
        sys.exit(1)
