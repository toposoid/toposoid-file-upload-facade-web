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

import cv2
import os
import ToposoidCommon as tc
import traceback

LOG = tc.LogUtils(__name__)

class ImageAdmin():
    
    def convertJpeg(self, filename, id, transversalState):
        try:
            # 画像読み込み        
            image = cv2.imread(filename)
            jpegFilename = 'tmp/' + id + ".jpg"
            #JPEGに変換
            cv2.imwrite(jpegFilename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])            
            return id + ".jpg"
        except:
            LOG.error(traceback.format_exc(), transversalState)
            return ""


"""
    def registImage(self, knowledgeForImage:KnowledgeForImage, isTemporaryUse = False):
        #with open('tmp/' + knowledgeForImage.id, 'wb') as f:
        #    f.write(response.content)
        
        # 画像フォーマットを取得
        fmt = imghdr.what('tmp/' + knowledgeForImage.id)

        #保存
        if knowledgeForImage.imageReference.reference.isWholeSentence:
            if isTemporaryUse:
                shutil.move('tmp/' + knowledgeForImage.id, 'contents/temporaryUse/' + knowledgeForImage.id + "-org." + fmt)
                image = cv2.imread('contents/temporaryUse/' + knowledgeForImage.id + "-org." + fmt)
                #JPEGに変換
                cv2.imwrite('contents/temporaryUse/' + knowledgeForImage.id + ".jpg" , image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]) 
            else:
                shutil.move('tmp/' + knowledgeForImage.id, 'contents/images/' + knowledgeForImage.id + "-org." + fmt)
                image = cv2.imread('contents/images/' + knowledgeForImage.id + "-org." + fmt)
                #JPEGに変換
                cv2.imwrite('contents/images/' + knowledgeForImage.id + ".jpg" , image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]) 
        else:
            # テンポラリファイル名変更
            os.rename('tmp/' + knowledgeForImage.id, 'tmp/' + knowledgeForImage.id + "." + fmt)

            image = cv2.imread('tmp/' + knowledgeForImage.id + "." + fmt)            
            #加工
            x = knowledgeForImage.imageReference.x
            y = knowledgeForImage.imageReference.y
            w = knowledgeForImage.imageReference.width
            h = knowledgeForImage.imageReference.height
            
            if isTemporaryUse:
                #元画像
                cv2.imwrite('contents/temporaryUse/' + knowledgeForImage.id + "-org." + fmt, image[y:y+h, x:x+w])
                #JPEGに変換
                cv2.imwrite('contents/temporaryUse/' + knowledgeForImage.id + ".jpg" , image[y:y+h, x:x+w], [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            else:
                #元画像
                cv2.imwrite('contents/images/' + knowledgeForImage.id + "-org." + fmt, image[y:y+h, x:x+w])
                #JPEGに変換
                cv2.imwrite('contents/images/' + knowledgeForImage.id + ".jpg", image[y:y+h, x:x+w], [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            #削除
            os.remove('tmp/' + knowledgeForImage.id + "." + fmt)



        if isTemporaryUse:
            knowledgeForImage.imageReference.reference.url = os.environ["TOPOSOID_CONTENTS_URL"] + "temporaryUse/" + knowledgeForImage.id + ".jpg"
        else:
            knowledgeForImage.imageReference.reference.url = os.environ["TOPOSOID_CONTENTS_URL"] + "images/" + knowledgeForImage.id + ".jpg"

        return knowledgeForImage
"""