# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN apt update && apt install -y build-essential libsndfile1 ffmpeg
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
