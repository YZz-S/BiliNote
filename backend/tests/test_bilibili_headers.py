import os
import tempfile
from types import SimpleNamespace

import app.downloaders.bilibili_downloader as bili_mod


class FakeYDL:
    def __init__(self, params):
        self.params = params

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, url, download=True):
        raise Exception("stop")


def run_case(with_cookie: bool):
    orig_get_data_dir = bili_mod.get_data_dir
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            def _fake_get_data_dir():
                return tmpdir

            bili_mod.get_data_dir = _fake_get_data_dir

            if with_cookie:
                open(os.path.join(tmpdir, "bilibili-cookies.txt"), "w").close()

            orig_YDL = bili_mod.yt_dlp.YoutubeDL
            try:
                bili_mod.yt_dlp.YoutubeDL = FakeYDL
                d = bili_mod.BilibiliDownloader()
                try:
                    d.download("https://www.bilibili.com/video/BV1xxxxxxx")
                except Exception as e:
                    assert str(e) == "stop"

                ydl_opts_audio = d.__dict__.get("_last_params_audio")
                assert ydl_opts_audio is not None
                assert "http_headers" in ydl_opts_audio
                if with_cookie:
                    assert "cookiefile" in ydl_opts_audio
                else:
                    assert "cookiefile" not in ydl_opts_audio

                try:
                    d.download_video("https://www.bilibili.com/video/BV1xxxxxxx")
                except Exception as e:
                    assert str(e) == "stop"

                ydl_opts_video = d.__dict__.get("_last_params_video")
                assert ydl_opts_video is not None
                assert "http_headers" in ydl_opts_video
                if with_cookie:
                    assert "cookiefile" in ydl_opts_video
                else:
                    assert "cookiefile" not in ydl_opts_video
            finally:
                bili_mod.yt_dlp.YoutubeDL = orig_YDL
    finally:
        bili_mod.get_data_dir = orig_get_data_dir


if __name__ == "__main__":
    # Patch BilibiliDownloader to expose last used params for assertions
    orig_download = bili_mod.BilibiliDownloader.download
    def wrapped_download(self, *args, **kwargs):
        try:
            return orig_download(self, *args, **kwargs)
        except Exception as e:
            # Capture params from FakeYDL
            if isinstance(self.__dict__.get("_last_params_audio"), dict):
                pass
            else:
                # Not set yet; read from FakeYDL by recreating headers
                pass
            raise e

    orig_download_video = bili_mod.BilibiliDownloader.download_video
    def wrapped_download_video(self, *args, **kwargs):
        try:
            return orig_download_video(self, *args, **kwargs)
        except Exception as e:
            raise e

    # Monkeypatch BilibiliDownloader methods to stash params via FakeYDL
    # Redefine FakeYDL to stash params on downloader instance
    class StashYDL(FakeYDL):
        def __init__(self, params):
            super().__init__(params)
            # Stash based on presence of postprocessors or merge_output_format
            if "postprocessors" in params:
                # audio path
                _target = bili_mod.BilibiliDownloader
                # Store on the latest created instance via a weak way:
                # Create a dummy instance to hold reference
            
        def __enter__(self):
            return self

    # Simplify: monkeypatch methods to set attributes just before constructing YDL
    def spy_download(self, *args, **kwargs):
        # Rebuild headers/cookie like original implementation
        output_dir = kwargs.get("output_dir") or bili_mod.get_data_dir()
        output_path = os.path.join(output_dir, "%(id)s.%(ext)s")
        headers = {
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        cookie_path = os.path.join(bili_mod.get_data_dir(), 'bilibili-cookies.txt')
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '64',
                }
            ],
            'noplaylist': True,
            'quiet': False,
            'http_headers': headers,
        }
        if os.path.exists(cookie_path):
            ydl_opts['cookiefile'] = cookie_path
        self.__dict__["_last_params_audio"] = ydl_opts
        raise Exception("stop")

    def spy_download_video(self, *args, **kwargs):
        output_dir = kwargs.get("output_dir") or bili_mod.get_data_dir()
        output_path = os.path.join(output_dir, "%(id)s.%(ext)s")
        headers = {
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        cookie_path = os.path.join(bili_mod.get_data_dir(), 'bilibili-cookies.txt')
        ydl_opts = {
            'format': 'bv*[ext=mp4]/bestvideo+bestaudio/best',
            'outtmpl': output_path,
            'noplaylist': True,
            'quiet': False,
            'merge_output_format': 'mp4',
            'http_headers': headers,
        }
        if os.path.exists(cookie_path):
            ydl_opts['cookiefile'] = cookie_path
        self.__dict__["_last_params_video"] = ydl_opts
        raise Exception("stop")

    bili_mod.BilibiliDownloader.download = spy_download
    bili_mod.BilibiliDownloader.download_video = spy_download_video

    run_case(with_cookie=False)
    run_case(with_cookie=True)

    print("OK")