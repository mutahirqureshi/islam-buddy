from aenum import Enum


class Event(Enum):
    _init_ = 'event_name, speech, display_text'
    FAJR = 'Fajr', 'Fejjer', 'Fajr'
    SUNRISE = 'Sunrise', 'sunrise', 'sunrise'
    DHUHR = 'Dhuhr', 'Dhuhr', 'Dhuhr'
    ASR = 'Asr', 'Usser', 'Asr'
    MAGHRIB = 'Maghrib', 'Mugreb', 'Maghrib'
    ISHA = 'Isha', 'Ishha', 'Isha'

    @classmethod
    def from_event_name(cls, event_name):
        return next(event for event in cls if event.event_name == event_name)


