import os
import sys

from google.colab import drive
from progress.bar import Bar

from .base import BaseCrawler


class Colab(BaseCrawler):

    def __init__(self):
        super().__init__()

    def run(self):
        import libtorrent as lt

        os.popen(
            'nohup rclone mount pod78:/ /content/drive --allow-other --allow-non-empty --vfs-cache-mode writes >/dev/null 2>&1 &')

        ses = lt.session()
        ses.listen_on(6881, 6891)
        downloads = []
        params = {"save_path": "/content/drive/mgstage"}

        downloads.append(
            lt.add_magnet_uri(ses,
                              'magnet:?xt=urn:btih:2926D85E7EBD5E9BF729878EFB9008F5C4C4FBE0&dn=300MAAN-372.mp4&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A',
                              params)
        )

        import time

        while downloads:
            next_shift = 0
            for index, download in enumerate(downloads[:]):
                if not download.is_seed():
                    s = download.status()
                    sys.stdout.write(
                        '\r{}:{} {}kb/s'.format(download.name(), s.progress * 100, str(s.download_rate / 1000)))
                    sys.stdout.flush()
                else:
                    next_shift -= 1
                    ses.remove_torrent(download)
                    downloads.remove(download)
                    print(download.name(), "complete")
            time.sleep(1)
