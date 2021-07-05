from typing import List
from .json_classes import Segment, AudioSegment


class SceneAnalytics:
    def __init__(self, scenes: List[Segment]):
        self.scenes = scenes


class SegmentAnalytics:
    def __init__(self, segments: List[AudioSegment]):
        self.segments = segments

    def analytics(self, scenes: List[Segment], length_lower_limit: float, length_upper_limit: float) -> List[Segment]:
        scores = []
        proper_scenes = []
        for scene in scenes:
            first = self._classify(scene.start_seconds)
            last = self._classify(scene.end_seconds)
            if self.segments[first].audio_type == 'speech' or self.segments[last].audio_type == 'speech':
                pass
            else:
                proper_scenes.append(scene)
                scores.append(self._percentage(scene.start_seconds, scene.end_seconds))
        scene_score = sorted(zip(proper_scenes, scores), key=lambda s: s[1], reverse=True)
        print(scene_score)
        proper_scenes = [scene for scene, _ in scene_score]
        proper_scenes = filter(lambda scene: length_lower_limit < scene.length_seconds < length_upper_limit, proper_scenes)

        return list(proper_scenes)

    def _percentage(self, start_seconds: float, end_seconds: float) -> float:
        start = self._classify(start_seconds)
        end = self._classify(end_seconds)
        if start == -1 or end == -1:
            return 0
        length = end_seconds - start_seconds
        speech_length = self.segments[start].end_seconds - start_seconds if self.segments[start].audio_type == 'speech' else 0
        for i in range(start + 1, end):
            if self.segments[i].audio_type == 'speech':
                speech_length += self.segments[i].length_seconds
        length += end_seconds - self.segments[end].start_seconds if self.segments[end].audio_type == 'speech' else 0
        return speech_length / length

    def _classify(self, seconds: float) -> int:
        # linear search
        for idx, seg in enumerate(self.segments):
            if seg.start_seconds <= seconds < seg.end_seconds:
                return idx
        return -1