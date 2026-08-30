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
from itertools import islice
import ToposoidCommon as tc
LOG = tc.LogUtils(__name__)

class TableAdmin():


    """
    def saveTablePermanently(self, knowledgeForTable:KnowledgeForTable, isTemporaryUse = False):
        #既にtemporaryUseに保存されていることが前提                
        ext = "." + knowledgeForTable.tableReference.reference.url.split(".")[-1]
        #保存
        if not isTemporaryUse:
            #オリジナルファイルも含めてコピー
            for target in glob.glob("contents/temporaryUse/%s.*" % (knowledgeForTable.id)):
                shutil.copy(target, "contents/tables/")                    
            knowledgeForTable.tableReference.reference.url = os.environ["TOPOSOID_CONTENTS_URL"] + "tables/" + knowledgeForTable.id + ext                    
        return knowledgeForTable
    """
    
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

    def convert(self, filename, id, transversalState):
        
        tableFileType = self.checkFileType(filename)        

        #このファイルがExcelファイルかテキストファイルかを見分ける
        if tableFileType == TableFileType.EXCEL:    
            ext = filename.split(".")[-1]        
            if not ext == "xslx":
                #ファイルをリネームして返す
                shutil.move(filename, f"tmp/{id}.xslx")    
            return f"{id}.xslx"      

        if tableFileType == TableFileType.EXCEL_OLD:
            #ファイルフォーマットをxslxに変換
            x2x = XLS2XLSX(filename)
            #ファイルをリネームして返す
            x2x.to_xlsx(f"tmp/{id}.xslx")
            return f"{id}.xslx"      
            
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

            return self.analyzeTablefile(id, tableFilename,  transversalState)
        else:
            return ""

    def checkDelimter(self, lines, divideNum):
        num_lines = len(lines)
        # サンプルをdivideNumで分割した真ん中で評価
        start = int(divideNum/2) * int(num_lines / divideNum)
        end = (int(divideNum/2) + 1) * int(num_lines / divideNum)                    
        # start と end が同じ、または逆転しないよう最低1行は確保
        if start >= end:
            end = start + 1                
        # 文字列のリストを1つの文字列に結合
        target_text = "".join(lines[start:end])                    
        # 3. csv.Sniffer に文字列を渡して推測
        dialect = csv.Sniffer().sniff(target_text)  
        if dialect.delimiter in [",", "\t", " ", "|", ":", ";"]:
            return max(len(line.split(dialect.delimiter)) for line in lines[start:end])
        else:
            raise Exception("Unexpected delimiter.")                                              

    def forceOuputTsv(self, lines, filename, transversalState):
        target_text = "".join(lines)                 
        dialect = csv.Sniffer().sniff(target_text)                                                
        if dialect.delimiter in [",", "\t", " ", "|", ":", ";"]:
            max_cols = max(len(line.split(dialect.delimiter)) for line in lines)
        else:
            LOG.error("Unexpected delimiter.", transversalState)
            return ""        
        col_names = list(range(max_cols))        
        df = pd.read_csv(filename, header=None, names=col_names) 
        df.to_csv(f"tmp/{id}.tsv", sep='\t', index=False, header=False)  
        return f"{id}.tsv"

    def analyzeTablefile(self, id, filename, transversalState):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                # 1. すべての行をリストに読み込む（行数カウントとデータ取得を同時に行う）
                lines = f.readlines()
                
            if len(lines) > 2:
                try:
                    max_cols = self.checkDelimter(lines, 3)
                    col_names = list(range(max_cols))
                    df = pd.read_csv(filename, header=None, names=col_names) 
                    df.to_csv(f"tmp/{id}.tsv", sep='\t', index=False, header=False) 
                    return f"{id}.tsv" 
                except:
                    if len(lines) > 4:
                        max_cols = self.checkDelimter(lines, 5)
                        col_names = list(range(max_cols))
                        df = pd.read_csv(filename, header=None, names=col_names) 
                        df.to_csv(f"tmp/{id}.tsv", sep='\t', index=False, header=False) 
                        return f"{id}.tsv" 
                    else:
                        return self.forceOuputTsv(lines, filename, transversalState)                
            else:
                return self.forceOuputTsv(lines, filename, transversalState)

        except Exception as e:
            LOG.error(e, transversalState)
            return ""
