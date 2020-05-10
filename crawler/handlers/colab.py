from .base import BaseCrawler
from ..utils.db import DB


# nohup rclone mount caoyufei_edu:/ /data/drive --allow-other --allow-non-empty --vfs-cache-mode writes >/dev/null 2>&1 &
class Colab(BaseCrawler):

    def __init__(self):
        super().__init__()

    def run(self):
        sql = 'select magnet_link from ii_mgstage where status = 1 order by publish_time desc limit 8'
        data = DB.all(sql)
        for item in data:
            _str = 'downloads.append(lt.add_magnet_uri(ses, \'{}\', params))'.format(item['magnet_link'])
            print(_str)
