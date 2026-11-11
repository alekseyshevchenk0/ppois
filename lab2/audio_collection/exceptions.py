"""Собственные исключения предметной области «Аудиоколлекция»."""


class AudioCollectionError(Exception):
    """Базовое исключение предметной области."""


class InvalidTrackDataError(AudioCollectionError):
    """Некорректные данные трека, альбома, исполнителя или длительности."""


class InvalidRatingError(AudioCollectionError):
    """Оценка вне допустимого диапазона."""


class InvalidAudioFormatError(AudioCollectionError):
    """Неподдерживаемый или неверный аудиоформат."""


class InvalidVolumeError(AudioCollectionError):
    """Громкость вне допустимого диапазона."""


class InvalidAmountError(AudioCollectionError):
    """Некорректное количество, сумма или параметр настроек."""


class WeakPasswordError(AudioCollectionError):
    """Пароль не удовлетворяет требованиям."""


class DuplicateTrackError(AudioCollectionError):
    """Трек уже существует."""


class ItemNotFoundError(AudioCollectionError):
    """Трек, альбом или другой объект не найден."""


class StorageFullError(AudioCollectionError):
    """Нет места на носителе, полке или в плейлисте."""


class EmptyQueueError(AudioCollectionError):
    """Очередь воспроизведения пуста."""


class PaymentError(AudioCollectionError):
    """Недостаточно средств, повторный платёж или неактивная подписка."""
