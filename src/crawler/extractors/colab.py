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

        links = [
            'magnet:?xt=urn:btih:2926D85E7EBD5E9BF729878EFB9008F5C4C4FBE0&dn=300MAAN-372.mp4&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A',
            'magnet:?xt=urn:btih:259531F4588817981BABFCA20E849B23A1569764&dn=jpfou-261ARA-377.mp4&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.',
            'magnet:?xt=urn:btih:5F4E86E88B9EBC2B1D994B9C7F24A527D28EA592&dn=jpfou.com-259LUXU-1092.mp4&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracke',
            'magnet:?xt=urn:btih:A20443D059BDBA5D6C4AB6CD53111FB90E1E5C2F&dn=jpfou.com-200GANA-2031.mp4&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracke',
            'magnet:?xt=urn:btih:FAB751E289519A9C73DF7FDA9754E043BE5073A6&dn=%5BThZu.Cc%5D026MGHT-234&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.',
            'magnet:?xt=urn:btih:A9ED013DCA8D4F3B243D3A4EBE3A4A0A06B8520E&dn=%5BThZu.Cc%5D026MGHT-233&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.',
            'magnet:?xt=urn:btih:F82D126C9B74595DABE4F73BC4BC4A904C2755EC&dn=%5BThZu.Cc%5D026NTRD-074&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.',
            'magnet:?xt=urn:btih:663D0B417478B52DCD4F32882A77ED8BF7344485&dn=%5BThZu.Cc%5D026MOND-162&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.',
            'magnet:?xt=urn:btih:1B02ABB88008EBC67B8C28ABA8002FC68A55DBA5&dn=%5BThZu.Cc%5D026SPRD-1121&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker',
            'magnet:?xt=urn:btih:A6039C954438B56156F5EBA24FBFCB05BFF99996&dn=%5BThZu.Cc%5D026SPRD-1120&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker']


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
