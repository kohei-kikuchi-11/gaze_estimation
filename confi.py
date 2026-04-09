import cv2
import numpy as np
from openvino.runtime import Core

# モデルのパスをここで指定
model_paths = {
    "face": "./intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml",
    "landmark": "./intel/facial-landmarks-35-adas-0002/FP16/facial-landmarks-35-adas-0002.xml",
    "headpose": "./intel/head-pose-estimation-adas-0001/FP16/head-pose-estimation-adas-0001.xml",
    "gaze": "./intel/gaze-estimation-adas-0002/FP16/gaze-estimation-adas-0002.xml"
}

# -----------------------
# ヘルパー関数
# -----------------------
def to_nchw(image):
    return np.transpose(image, (2,0,1))[np.newaxis,:]

# -----------------------
# モデル読み込み
# -----------------------
core = Core()

face_model = core.read_model(model_paths["face"])
face_compiled = core.compile_model(face_model, "CPU")
lm_model = core.read_model(model_paths["landmark"])
lm_compiled = core.compile_model(lm_model, "CPU")
hp_model = core.read_model(model_paths["headpose"])
hp_compiled = core.compile_model(hp_model, "CPU")
gaze_model = core.read_model(model_paths["gaze"])
gaze_compiled = core.compile_model(gaze_model, "CPU")

# -----------------------
# 動画 or カメラ
# -----------------------
cap = cv2.VideoCapture("/home/kk06/workspace/tmp/IMG_2531.mp4")  # 動画の場合

ret, frame = cap.read()
cap.release()

if not ret:
    raise RuntimeError("フレームを取得できませんでした")

# -----------------------
# 1. 顔検出
# -----------------------
face_input = cv2.resize(frame, (face_compiled.input(0).shape[3], face_compiled.input(0).shape[2]))
face_input = to_nchw(face_input)
face_out = face_compiled([face_input])
print("=== Face Detection Output ===")
print("type:", type(face_out))
if not isinstance(face_out, dict):
    for k,v in face_out.items():
        print(f"key: {k}, shape: {v.shape}, dtype: {v.dtype}")

# -----------------------
# 2. ランドマーク
# -----------------------
face_img = frame[0:100,0:100]  # 適当に顔領域を切り出し
lm_input = cv2.resize(face_img, (lm_compiled.input(0).shape[3], lm_compiled.input(0).shape[2]))
lm_input = to_nchw(lm_input)
lm_out = lm_compiled([lm_input])
print("\n=== Landmark Output ===")
print("type:", type(lm_out))
if not isinstance(lm_out, dict):
    for k,v in lm_out.items():
        print(f"key: {k}, shape: {v.shape}, dtype: {v.dtype}")

# -----------------------
# 3. Head Pose
# -----------------------
hp_input = cv2.resize(face_img, (hp_compiled.input(0).shape[3], hp_compiled.input(0).shape[2]))
hp_input = to_nchw(hp_input)
hp_out = hp_compiled([hp_input])
print("\n=== Head Pose Output ===")
print("type:", type(hp_out))
if not isinstance(hp_out, dict):
    for k,v in hp_out.items():
        print(f"key: {k}, shape: {v.shape}, dtype: {v.dtype}")

# -----------------------
# 4. Gaze Estimation
# -----------------------
# 左右目画像を仮に顔画像から切り出し
le = to_nchw(face_img[0:60,0:60])
re = to_nchw(face_img[0:60,0:60])
hp_angles = np.array([[0,0,0]], dtype=np.float32)  # 仮の頭部角度
gaze_out = gaze_compiled({"left_eye_image": le, "right_eye_image": re, "head_pose_angles": hp_angles})
print("\n=== Gaze Estimation Output ===")
print("type:", type(gaze_out))
if not isinstance(gaze_out, dict):
    for k,v in gaze_out.items():
        print(f"key: {k}, shape: {v.shape}, dtype: {v.dtype}")

# === Face Detection Output ===
# type: <class 'openvino.runtime.utils.data_helpers.wrappers.OVDict'>
# key: <ConstOutput: names[detection_out] shape[1,1,200,7] type: f32>, shape: (1, 1, 200, 7), dtype: float32

# === Landmark Output ===
# type: <class 'openvino.runtime.utils.data_helpers.wrappers.OVDict'>
# key: <ConstOutput: names[align_fc3] shape[1,70] type: f32>, shape: (1, 70), dtype: float32

# === Head Pose Output ===
# type: <class 'openvino.runtime.utils.data_helpers.wrappers.OVDict'>
# key: <ConstOutput: names[fc_r, angle_r_fc] shape[1,1] type: f32>, shape: (1, 1), dtype: float32
# key: <ConstOutput: names[fc_p, angle_p_fc] shape[1,1] type: f32>, shape: (1, 1), dtype: float32
# key: <ConstOutput: names[fc_y, angle_y_fc] shape[1,1] type: f32>, shape: (1, 1), dtype: float32

# === Gaze Estimation Output ===
# type: <class 'openvino.runtime.utils.data_helpers.wrappers.OVDict'>
# key: <ConstOutput: names[gaze_vector] shape[1,3] type: f32>, shape: (1, 3), dtype: float32


## 0. はじめに
2025年10月入社の菊池紘平と申します。アサイン中に業務で使用したOpenVINOを使った視線推定について備忘録を兼ねて再現をしてみたいと思います。

## 1. OpenVINOとは
OpenVINOとは、Intelが開発したAIモデルを“速く・軽く動かすための推論最適化ツールで、正式名称をOpen Visual Inference & Neural Network Optimizationといいます。
### できること
モデルの変換
PyTorch / TensorFlow → OpenVINO形式（IR形式）に変換　
推論の高速化
	•	CPU / GPU / VPUで最適に実行
	•	特にCPUがめちゃ速くなる（Intel製だとさらに強い）
③ 軽量化
	•	モデルサイズ削減
	•	推論時間短縮

使用例:
	•	カメラ映像をリアルタイム処理したい
	•	GPUなし環境で動かしたい
	•	エッジデバイス（PC・組み込み）で動かしたい

PyTorchでモデルを作ってOpenVINOで変換して軽量化、最速化して実行する

## 2. 視線推定の流れ
```参考ページ
[視線推定デモ]https://www.isus.jp/wp-content/uploads/openvino/2024/docs/omz_demos_gaze_estimation_demo_cpp.html
```

1. 与えられた動画または画像から顔を検出し、顔ROI(Region of Interest)を切り出す
ROI(Region of Interest)とは?
画像または動画の中で特に注目して、処理や分析を行いたい部分のこと。

2. 顔ROIからランドマーク(目、鼻、口、眉毛、輪郭)推定する

3. 頭部姿勢推定をする

4. 目の座標と頭部姿勢から視線推定を行う。

## 3. 実行例
使用モデル:











