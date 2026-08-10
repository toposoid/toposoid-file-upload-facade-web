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



import tempfile
from charset_normalizer import from_bytes
import io
import os
import shutil
import magic
from model import TableFileType
from xls2xlsx import XLS2XLSX
import pandas as pd
import csv

class TableAdmin():
    
    def checkFileType(self, filename):
        # ファイルが存在するか確認
        if not os.path.isfile(filename):
            raise FileNotFoundError
        # filetypeライブラリでファイルの種類を推測
        mime = magic.from_file(filename, mime=True)
        if mime is None:
            return TableFileType.NOT_APPLICABLE
        # MIMEタイプから分類
        if mime == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return TableFileType.EXCEL 
        elif mime == 'application/vnd.ms-excel':
            return TableFileType.EXCEL_OLD
        elif mime.startswith('text/'):
            return TableFileType.TEXT
        else:
            return TableFileType.NOT_APPLICABLE

    def convert(self, filename, id):
        
        tableFileType = self.checkFileType(filename)        

        #このファイルがExcelファイルかテキストファイルかを見分ける
        if tableFileType == TableFileType.EXCEL:    
            ext = filename.split(".")[-1]        
            if not ext == "xlsx":
                #ファイルをリネームして返す
                shutil.move(filename, f"tmp/{id}.xlsx")    
            return f"{id}.xlsx"      

        if tableFileType == TableFileType.EXCEL_OLD:
            #ファイルフォーマットをxlsxに変換
            x2x = XLS2XLSX(filename)
            #ファイルをリネームして返す
            x2x.to_xlsx(f"tmp/{id}.xlsx")
            return f"{id}.xlsx"      
            
        elif tableFileType == TableFileType.TEXT:            
            with open(filename, 'rb') as f:
                data = f.read() #バイトデータで読み込む
            # 2. tempfile で一時ファイルを作成し、読み込む
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                # バイト列をファイルに書き込む
                tmp.write(data)    
                # 読み込みのためにファイルポインタを先頭に戻す
                tmp.seek(0)    
                # 一時ファイルの中身を読み込む
                content = tmp.read()
                res = from_bytes(
                    content,
                    cp_isolation=['cp932','shift-jis','utf-8', 'ascii', 'windows-1252', 'iso-8859-1', 'iso-8859-9', 'macroman', 'utf-8-sig']
                )                    
            byte_stream = io.BytesIO(content)
            text_stream = io.TextIOWrapper(byte_stream, encoding=res.best().encoding if res.best() is not None else 'utf-8', errors='ignore')        
            tableFilename = f'tmp/{id}.txt'
            #削除
            os.remove(filename)
            #UTF8にコンバート            
            with open(tableFilename, 'w', encoding='utf-8') as f:
                f.write(text_stream.read())
            if self.isTablefile(tableFilename):
                #区切り文字を文字を自動判定
                #with open(tableFilename, 'r', encoding='utf-8') as f:
                #    # 先頭の1024バイトから区切り文字を推測
                #    dialect = csv.Sniffer().sniff(f.read(1024))            
                #df = pd.read_csv(tableFilename, sep=dialect.delimiter)
                df = pd.read_csv(tableFilename, sep=None, engine='python')

                # タブ区切り（sep='\t'）でファイルに出力
                df.to_csv(f"tmp/{id}.tsv", sep='\t', index=False)  
                #削除
                os.remove(tableFilename)
                return f"{id}.tsv"
            else:
                return ""
        else:
            return ""

    def isTablefile(self, filename):
        #区切り文字を文字を自動判定
        with open(filename, 'r', encoding='utf-8') as f:
            #先頭の1024バイトから区切り文字を推測
            dialect = csv.Sniffer().sniff(f.read(1024))            
            
        if dialect.delimiter in [",", "\t", " ", "|", ":", ";"]:
            return True
        else:
            return False
        
        #行ごとに区切り文字をカウントする
        """
        #下記では、プログラムファイルなどが検知できないケースがある。
        with open(filename, 'r', encoding='utf-8') as f:
            header_count = 0
            row_count = 0
            delimiter_counts = []
            for line in f:
                if row_count == 0:
                    header_count = line.count(dialect.delimiter)
                else:
                    delimiter_counts.append(header_count - line.count(dialect.delimiter))

                row_count += 1

            print(delimiter_counts)
        """
