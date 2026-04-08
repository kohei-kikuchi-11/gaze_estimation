# models.py
# 各モデルの入出力管理
from openvino.runtime import Core
import numpy as np
import cv2

def to_nchw(image):
    """
    入力画像(h,w,c)→(n,c,h,c)に変換する
    nはバッチ数(基本1)
    """
    image = np.transpose(image, (2, 0, 1))[np.newaxis, :]
    return image

# ベースモデル
class BaseModel:
    """
    1. モデルの読み込み
    2. 実行用に最適化(コンパイル)
    3. 入出力の取得
    4. 推論実行
    """
    def __init__(self, model_path, device="CPU"):
        self.core = Core() # openvinoのエンジンを作成
        self.model = self.core.read_model(model_path) # xmlモデルを読み込む
        self.compiled_model = self.core.compile_model(self.model, device) # モデルをコンパイル

        self.input_layer = self.compiled_model.input(0) # 入力の取得 
        self.output_layer = self.compiled_model.output(0) # 出力の取得
    
    def infer(self, inputs):
        if isinstance(inputs, dict):
            result = self.compiled_model(inputs)
        else:
            result = self.compiled_model([inputs])
        return {out.any_name: result[out] for out in self.compiled_model.outputs} # 出力が複数あっても対応する

# 顔検出クラス
class FaceDetector(BaseModel):
    """
    入力:(n,c,h,w) 色の順序はBGR
    出力:正規化済み(1,1,200,7) 200は最大検出bbox数  検出結果は[image_id, label, conf, x_min, y_min, x_max, y_max] 
    """
    def preprocess(self,frame):
        """
        入力サイズ取得、リサイズ、nchw変換
        """
        input_shape = self.input_layer.shape
        resized = cv2.resize(frame, (input_shape[3], input_shape[2]))
        input_blob = to_nchw(resized)

        return input_blob

    def postprocess(self,outputs, frame, conf_th=0.9):
        """
        信頼度が0.9を超えるものだけを保存する
        """
        h, w = frame.shape[:2]
        faces = []
        
        dets = outputs["detection_out"]
        dets = dets.reshape(-1, 7)
        for det in dets: # (1,1,200,7)→(200,7)
            conf = det[2]
            if conf > conf_th:
                xmin = int(det[3] * w)
                ymin = int(det[4] * h)
                xmax = int(det[5] * w)
                ymax = int(det[6] * h)
                faces.append((float(conf), xmin, ymin, xmax, ymax))
        return faces

# ランドマーク推定クラス
class LandmarkDetector(BaseModel):
    """
    入力:顔ROI(n,c,h,w)
    出力:正規化済み(1,70(x,y)) 0,1:左目 2,3:右目 4-7:鼻 8-11:口 12-14:左眉毛 15-17:右眉毛 18-34:輪郭
    """
    def preprocess(self, face_img):
        input_shape = self.input_layer.shape
        resized = cv2.resize(face_img, (input_shape[3], input_shape[2]))
        input_blob = to_nchw(resized)
        return input_blob
    
    def postprocess(self, outputs, face_img):
        h, w = face_img.shape[:2]
        landmarks = outputs["align_fc3"] # OVDictから取り出す
        landmarks = landmarks.reshape(-1, 2) # (1,70)→(35,2)
        

        coords = []
        for (x, y) in landmarks:
            coords.append((int(x * w), int(y * h)))
        return coords

# 頭部推定クラス
class HeadPoseEstimator(BaseModel):
    
    """
    入力:顔ROI(n,c,h,w)
    出力: yaw:fc_y(1,1), pitch:fc_p(1,1), roll:fc_r(1,1)
    yaw:横を向く, pitch:上下を見る, roll:首を傾ける
    """
    def preprocess(self, face_img):
        input_shape = self.input_layer.shape
        resized = cv2.resize(face_img, (input_shape[3], input_shape[2]))
        input_blob = to_nchw(resized)
        return input_blob
    
    def postprocess(self, outputs):
        yaw =float(outputs["angle_y_fc"].item())
        pitch = float(outputs["angle_p_fc"].item())
        roll = float(outputs["angle_r_fc"].item())

        return yaw, pitch, roll

# 視線推定クラス
class GazeEstimation(BaseModel):
    def preprocess(self, left_eye, right_eye, head_pose):
        """
        左目、右目、頭部姿勢の入力を作成する

        """
        # 目画像
        le = to_nchw(cv2.resize(left_eye, (60, 60)))
        re = to_nchw(cv2.resize(right_eye, (60, 60)))

        hp = np.array(head_pose).reshape(1, 3)

        return {
            "left_eye_image": le,
            "right_eye_image": re,
            "head_pose_angles": hp
        }
    
    def postprocess(self, outputs):
        return outputs["gaze_vector"].flatten()

