FROM python:3.12.3-slim

# rootユーザーの切り替え
USER root
# 作業ディレクトリ
WORKDIR /gaze_estimation

# 必要パッケージのインストール
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    libgl1 \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# pythonライブラリのインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ファイルコピー
COPY . .

# モデルのダウンロード
RUN bash model_downloader.sh

# 視線推定の実行(固定項目)
ENTRYPOINT ["python3", "./project/main.py"]