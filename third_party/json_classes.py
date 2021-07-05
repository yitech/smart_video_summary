from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Segment:
    start_seconds: float
    end_seconds: float
    length_seconds: float


@dataclass_json
@dataclass
class AudioSegment:
    start_seconds: float
    end_seconds: float
    length_seconds: float
    audio_type: str
