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
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
from ToposoidCommon.model import StatusInfo, TransversalState
from fastapi.encoders import jsonable_encoder
import ToposoidCommon as tc
LOG = tc.LogUtils(__name__)

"""
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:            
            transversalState = TransversalState.parse_raw(request.headers.get("X_TOPOSOID_TRANSVERSAL_STATE", "").replace("'", "\""))
            response: Response = await call_next(request)
            if response.status_code != 200:
                LOG.error(traceback.format_exc(), transversalState)
                response = JSONResponse(content=jsonable_encoder(StatusInfo(status="ERROR", message=traceback.format_exc())))
        except Exception as e:
            ambiguousTransversalState = TransversalState(userId="ambiguous", username="", roleId=0, csrfToken = "")
            LOG.error(traceback.format_exc(), ambiguousTransversalState)
            response = JSONResponse(content=jsonable_encoder(StatusInfo(status="ERROR", message=traceback.format_exc())))
        return response
"""

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 💡 アンダースコアとハイフンの両方に対応してヘッダを取得
        header_value = request.headers.get("X_TOPOSOID_TRANSVERSAL_STATE") or request.headers.get("X-TOPOSOID-TRANSVERSAL-STATE") or ""
        
        try:            
            # ヘッダが存在する場合のみパースを試みる
            if header_value:
                transversalState = TransversalState.parse_raw(header_value.replace("'", "\""))
            else:
                transversalState = TransversalState(userId="ambiguous", username="", roleId=0, csrfToken="")
                
            response: Response = await call_next(request)

            #print("詳細なエラー内容:", response.json())
            # 💡 call_nextの後にエラーログを残す場合、ここではまだ例外が発生していないため
            # traceback.format_exc() ではなく、ステータスコードに応じたメッセージを出す必要があります
            if response.status_code != 200:
                LOG.error(f"Request failed with status code {response.status_code}", transversalState)
                # 注: 正常な422エラー（バリデーション失敗）の場合も、ここで上書きされてしまう点に注意してください
                # もしFastAPI標準の422エラー画面をテストで見たい場合は、一時的にこのifブロックをコメントアウトすると確認しやすいです

                # 💡 422エラーの詳細（bodyの中身）を安全にパースしてログに出すデバッグコード
                if response.status_code == 422:
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    # 読み直せるようにレスポンスを再構築
                    from fastapi.responses import Response
                    response = Response(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )
                    LOG.error(f"★422エラーの真の原因:{body.decode('utf-8')}", transversalState)
                    
                response = JSONResponse(content=jsonable_encoder(StatusInfo(status="ERROR", message=f"Status {response.status_code}")), status_code=response.status_code)
                
        except Exception as e:
            # 💡 本当にコード内で例外（ランタイムエラー）が発生した場合のみここに入る
            ambiguousTransversalState = TransversalState(userId="ambiguous", username="", roleId=0, csrfToken="")
            LOG.error(traceback.format_exc(), ambiguousTransversalState)
            response = JSONResponse(content=jsonable_encoder(StatusInfo(status="ERROR", message=traceback.format_exc())), status_code=500)
            
        return response