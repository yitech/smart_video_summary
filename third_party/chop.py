import os


def chop(src: str, start_seconds: float, end_seconds: float, dst: str) -> None:
    line = f'ffmpeg -ss {start_seconds} -i "{src}" -t {end_seconds - start_seconds} -hide_banner -loglevel error "{dst}"'
    os.system(line)
    return
