#!/bin/bash

cd /app/toposoid-file-upload-facade-web
uvicorn api:app --reload --host 0.0.0.0 --port 9024