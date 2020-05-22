# nohup rclone mount caoyufei_edu:/ /data/drive --allow-other --allow-non-empty --vfs-cache-mode writes >/dev/null 2>&1 &
import os
from pathlib import Path

import aria2p

from crawler.libs.base import BaseHandler
from crawler.libs.common import md5
from crawler.libs.db import DB

VIDEO_PATH = '/data/video'

if not os.path.isdir(VIDEO_PATH):
    os.makedirs(VIDEO_PATH)


class Download(BaseHandler):

    def __init__(self):
        super().__init__()
        self.aria2 = aria2p.API(
            aria2p.Client(
                host='http://localhost',
                port=6800,
                secret=self.config.get('secret', '66a712e1d520b7fdc2db')
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

            result = []
            for file in download.files:
                file_name = str(file).lower()
                if file_name.find('uue29') != -1:
                    os.system("rm -f '{}'".format(file_name))
                    continue

                if file_name.find('mp4') != -1 or file_name.find('mkv') != -1 or file_name.find('wmv') != -1:
                    result.append(file_name)
                else:
                    os.system("rm -f '{}'".format(file_name))

            n = len(result)
            for i, file in enumerate(result):
                file_name = md5(data['title'])
                if n > 1:
                    file_name = '{}-{}'.format(file_name, (i + 1))
                ext = file.split('.')[-1]
                new_file = os.path.join(VIDEO_PATH, file_name, '.', ext)
                os.system("mv '{}' {}".format(file, new_file))
