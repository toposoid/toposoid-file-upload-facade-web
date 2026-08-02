#!/bin/bash

cd /app/toposoid-common-image-recognition-web
uvicorn api:app --reload --host 0.0.0.0 --port 9024