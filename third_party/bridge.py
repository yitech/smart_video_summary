from typing import List
from .json_classes import Segment, AudioSegment


def audio_segment_to_gap(segments: List[AudioSegment]) -> List[float]:
    length = sum([s.length_seconds for s in segments])
    gaps = {0, length}
    gaps = gaps.union({seg.start_seconds for seg in filter(lambda s: s.audio_type == 'speech', segments)})
    gaps = gaps.union({seg.end_seconds for seg in filter(lambda s: s.audio_type == 'speech', segments)})
    gaps = sorted(gaps)
    return gaps


def video_segment_to_gap(segments: List[Segment]) -> List[float]:
    length = sum([s.length_seconds for s in segments])
    gaps = {0, length}
    gaps = gaps.union({seg.start_seconds for seg in segments})
    gaps = gaps.union({seg.end_seconds for seg in segments})
    gaps = sorted(gaps)
    return gaps
