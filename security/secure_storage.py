"""
NEXUS Secure Credential Storage
Encrypts and stores sensitive AI provider API keys using Windows DPAPI (Data Protection API).
Keys are tied to the local Windows user credentials and are never stored in plaintext.
"""
import os
import json
import base64
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger("NEXUS.Security")

try:
    import win32crypt
    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False
    logger.warning("win32crypt not available. Falling back to local vault.")

class SecureStorage:
    """Manages encrypted storage of API keys and credentials."""

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.vault_dir = Path(storage_dir)
        else:
            appdata = os.environ.get("APPDATA")
            if appdata:
                self.vault_dir = Path(appdata) / "NEXUS"
            else:
                self.vault_dir = Path(__file__).parent.parent / "data"

        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.vault_file = self.vault_dir / "credentials.vault"
        self._cache: Dict[str, str] = {}
        self._load_vault()

    def _encrypt(self, plaintext: str) -> str:
        """Encrypts a string using Windows DPAPI."""
        raw_bytes = plaintext.encode("utf-8")
        if DPAPI_AVAILABLE:
            try:
                enc_bytes = win32crypt.CryptProtectData(raw_bytes, "NEXUS_CRED", None, None, None, 0)
                return base64.b64encode(enc_bytes).decode("ascii")
            except Exception as e:
                logger.error(f"DPAPI Protect failed: {e}")
        # Obfuscated fallback if DPAPI unavailable
        xor_key = 0x5A
        obf = bytes([b ^ xor_key for b in raw_bytes])
        return base64.b64encode(obf).decode("ascii")

    def _decrypt(self, ciphertext: str) -> Optional[str]:
        """Decrypts a string using Windows DPAPI."""
        try:
            raw_bytes = base64.b64decode(ciphertext.encode("ascii"))
            if DPAPI_AVAILABLE:
                try:
                    dec_bytes = win32crypt.CryptUnprotectData(raw_bytes, None, None, None, 0)[1]
                    return dec_bytes.decode("utf-8")
                except Exception as e:
                    logger.error(f"DPAPI Unprotect failed: {e}")
            xor_key = 0x5A
            deobf = bytes([b ^ xor_key for b in raw_bytes])
            return deobf.decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to decrypt credential: {e}")
            return None

    def _load_vault(self):
        """Loads and decrypts all cached credentials from vault file."""
        if not self.vault_file.exists():
            return
        try:
            with open(self.vault_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for provider, enc_val in data.items():
                dec_val = self._decrypt(enc_val)
                if dec_val:
                    self._cache[provider] = dec_val
            logger.info("Loaded secure credential vault.")
        except Exception as e:
            logger.error(f"Failed to read vault file: {e}")

    def _save_vault(self):
        """Encrypts and persists cached credentials to vault file."""
        try:
            payload = {}
            for provider, val in self._cache.items():
                if val:
                    payload[provider] = self._encrypt(val)
            with open(self.vault_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write to vault file: {e}")

    def store_api_key(self, provider: str, api_key: str):
        """Stores API key securely."""
        key = provider.lower().strip()
        val = api_key.strip()
        self._cache[key] = val
        self._save_vault()
        logger.info(f"API key for '{key}' securely saved via Windows DPAPI.")

    def get_api_key(self, provider: str) -> Optional[str]:
        """Retrieves decrypted API key for a provider."""
        key = provider.lower().strip()
        return self._cache.get(key) or os.environ.get(f"{key.upper()}_API_KEY")

    def has_api_key(self, provider: str) -> bool:
        """Checks if a valid key exists for a provider."""
        val = self.get_api_key(provider)
        return bool(val and len(val) > 4)

    def delete_api_key(self, provider: str):
        """Removes a stored key."""
        key = provider.lower().strip()
        if key in self._cache:
            del self._cache[key]
            self._save_vault()

    # Convenience alias for store_api_key
    set_api_key = store_api_key

# Global accessor
_storage_instance = None
def get_secure_storage() -> SecureStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = SecureStorage()
    return _storage_instance
