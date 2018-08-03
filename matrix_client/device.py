from .errors import MatrixRequestError


class Device(object):

    def __init__(self,
                 api,
                 user_id,
                 device_id,
                 database=None,
                 display_name=None,
                 last_seen_ip=None,
                 last_seen_ts=None,
                 verified=False,
                 blacklisted=False,
                 ignored=False,
                 ed25519_key=None,
                 curve25519_key=None):
        self.api = api
        self.user_id = user_id
        self.device_id = device_id
        self.database = database
        self.display_name = display_name
        self.last_seen_ts = last_seen_ts
        self.last_seen_ip = last_seen_ip
        self._verified = verified
        self._blacklisted = blacklisted
        self._ignored = ignored
        self._ed25519 = ed25519_key
        self._curve25519 = curve25519_key

    def get_info(self):
        """Gets information on the device.

        The ``display_name``, ``last_seen_ip`` and ``last_seen_ts`` attribute will
        get updated, if these were available.

        Returns:
            True if successful, False if the device was not found.
        """
        try:
            info = self.api.get_device(self.device_id)
        except MatrixRequestError as e:
            if e.code == 404:
                return False
            raise
        self.display_name = info.get('display_name')
        self.last_seen_ip = info.get('last_seen_ip')
        self.last_seen_ts = info.get('last_seen_ts')
        return True

    def save_to_db(func):
        def save(self, boolean):
            if not self.ed25519:
                raise ValueError('Changing this property is not allowed when the device '
                                 'keys are unknown.')
            func(self, boolean)
            self.database.save_device_keys({self.user_id: {self.device_id: self}})
        return save

    @property
    def ed25519(self):
        return self._ed25519

    @property
    def curve25519(self):
        return self._curve25519

    @property
    def verified(self):
        return self._verified

    @verified.setter
    @save_to_db
    def verified(self, boolean):
        self._verified = boolean

    @property
    def ignored(self):
        return self._ignored

    @ignored.setter
    @save_to_db
    def ignored(self, boolean):
        self._ignored = boolean

    @property
    def blacklisted(self):
        return self._blacklisted

    @blacklisted.setter
    @save_to_db
    def blacklisted(self, boolean):
        self._blacklisted = boolean
