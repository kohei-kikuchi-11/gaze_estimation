# bash
mkdir -p ./output
sudo chown 1000:1000 ./output
chmod 775 ./output
docker compose run gaze_estimation --input input/36510_1280x720.mp4