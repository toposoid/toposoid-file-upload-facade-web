'''
  Copyright (C) 2025  Linked Ideal LLC.[https://linked-ideal.com/]
 
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.
 
  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from typing import BinaryIO
import shutil
import requests
import time
import glob
import os

class RawDataAdmin():

    def exsitTempraryUse(self, id):
        return True if len(glob.glob("contents/temporaryUse/%s.*" % (id))) > 0 else False


    def getRawData(self, id, file:BinaryIO, resourceNameOrUrl:str, savepath:str):        

        if file is None:
            if not self.exsitTempraryUse(id):
                for attempt in range(3):
                    try:
                        header = {
                            "Accept": "*/*",
                            "Accept-Encoding": "gzip, deflate",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
                        }
                        with requests.get(resourceNameOrUrl, stream=True,verify=False, headers=header, timeout=(10.0, 10.0)) as res:
                            #一時的にファイルに保存
                            with open(savepath, "wb") as f:
                                for chunk in res.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                        break
                    except requests.exceptions.ChunkedEncodingError:
                        time.sleep(1)
        else:
            with open(savepath, 'w+b') as buffer:
                shutil.copyfileobj(file, buffer)    

    """
    def transferFile(filename):
        url =  f"{os.environ["TOPOSOID_CONTENTS_ADMIN_HOST"]}:{os.environ["TOPOSOID_CONTENTS_ADMIN_PORT"]}/transfer"

        with open(filename, 'rb') as f:
            # (ファイル名, ファイルオブジェクト, Content-Type) の順に指定可能
            files = {'file': (filename, f, 'text/plain')}
            response = requests.post(url, files=files, data={'key': 'value'})        
    """