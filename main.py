import os
import glob
import time
import json
from inaSpeechSegmenter import Segmenter
from third_party import find_scenes
from third_party import audio_segment_to_gap, video_segment_to_gap
from third_party import Segment, AudioSegment
from third_party import chop
from third_party import SceneAnalytics, SegmentAnalytics

if __name__ == '__main__':
    # files
    files = glob.glob('data/short/*.mp4')
    # Extract audio from video
    audio_template: str = '{}-audio.mp3'
    mp3_saved_directory: str = os.path.join('data', 'mp3')
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        file_dst = os.path.join(mp3_saved_directory, audio_template.format(filename))
        if not os.path.exists(file_dst):
            line = f'ffmpeg -i "{file_src}" -b:a 192K -vn -loglevel error "{file_dst}"'
            print(f'commend line: {line}')
            os.system(line)
        else:
            print(f'{file_dst} has already exist')

    # Audio segmentation process
    segmenter = Segmenter(detect_gender=False)
    segment_template: str = '{}-log.json'
    json_saved_directory: str = os.path.join('data', 'json')
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        file_dst = os.path.join(json_saved_directory, segment_template.format(filename))
        if not os.path.exists(file_dst):
            print(f'speech process {file_src}')
            s = time.time()
            segs = segmenter(file_src)
            jsegs = [AudioSegment(start_seconds=s[1],
                                  end_seconds=s[2],
                                  length_seconds=s[2] - s[1],
                                  audio_type=s[0]) for s in segs]
            e = time.time()
            with open(file_dst, 'w+') as jfile:
                json.dump({'video_path': file_src,
                           'audio_path': os.path.join(mp3_saved_directory, audio_template.format(filename)),
                           'elapse_time': e - s,
                           'segments': AudioSegment.schema().dump(jsegs, many=True)}, jfile, indent=4)
        else:
            print(f'{file_dst} has already exist')

    # Cut the speech part
    scene_template: str = '{}-scene.json'
    json_saved_directory: str = os.path.join('data', 'json')
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        file_dst = os.path.join(json_saved_directory, scene_template.format(filename))
        if not os.path.exists(file_dst):
            print(f'video process {file_src}')
            s = time.time()
            scenes = find_scenes(file_src)
            jscenes = [Segment(start_seconds=start.frame_num / start.framerate,
                               end_seconds=end.frame_num / end.framerate,
                               length_seconds=(end.frame_num - start.frame_num) / start.framerate) for start, end in scenes]
            print(scenes)
            e = time.time()
            with open(file_dst, 'w+') as jfile:
                json.dump({'video_path': file_src,
                           'audio_path': os.path.join(mp3_saved_directory, audio_template.format(filename)),
                           'elapse_time': e - s,
                           'fps': scenes[0][0].framerate,
                           'scenes': Segment.schema().dump(jscenes, many=True)}, jfile, indent=4)
        else:
            print(f'{file_dst} has already exist')

    # load analytics and show
    sample_rate = 120
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        # read audio analytics
        audio_src = os.path.join(json_saved_directory, segment_template.format(filename))
        with open(audio_src, 'r') as jfile:
            audio_segment = AudioSegment.schema().load(json.load(jfile)['segments'], many=True)
        audio_gaps = audio_segment_to_gap(audio_segment)
        # read video analytics
        video_src = os.path.join(json_saved_directory, scene_template.format(filename))
        with open(video_src, 'r') as jfile:
            video_segment = Segment.schema().load(json.load(jfile)['scenes'], many=True)
        video_gaps = video_segment_to_gap(video_segment)
        # print(audio_gaps, video_gaps)
        # for v in audio_gaps:
        #     plt.vlines(v, ymax=1.0, ymin=-1.0, colors='r')
        # for v in video_gaps:
        #     plt.vlines(v, ymax=1.0, ymin=-1.0, colors='g')
        # plt.show()
        # plt.clf()

    # chop all speech audio
    print("clip by speech...")
    segment_dst_template: str = "{}-audio-segment-{}.mp4"
    segment_saved_directory_template: str = os.path.join('data', 'video_segment', "{}")
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        segment_saved_directory = segment_saved_directory_template.format(filename)
        if not os.path.exists(segment_saved_directory):
            os.mkdir(segment_saved_directory)
        # read audio analytics
        audio_analytics_src = os.path.join(json_saved_directory, segment_template.format(filename))
        with open(audio_analytics_src, 'r') as jfile:
            audio_segment = AudioSegment.schema().load(json.load(jfile)['segments'], many=True)
        for sdx, s in enumerate(filter(lambda s: s.audio_type == 'speech', audio_segment)):
            video_dst = os.path.join(segment_saved_directory, segment_dst_template.format(filename, sdx))
            if not os.path.exists(video_dst):
                print(f"chopping {file_src} in range [{s.start_seconds}, {s.end_seconds}] to {video_dst}")
                chop(file_src, s.start_seconds, s.end_seconds, video_dst)
            else:
                print(f"{video_dst} has already exist.")

    # chop all scene
    print("clip by scene...")
    scenes_dst_template: str = "{}-video-segment-{}.mp4"
    scenes_saved_directory_template: str = os.path.join('data', 'video_scene', "{}")
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        scenes_saved_directory = scenes_saved_directory_template.format(filename)
        if not os.path.exists(scenes_saved_directory):
            os.mkdir(scenes_saved_directory)
        # read audio analytics
        video_analytics_src = os.path.join(json_saved_directory, scene_template.format(filename))
        with open(video_analytics_src, 'r') as jfile:
            scenes_segment = Segment.schema().load(json.load(jfile)['scenes'], many=True)
        for sdx, s in enumerate(scenes_segment):
            video_dst = os.path.join(scenes_saved_directory, scenes_dst_template.format(filename, sdx))
            if not os.path.exists(video_dst):
                print(f"chopping {file_src} in range [{s.start_seconds}, {s.end_seconds}] to {video_dst}")
                chop(file_src, s.start_seconds, s.end_seconds, video_dst)
            else:
                print(f"{video_dst} has already exist.")

    # audio analytics
    scenes_dst_template: str = "{}-segment-analytic-{}.mp4"
    analytics_saved_directory_template: str = os.path.join('data', 'analytics_clip', "{}")
    for file_src in files:
        filename = os.path.basename(os.path.splitext(file_src)[0])
        audio_src = os.path.join(json_saved_directory, segment_template.format(filename))
        with open(audio_src, 'r') as jfile:
            audio_segment = AudioSegment.schema().load(json.load(jfile)['segments'], many=True)
        seg_analytics = SegmentAnalytics(segments=audio_segment)
        video_src = os.path.join(json_saved_directory, scene_template.format(filename))
        with open(video_src, 'r') as jfile:
            video_segment = Segment.schema().load(json.load(jfile)['scenes'], many=True)
        proper_scenes = seg_analytics.analytics(video_segment, 3.5, 6.5)
        scenes_analytic_saved_directory = analytics_saved_directory_template.format(filename)
        analytics_saved_directory = analytics_saved_directory_template.format(filename)
        if not os.path.exists(analytics_saved_directory):
            os.mkdir(analytics_saved_directory)
        for sdx, scene in enumerate(proper_scenes):
            analytics_dst = os.path.join(analytics_saved_directory, scenes_dst_template.format(filename, str(sdx).zfill(2)))
            if not os.path.exists(analytics_dst):
                print(f"chopping {file_src} in range [{scene.start_seconds}, {scene.end_seconds}] to {analytics_dst}")
                chop(file_src, scene.start_seconds, scene.end_seconds, analytics_dst)
            else:
                print(f"{analytics_dst} has already existed!")








