from pytube import YouTube, Stream
from typing import List
from pathlib import Path


def seconds_to_time_format(seconds: int) -> str:
    h, s = (seconds // 3600), (seconds % 3600)
    m, s = (s // 60), (s % 60)

    return f'{h:02d}:{m:02d}:{s:02d}'


def get_output_dir() -> str:
    home_path = Path.home()
    download_path = home_path.joinpath('Downloads', 'pytd')
    if not Path.exists(download_path):
        download_path.mkdir(parents=True)
    return str(download_path)


def is_yt_url(text: str) -> bool:
    if text.startswith("https://www.youtube.com/watch?v=") or text.startswith("https://youtu.be/") or text.startswith("https://www.youtube.com/shorts/"):
        # try:
        #     available = YouTube(url).check_availability()
        #     if available is None:
        #         print("Entró owo")
        #         return True
        # except Exception as e:
        #     return str(e)
        return True
    return False


def get_progressive_media_formatted(youtube_object: YouTube):
    streams: List[Stream] = youtube_object.streams.filter(progressive=True)
    pg_medias: List[str] = []
    for stream in streams:
        pg_medias.append(str().join([
            str(stream.itag).ljust(5),
            f'{stream.mime_type}/{stream.resolution}'.ljust(17),
            'audio/' + str(stream.abr).ljust(9),
            f'({stream.filesize_mb :.2f} MB)'.rjust(9),
        ]))
    return pg_medias


def get_only_videos_formatted(youtube_object: YouTube) -> List[str]:
    streams: List[Stream] = youtube_object.streams.filter(progressive=False, only_video=True).order_by('mime_type')
    only_videos: List[str] = []
    for stream in streams:
        only_videos.append(str().join([
            str(stream.itag).ljust(6),
            stream.mime_type.ljust(12),
            str(stream.resolution).ljust(6),
            f'({stream.filesize_mb :.2f} MB)'.rjust(9),
        ]))
    return only_videos


def get_only_audios_formatted(youtube_object: YouTube) -> List[str]:
    streams: List[Stream] = youtube_object.streams.filter(progressive=False, only_audio=True)
    only_videos: List[str] = []
    for stream in streams:
        only_videos.append(str().join([
            str(stream.itag).ljust(6),
            stream.mime_type.ljust(12),
            str(stream.abr).ljust(9),
            f'({stream.filesize_mb :.2f} MB)'.rjust(9),
        ]))
    return only_videos


if __name__ == '__main__':
    # yobj = YouTube("https://www.youtube.com/watch?v=KRNUGjc1dFQ")
    #
    # print(get_only_videos_formatted(yobj))
    # print()
    # print(get_progressive_media_formatted(yobj))
    out = get_output_dir()
    print(out)
