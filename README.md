# gaze_estimation実行方法

## 1. 準備
### step1
リポジトリをクローン
```
git clone https://github.com/kohei-kikuchi-11/gaze_estimation.git
```
### step2
視線推定を行いたい動画をinputディレクトリに人の顔が写っている動画を格納します。

## 2. 実行
下記コマンドを実行する。自分の動画inputのパスを書き換えて実行する。
```
bash run.sh
```

docker compose down
docker compose build --no-cache
docker compose down --remove-orphans