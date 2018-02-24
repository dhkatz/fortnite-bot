from __future__ import unicode_literals

import json
import mimetypes
import shlex
import subprocess

import youtube_dl
from praw.models import Redditor


class VideoValidator:
    def __init__(self, limit: int = 60, quiet: bool = True):
        mimetypes.init()
        self.duration_limit = limit
        self.extensions = self.get_extensions()
        self.ydl_opts = {'quiet': quiet}

    @staticmethod
    def get_extensions() -> tuple:
        extensions = []
        for ext in mimetypes.types_map:
            if mimetypes.types_map[ext].split('/')[0] == 'video':
                extensions.append(ext)
        return tuple(extensions)

    @staticmethod
    def get_metadata(input_video):
        cmd = "ffprobe -v quiet -print_format json -show_streams"
        args = shlex.split(cmd)
        args.append(input_video)
        ffprobe_output = subprocess.check_output(args).decode('utf-8')
        ffprobe_output = json.loads(ffprobe_output)

        return ffprobe_output

    def find_url(self, data: dict):
        for k, v in data.items():
            if isinstance(v, str):
                if v.endswith(self.extensions):
                    return v
            elif isinstance(v, list):
                d = {}
                for i in range(len(v)):
                    d[str(i)] = v[i]
                return self.find_url(d)
            elif isinstance(v, dict):
                return self.find_url(v)

    def validate(self, url) -> bool:
        meta = None
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            try:
                meta = ydl.extract_info(url, download=False)
            except Exception as e:
                print(e)

        if meta is not None:
            if 'duration' in meta and meta['duration'] <= 60:
                return True
            else:
                url = self.find_url(meta)
                try:
                    metadata = self.get_metadata(url)
                except Exception as e:
                    # print('ERROR', meta, e)
                    pass
                else:
                    print(metadata)
        return False


class UserValidator:
    def __init__(self, subreddit: str, threshold: int = 10):
        self.threshold = threshold
        self.subreddit = subreddit

    def validate(self, user: Redditor) -> bool:
        counter = 0
        for comment in user.comments.new(limit=None):
            if comment.subreddit.display_name.lower() == self.subreddit:
                counter += 1
                if counter >= self.threshold:
                    return True

        return False
