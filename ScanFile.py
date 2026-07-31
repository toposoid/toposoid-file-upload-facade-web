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

import clamd
import ToposoidCommon as tc
from ToposoidCommon.model import TransversalState
import os

LOG = tc.LogUtils(__name__)

class ScanFile():

    def __init__(self, host, port, transversalState):
        # 1. Docker上のClamAV（clamd）へのネットワーク接続を確立
        self.cd = clamd.ClamdNetworkSocket(host=host, port=port)
        # 2. 起動確認（PINGを送信してPONGが返るかチェック）
        if not self.cd.ping() == "PONG":
            LOG.error("Failed to connect to the ClamAV server.", transversalState)
    
    
    def scan_file_via_clamav(self, file_path: str, transversalState:TransversalState):
        # 3. ファイルをバイナリストリームとしてコンテナに送信し、スキャンを実行
        result =  self.cd.instream(open(file_path, "rb"))
        # 4. 結果の解析
        # 戻り値の例: {'stream': ('OK', None)} または {'stream': ('FOUND', 'Eicar-Test-Signature')}
        status, virus_name = result["stream"]
        if status == "OK":                
            LOG.info(f"[Safe] No viruses were detected. ({file_path})", transversalState)
        elif status == "FOUND":
            os.remove(file_path)
            LOG.error(f"[Danger] Virus detected! Threat name: {virus_name} ({file_path})", transversalState)
        else:
            os.remove(file_path)
            LOG.error(f"[Unknown] Could not determine the scan result: {result}", transversalState)                
        return status


