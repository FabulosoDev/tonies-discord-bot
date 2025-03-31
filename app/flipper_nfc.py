class FlipperNfc:
    def __init__(self, nfc_content: str):
        self.nfc_content = nfc_content
        self._ruid = None
        self._auth = None
        self._parse()

    def _parse(self):
        """Parse NFC content for UID and Data Content"""
        for line in self.nfc_content.splitlines():
            if line.startswith('UID:'):
                uid = line.replace('UID:', '').replace(' ', '').lower().strip()
                uid_bytes = [uid[i:i+2] for i in range(0, len(uid), 2)]
                self._ruid = ''.join(uid_bytes[::-1])
            elif line.startswith('Data Content:'):
                self._auth = line.replace('Data Content:', '').replace(' ', '').lower().strip()

    @property
    def ruid(self) -> str | None:
        """Get the reversed UID"""
        return self._ruid

    @property
    def auth(self) -> str | None:
        """Get the authentication data"""
        return self._auth

    def is_valid(self) -> bool:
        """Check if both UID and auth data are present"""
        return bool(self._ruid and self._auth)

    def is_custom_tag(self) -> bool:
        """Check if this is a custom tag (auth is all zeros)"""
        if not self._auth:
            return False
        return self._auth == "0" * len(self._auth)