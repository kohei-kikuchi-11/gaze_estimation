# bash

OUTPUT_DIR="output"
mkdir -p $OUTPUT_DIR

rm -rf ${OUTPUT_DIR}/*

# コンテナ起動 -d バックグラウンド実行 --input "$1" スクリプト因数をPythonに渡す。
CONTAINER_ID=$(docker compose run -d gaze_estimation --input "$1")

echo "Container ID: $CONTAINER_ID"

# 終了時に削除
trap "docker rm -f $CONTAINER_ID 2>/dev/null" EXIT

# コンテナ終了待ち
docker wait $CONTAINER_ID

echo "Processing finished. Copying files..."

# コンテナ内の出力をoutputの中身だけコピー
docker cp ${CONTAINER_ID}:/gaze_estimation/output/. $OUTPUT_DIR

echo "Done!"