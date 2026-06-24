"""
services/crypto_service.py — сервис шифрования/дешифрования.

Fernet — это симметричное шифрование из библиотеки cryptography.
«Симметричное» значит: один и тот же ключ и шифрует, и расшифровывает.

Аналогия из жизни: Fernet — это как обычный замок с ключом.
Тот, у кого есть ключ (FERNET_KEY), может и закрыть, и открыть сейф.

Почему Fernet безопасен?
- Использует AES-128 в режиме CBC (военный стандарт)
- Добавляет временную метку (можно проверить «срок годности» токена)
- Добавляет HMAC-подпись (нельзя подделать данные)
"""

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


class CryptoService:
    def __init__(self) -> None:
        # Если ключ не задан — генерируем временный (для разработки)
        if settings.fernet_key:
            key = settings.fernet_key.encode()
        else:
            key = Fernet.generate_key()

        self._fernet = Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """
        Шифрует строку и возвращает зашифрованную строку (base64).
        
        plain_text: "ghp_myGitHubToken123"
        -> "gAAAAABm...зашифрованный_blob..."
        """
        encrypted_bytes = self._fernet.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")  # сохраняем как строку в MongoDB

    def decrypt(self, encrypted_text: str) -> str:
        """
        Расшифровывает строку.
        Бросает ValueError если ключ неверный или данные повреждены.
        """
        try:
            decrypted_bytes = self._fernet.decrypt(encrypted_text.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            raise ValueError("Не удалось расшифровать данные. Проверьте FERNET_KEY.")

    @staticmethod
    def generate_key() -> str:
        """Генерирует новый Fernet ключ (для setup/onboarding)."""
        return Fernet.generate_key().decode()


# Единственный экземпляр сервиса (паттерн Singleton через модуль)
crypto_service = CryptoService()
