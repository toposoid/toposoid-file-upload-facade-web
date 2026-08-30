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


from fastapi import FastAPI, File, UploadFile, Header, Body, Form, Depends
from ToposoidCommon.model import StatusInfo, TransversalState
from ToposoidCommon.constants import FeatureType
from model import UploadContentContext, UploadResult, UploadStatusType
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import parse_obj_as

import os
import traceback
from middleware import ErrorHandlingMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import uuid
import ToposoidCommon as tc
#from ElasiticMQUtils import sendMessage
from ScanFile import ScanFile
from RawDataAdmin import RawDataAdmin
from ImageAdmin import ImageAdmin
from TableAdmin import TableAdmin
import requests

LOG = tc.LogUtils(__name__)
#TOPOSOID_MQ_DOCUMENT_ANALYSIS_QUENE = os.environ["TOPOSOID_MQ_DOCUMENT_ANALYSIS_QUENE"]

app = FastAPI(
    title="toposoid-file-upload-facade-web",
    version="0.7-SNAPSHOT"
)
app.add_middleware(ErrorHandlingMiddleware)
rawDataAdmin = RawDataAdmin()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

rawDataAdmin = RawDataAdmin()

@app.post("/upload")
async def upload(uploadContentContext:UploadContentContext= Depends(UploadContentContext.as_form), uploadfile: UploadFile | None = None, X_TOPOSOID_TRANSVERSAL_STATE: Optional[str] = Header(None, convert_underscores=False)):       
    transversalState = TransversalState.parse_raw(X_TOPOSOID_TRANSVERSAL_STATE.replace("'", "\""))
    id = str(uuid.uuid1())
    uploadStatus = UploadStatusType.UNSPECIFIED.value 
    try:        
        scanFile = ScanFile(os.environ["TOPOSOID_FILESCAN_HOST"], int(os.environ["TOPOSOID_FILESCAN_PORT"]), transversalState)        
        savePath = f"tmp/{id}" 
        status = ""
        if uploadfile is None:
            rawDataAdmin.getRawData(id, None, uploadContentContext.url, savePath)               
        else:
            #2026/07現在、一つだけファイルは送られてくる想定
            rawDataAdmin.getRawData(id, uploadfile.file, uploadfile.filename, savePath)                                    

        status = scanFile.scan_file_via_clamav(savePath, transversalState)
        if status == "OK":                            
            targetFile = ""
            #ファイルコンバート
            if uploadContentContext.featureType == FeatureType.IMAGE.value:
                imageAdmin = ImageAdmin()
                targetFile = imageAdmin.convertJpeg(savePath, id, transversalState)
                
            elif uploadContentContext.featureType == FeatureType.TABLE.value:
                tableAdmin = TableAdmin()
                targetFile = tableAdmin.convert(savePath, id, transversalState)

            elif uploadContentContext.featureType == FeatureType.DOCUMENT.value:
                #何もしない
                targetFile = f"{id}.pdf"            
                shutil.move(savePath, f"tmp/{targetFile}")                
            else:
                uploadStatus = UploadStatusType.FILE_FORMAT_ERROR.value
                return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url="", status=uploadStatus)))        
                
            if not targetFile == "":
                #toposoid-contents-adminにファイル移動
                url =  f"http://{os.environ['TOPOSOID_CONTENTS_ADMIN_HOST']}:{os.environ['TOPOSOID_CONTENTS_ADMIN_PORT']}/transferFile"
                with open(f"tmp/{targetFile}", 'rb') as f:
                    # (ファイル名, ファイルオブジェクト, Content-Type) の順に指定可能
                    files = {'uploadfile': (targetFile, f)}         
                    requestHeaders = {'X_TOPOSOID_TRANSVERSAL_STATE': X_TOPOSOID_TRANSVERSAL_STATE}   
                    transferResponse = requests.post(url, files=files, headers=requestHeaders)  
                    statusInfo = parse_obj_as(StatusInfo, transferResponse.json())
                if statusInfo.status == "OK":
                    url = os.environ["TOPOSOID_CONTENTS_URL"] + "temporaryUse/" + targetFile
                    uploadStatus = UploadStatusType.OK.value 
                    LOG.info(f"File upload completed.[url:{url}", transversalState)
                    return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url=url, status=uploadStatus)))                            
                else:
                    uploadStatus = UploadStatusType.TRANSFER_ERROR.value
                    return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url="", status=uploadStatus)))        
            else:
                uploadStatus = UploadStatusType.FILE_FORMAT_ERROR.value
                return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url="", status=uploadStatus)))        

        elif status == "FOUND":
            uploadStatus = UploadStatusType.FOUND_INFECTED_FILE.value
            return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url="", status=uploadStatus)))        
        else:
            uploadStatus = UploadStatusType.SCAN_ERROR.value
            return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url="", status=uploadStatus)))       

    except Exception as e:
        LOG.error(traceback.format_exc(), transversalState)
        return JSONResponse(content=jsonable_encoder(UploadResult(id=id, url=url, status=UploadStatusType.SYSTEM_ERROR.value)))
        


