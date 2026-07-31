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

from pydantic import BaseModel, model_validator
from typing import List, Any
from enum import Enum
import json
from fastapi import Form
from ToposoidCommon.model import StatusInfo

class TableFileType(Enum):
    NOT_APPLICABLE = 0
    TEXT = 1
    EXCEL = 2
    EXCEL_OLD = 3

class UploadStatusType(Enum):
    UNSPECIFIED = 0
    OK = 1
    FOUND_INFECTED_FILE = 2
    SCAN_ERROR = 3
    FILE_FORMAT_ERROR = 4
    CONVERT_ERROR = 5
    TRANSFER_ERROR = 6 
    SYSTEM_ERROR = -1

class UploadContentContext(BaseModel):
    featureType: int
    url: str

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, data: Any) -> Any:
        if isinstance(data, str):
            return json.loads(data)
        return data

    # 💡 フォームデータからこのモデルを生成するためのヘルパー関数を追加
    @classmethod
    def as_form(
        cls,
        featureType: int = Form(...),
        url: str = Form("")
    ):
        return cls(featureType=featureType, url=url)

class UploadResult(BaseModel):
    id: str
    url: str 
    status: int
