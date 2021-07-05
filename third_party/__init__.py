from .find_scenes import find_scenes
from .json_classes import Segment, AudioSegment
from .bridge import audio_segment_to_gap, video_segment_to_gap
from .chop import chop
from .analytics import SceneAnalytics, SegmentAnalytics

import os


def init_directories() -> None:
    curr_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(curr_path, '..', 'data')
    directories = ['analytics_clip', 'json', 'mp3', 'short', 'videos', 'video_scene', 'video_segment']
    for directory in directories:
        src_dir = os.path.join(dir_path, directory)
        if not os.path.exists(src_dir):
            os.makedirs(src_dir)
        else:
            print(f'{src_dir} has already existed.')
    return


init_directories()