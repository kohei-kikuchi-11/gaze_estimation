FROM python:3.12.3-slim

# rootユーザーの切り替え
USER root

WORKDIR /gaze_estimtion

# 必要パッケージのインストール
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# pythonライブラリのインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# コードコピー
COPY . .

# モデルのダウンロード
RUN bash model_downloader.sh

# 視線推定の実行
ENTRYPOINT ["python3", "./project/main.py"]