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

from fastapi.testclient import TestClient
from fastapi import status
from api import app
from model import UploadResult, UploadStatusType
from ToposoidCommon.model import TransversalState, StatusInfo
from ToposoidCommon.constants import FeatureType
import numpy as np
from time import sleep
import pytest
import uuid
import os
from fastapi.encoders import jsonable_encoder
#from ElasiticMQUtils import receiveMessage
from typing import List
from pydantic import parse_obj_as
import pprint
from httpx import AsyncClient, ASGITransport 
import requests
import magic
import io
import pandas as pd
from charset_normalizer import from_bytes
import csv


class TestToposoidFileUploadFacadeWeb(object):

    client = TestClient(app)
    vector = list(np.random.rand(768))
    id1 = ""
    id2 = ""
    transversalState = str(jsonable_encoder(TransversalState(userId="test-user", username="guest", roleId=0, csrfToken = "")))

    #@classmethod
    #def setup_class(cls):    
    #    cls.id1 = str(uuid.uuid4())
    #    cls.id2 = str(uuid.uuid4())

    #@classmethod
    #def teardown_class(cls):
    #    if os.path.isfile('contents/images/' + cls.id1 + ".jpeg"):
    #        os.remove('contents/images/' + cls.id1 + ".jpeg")
    #    if os.path.isfile('contents/images/' + cls.id2 + ".jpeg"):    
    #        os.remove('contents/images/' + cls.id2 + ".jpeg")
    @pytest.mark.anyio
    async def test_uploadImageUrlJpeg(self): 

        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.IMAGE.value),
                    "url": "http://images.cocodataset.org/val2017/000000039769.jpg"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200
        
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "image/jpeg")
        
    @pytest.mark.anyio
    async def test_uploadImageUrlNotJpeg(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.IMAGE.value),
                    "url": "http://localhost:8000/IMG_TEST.png"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "image/jpeg")
       

    @pytest.mark.anyio
    async def test_uploadImageFileJpeg(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/IMG_TEST.jpg", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.IMAGE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("IMG_TEST.jpg", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200     
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "image/jpeg")

    @pytest.mark.anyio
    async def test_uploadImageFileNotJpeg(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/IMG_TEST.png", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.IMAGE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("IMG_TEST.png", f)})
                    assert response.status_code == 200


        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)        
        #toposoid-contents-admin側に適切にフォルダに配置されているか？        
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "image/jpeg")

    @pytest.mark.anyio
    async def test_uploadTableUrlExcel(self):      
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST.xlsx"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @pytest.mark.anyio       
    async def test_uploadTableUrlOldExcxel(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST.xls"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @pytest.mark.anyio
    async def test_uploadTableUrlCsvUTF8(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST_UTF8.csv"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')                
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")


    @pytest.mark.anyio
    async def test_uploadTableUrlTsvUTF8(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST_UTF8.tsv"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")


    @pytest.mark.anyio
    async def test_uploadTableUrlTextUTF8(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST_UTF8.txt"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")


    @pytest.mark.anyio
    async def test_uploadTableUrlCsvSJIS(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST_SJIS.csv"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")


    @pytest.mark.anyio
    async def test_uploadTableUrlTsvSJIS(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST_SJIS.tsv"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")

    @pytest.mark.anyio
    async def test_uploadTableUrlTextSJIS(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.TABLE.value),
                    "url": "http://localhost:8000/TABLE_TEST_SJIS.txt"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")

    @pytest.mark.anyio
    async def test_uploadTableFileExcel(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST.xlsx", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST.xlsx", f)})
                    assert response.status_code == 200


        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @pytest.mark.anyio
    async def test_uploadTableFileOldText(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST.xls", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST.xls", f)})
                    assert response.status_code == 200


        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @pytest.mark.anyio
    async def test_uploadTableFileCsvUTF8(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST_UTF8.csv", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST_UTF8.csv", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")

    @pytest.mark.anyio
    async def test_uploadTableFileTsvUTF8(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST_UTF8.tsv", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST_UTF8.tsv", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")
        
    @pytest.mark.anyio
    async def test_uploadTableFileTextUTF8(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST_UTF8.txt", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST_UTF8.txt", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")

    @pytest.mark.anyio
    async def test_uploadTableFileCsvSJIS(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST_SJIS.csv", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST_SJIS.csv", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")

    @pytest.mark.anyio
    async def test_uploadTableFileTsvSJIS(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST_SJIS.tsv", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST_SJIS.tsv", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")           

    @pytest.mark.anyio
    async def test_uploadTableFileTextSJIS(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/TABLE_TEST_SJIS.txt", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("TABLE_TEST_SJIS.txt", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "text/plain")
        result = from_bytes(checkResponse.content).best()
        assert(result.encoding == 'utf_8')
        dialect = csv.Sniffer().sniff(checkResponse.content.decode("utf-8"))
        assert(dialect.delimiter == "\t")              
    
    @pytest.mark.anyio
    async def test_uploadDocumentFile(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/PDF_TEST.pdf", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.DOCUMENT.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("PDF_TEST.pdf", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())
        assert(uploadResult.status == UploadStatusType.OK.value)
        #toposoid-contents-admin側に適切にフォルダに配置されているか？
        checkResponse = requests.get(uploadResult.url, headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState})
        assert checkResponse.status_code == 200  
        #適切にコンバートされているか？
        mime_detector = magic.Magic(mime=True)
        mime = mime_detector.from_buffer(checkResponse.content)
        assert(mime == "application/pdf")

    @pytest.mark.anyio
    async def test_uploadIrregularUrl(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.IMAGE.value),
                    "url": "http://localhost:8000/IRREGULAR_TEST"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())        
        assert(uploadResult.status == UploadStatusType.FILE_FORMAT_ERROR.value)

    @pytest.mark.anyio
    async def test_uploadIrregularFile(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/IRREGULAR_TEST", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("IRREGULAR_TEST", f)})
                    assert response.status_code == 200
        
        uploadResult = UploadResult.parse_obj(response.json())        
        assert(uploadResult.status == UploadStatusType.FILE_FORMAT_ERROR.value)


    @pytest.mark.anyio
    async def test_uploadIrregularUrl2(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.IMAGE.value),
                    "url": "http://localhost:8000/TABLE_TEST_SJIS.tsv"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())        
        assert(uploadResult.status == UploadStatusType.FILE_FORMAT_ERROR.value)

    @pytest.mark.anyio
    async def test_uploadIrregularFile2(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/PDF_TEST.pdf", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("PDF_TEST.pdf", f)})
                    assert response.status_code == 200
        
        uploadResult = UploadResult.parse_obj(response.json())        
        assert(uploadResult.status == UploadStatusType.FILE_FORMAT_ERROR.value)
     

    @pytest.mark.anyio
    async def test_uploadInfectedUrl(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                data = {
                    "featureType": int(FeatureType.IMAGE.value),
                    "url": "http://localhost:8000/INFECTED_FILE_TEST"
                }

                response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data)
                assert response.status_code == 200
        
        uploadResult = UploadResult.parse_obj(response.json())        
        assert(uploadResult.status == UploadStatusType.FOUND_INFECTED_FILE.value)

        #ファイルが削除されていることを確認
        assert(not os.path.exists(f"tmp/{uploadResult.id}"))

    @pytest.mark.anyio
    async def test_uploadInfectedFile(self): 
        async with AsyncClient(
            transport = ASGITransport(app=app), base_url="http://test"
        ) as ac:
                with open("testdata/INFECTED_FILE_TEST", "rb") as f:
                    data = {
                        "featureType": int(FeatureType.TABLE.value),
                        "url": None
                    }
                    response = await ac.post(url = "http://testserver/upload", headers={"X_TOPOSOID_TRANSVERSAL_STATE": self.transversalState}, data=data, files={"uploadfile": ("INFECTED_FILE_TEST", f)})
                    assert response.status_code == 200

        uploadResult = UploadResult.parse_obj(response.json())        
        assert(uploadResult.status == UploadStatusType.FOUND_INFECTED_FILE.value)

        #ファイルが削除されていることを確認
        assert(not os.path.exists(f"tmp/{uploadResult.id}"))