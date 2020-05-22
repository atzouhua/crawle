# nohup rclone mount caoyufei_edu:/ /data/drive --allow-other --allow-non-empty --vfs-cache-mode writes >/dev/null 2>&1 &
import aria2p

from crawler.libs.base import BaseHandler
from crawler.libs.db import DB


class Download(BaseHandler):

    def __init__(self):
        super().__init__()
        self.aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=6800,
                secret="66a712e1d520b7fdc2db"
            )
        )

    def action_index(self):
        sql = 'select * from ii_sehuatang where status = 1 order by id desc limit 5'
        data = DB.all(sql)
        for item in data:
            download = self.aria2.add_magnet(item['magnet_link'])
            print(download.status)

    def action_print(self):
        downloads = self.aria2.get_downloads()
        for download in downloads:
            print(download.name, download.status, download.is_complete)
