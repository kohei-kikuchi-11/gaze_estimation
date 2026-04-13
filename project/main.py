# main.py
# 視線推定を実行する
import argparse
import cv2
import subprocess
from pathlib import Path

from pipeline import GazePipeline

def parse_args():
    '''
    cliで指定できるようにする
    --input...入力動画パス
    --output...出力動画パス
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",type=str,required=True,help="入力動画パス")
    return parser.parse_args()

def convert_to_h264(input_path, output_path):
    '''
    動画をmpegからh264へエンコードする。
    -y: 既存ファイルがあっても強制的に上書き
    -i input_path: 変換元のファイルパス
    -vcodec libx264 -pix_fmt yuv420p:動画をh.264コーデックにし、色空間を指定する
    -acodec aac :音声をaacコーデックに指定する
    '''
    print(f"H.264へエンコード中:{output_path}")
    command = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-acodec", "aac", str(output_path)
    ]
    # ffmpegを同期的に実行し、不要な出力を抑える
    # stdout=subprocess.DEVNULL:標準出力をnullにする stderr=subprocess.STDOUT:エラー出力もnullにする
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("エンコード完了")

def main():
    args = parse_args()

    cap = None
    out = None

    # 出力先設定
    base_dir  = Path(__file__).resolve().parent.parent # gaze_esitmationディレクトリ
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True, parents=True)

    # 出力ファイル名設定
    base_name = Path(args.input).stem
    final_output = output_dir / f"{base_name}.mp4"
    temp_output = output_dir / f"temp_{base_name}.mp4"

    try:
        cap = cv2.VideoCapture(args.input)

        if not cap.isOpened():
            print("動画を開けません:",args.input)
            return
        else:
            print("動画読み込み成功")

        # 動画情報取得
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"fps={fps}, size=({width},{height})")

        # 保存設定
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(temp_output), cv2.CAP_FFMPEG, fourcc, fps, (width, height))

        if not out.isOpened():
            print("VideoWriter作成失敗:", temp_output)
            return
        else:
            print("VideoWriter作成成功:", temp_output)

        # 色の設定(GBR)
        green, blue, yellow, red = (0, 255, 0), (255, 0, 0), (0, 255, 255), (0, 0, 255)
        #  モデルパスを設定
        pipeline = GazePipeline({
        "face": "./intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml",
        "landmark": "./intel/facial-landmarks-35-adas-0002/FP16/facial-landmarks-35-adas-0002.xml",
        "headpose": "./intel/head-pose-estimation-adas-0001/FP16/head-pose-estimation-adas-0001.xml",
        "gaze": "./intel/gaze-estimation-adas-0002/FP16/gaze-estimation-adas-0002.xml"
        })

        frame_count = 0
        while True:
                    
            ret, frame = cap.read()
            if not ret:
                print("frame読み取り完了")
                break
            
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"processing frame: {frame_count}")

            results = pipeline.process_frame(frame)

            for r in results:
                xmin, ymin, xmax, ymax = r["face"]
                gaze_vec = r["gaze"].flatten()

                # pipelineから取得する
                conf = r.get("face_conf",0.0)
                landmarks = r.get("landmarks", [])
                yaw, pitch, roll = r.get("head_pose",[])
                left_eye = r.get("left_eye", (0,0,0,0))
                right_eye = r.get("right_eye", (0,0,0,0))

                # 顔bboxと信頼度の描画
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), green,2)
                cv2.putText(frame, f"conf:{conf:.2f}", (xmin, ymin -10), cv2.FONT_HERSHEY_DUPLEX, 1, green, 1)
                
                # ランドマークの描画
                for (lx, ly) in landmarks:
                    cv2.circle(frame, (int(lx), int(ly)), 2, yellow, -1)
                # 頭部姿勢の描画
                cv2.putText(frame, f"yaw:{yaw:.2f} pitch:{pitch:.2f} roll:{roll:.2f}",(xmin, ymax + 50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)

                #  目ROIの描画
                for eye_box in [left_eye ,right_eye]:
                    ex_min, ey_min, ex_max, ey_max = eye_box
                    # 目ROI矩形
                    cv2.rectangle(frame, (ex_min, ey_min),(ex_max, ey_max), green, 1)

                    # 目の中心座標を計算する
                    cx, cy = (ex_min + ex_max) // 2, (ey_min + ey_max) // 2

                    # 視線矢印の描画
                    end_x = int(cx + gaze_vec[0] * 100)
                    end_y = int(cy + gaze_vec[1] * 100)
                    cv2.arrowedLine(frame,(cx, cy),(end_x, end_y),blue,2)
            out.write(frame)

    finally:
        cap.release()
        out.release()
    
    temp_output_path = Path(temp_output)
    if temp_output_path.exists():
        convert_to_h264(temp_output, final_output)
        temp_output_path.unlink()
        print(f"処理完了:{final_output}を生成しました。")

if __name__ == "__main__":
    main()
