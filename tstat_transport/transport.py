"""
Classes to handle the sending of the json-formatted by the appropriate transport layers.
"""

import warnings

from .common import (
    TstatBase,
    TstatConfigException,
    TstatTransportException,
    TstatTransportWarning,
)

TRANSPORT_DEFAULT = 'rabbit'


class BaseTransport(TstatBase):
    """Base class for the transport-specific classes.

    The PORT attribute should be overridden in the subclasses
    and set to the default port number for the transport protocol
    in question (ie: 80 for http, 5672 for rabbit, etc).  Port will
    be able to be changed to a non-standard port with a command
    line flag.
    """

    def __init__(self, config_capsule, init_user_pass=False):
        super(BaseTransport, self).__init__(config_capsule)

        self._host = self._config.get_cfg_val('host')
        self._port = self._config.get_cfg_val('port')

        # Initialize user/pass from ini file if transport needs it.
        if init_user_pass:
            self._username = self._safe_cfg_val('username')
            self._password = self._safe_cfg_val('password')

        self._payload = None

    def _safe_cfg_val(self, value, **kwargs):
        """
        Call in subclasses to get transport specific config values
        and raise an exception if it's not found.
        """
        try:
            return self._config.get_cfg_val(value, **kwargs)
        except TstatConfigException:
            msg = '[{0}] is a required config value for transport [{1}]'.format(
                value, self._options.transport)
            raise TstatTransportException(msg)

    def send(self):
        """
        Transport/driver specific code to send the payload.
        Set in subclass.
        """
        raise NotImplementedError

    def set_payload(self, p_load):
        """
        Method to set the payload to be sent across the wire.

        Can be overridden in subclasses in case there needs to be
        any additional massaging of the payload before sending.
        """
        self._payload = p_load

    def warn(self, msg):  # pylint: disable=no-self-use
        """Emit a warning."""
        warnings.warn(msg, TstatTransportWarning, stacklevel=2)


class RabbitMQTransport(BaseTransport):
    """
    Class to send JSON payload to a RabbitMQ server.
    """
    def __init__(self, config_capsule):
        super(RabbitMQTransport, self).__init__(config_capsule, init_user_pass=True)

        self._vhost = self._safe_cfg_val('vhost')
        self._queue = self._safe_cfg_val('queue')
        self._use_ssl = self._safe_cfg_val('use_ssl', as_bool=True)

        print self.__dict__

    def send(self):
        print 'XXX', self._port, self._host

TRANSPORT_MAP = dict(
    rabbit=RabbitMQTransport,
)

TRANSPORT_TYPE = [x for x in TRANSPORT_MAP.keys()]