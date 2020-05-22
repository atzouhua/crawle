# nohup rclone mount caoyufei_edu:/ /data/drive --allow-other --allow-non-empty --vfs-cache-mode writes >/dev/null 2>&1 &
import os

import aria2p

from crawler.libs.base import BaseHandler
from crawler.libs.db import DB

VIDEO_PATH = '/data/video'

if not os.path.isdir(VIDEO_PATH):
    os.makedirs(VIDEO_PATH)


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
            if str(download.name).find('METADATA') != -1:
                continue

            if not download.is_complete:
                continue

            sql = 'select * from ii_sehuatang where magnet_link like %s'
            data = DB.one(sql, ('%{}%'.format(download.info_hash),))
            if not data:
                continue

            result = {}
            for file in download.files:
                file_name = str(file.path).lower()
                if file_name.find('mp4') == -1 or file_name.find('mkv') == -1 or file_name.find('wmv') == -1:
                    os.remove(file_name)
                if not result.get(data['id']):
                    result[data['id']] = []
                result[data['id']].append(file_name)
            print(result)
            print('')
