from openvino.runtime import Core
import numpy as np
import cv2

def to_nchw(image):
    """入力画像(h,w,c)→(n,c,h,c)に変換する
    """
    image = np.transpose(image, (2, 0, 1))[np.newaxis, :]
    return image

# ベースモデル
class BaseModel:
    def __init__(self, model_path, device="CPU")
        self.core = Core()
        self.model = self.core.read_model(model_path)
        self.compiled_model = self.compiled_model(self.model, device)

        self.input_layer = self.compiled_model.input(0)
        self.output_layer = self.compiled_model.output(0)
    
    def infer(self, input_data)
        return self.compiled_model([input_data])[self.output_layer]

# 顔検出クラス
class FaceDetector(BaseModel):
    def preprocess(self,frame):
        input_shape = self.input_layer.shape
        resized = cv2.resize(frame, (input_shape[3], input_shape[2]))
        input_blob = to_nchw(resized)

        return input_blob
    #  outputs=[image_id, label, conf, x_min, y_min, x_max, y_max] shape(1,1,200,7)→200,7
    def postprocess(self,outputs, frame, conf_th=0.9):
        h, w = frame.shape[:2]
        faces = []

        for det in outputs[0][0]:
            conf = det[2]
            if conf > conf_th:
                xmin = int(det[3] * w)
                ymin = int(det[4] * h)
                xmax = int(det[5] * w)
                ymax = int(det[6] * h)
            faces.append((xmin,ymin, xmax, ymax))
        return faces

# ランドマーク推定クラス
class LandmarkDetector(BaseModel):
    def preprocess(self, face_img):
        input_shape = self.input_layer.shape
        resized = cv2.resize(face_img, (input_shape[3], input_shape[2]))
        inpout_blob = to_nchw(resized)
        return inpout_blob
    
    def postprocess(self, outputs, face__img):
        h, w = face_img.shape[:2]
        landmarks = outputs.reshape(-1, 2)

        coords = []
        for (x, y) in landmarks:
            coords.append((int(x * w), int(y * h)))
        return coords

# 頭部推定クラス
class HeadPoseEstimator(BaseModel):
    def postprocess(self, outputs):
        yaw = outputs["angle_y_fc"][0][0]
        pitch = outputs["angle_p_fc"][0][0]
        roll = outputs["angle_t_fc"][0][0]

        return yaw, pitch, roll

# 視線推定クラス
class GazeEstimation(BaseModel):
    def preprocess(self, left_eye, right_eye, head_pose):
        # 目画像
        le = to_nchw(cv2.resize(left_eye, (60, 60)))
        re = to_nchw(cv2.resize(right_eye, (60, 60)))

        hp = np.array(head_pose).reshape(1, 3)

        return {
            "left_eye_image": le,
            "right_eye_image": re,
            "head_pose_angles": hp
        }
    
    def infer(self, inputs):
        return self.compiled_model(inputs)
    
    def postprocess(self, outputs):
        return outputs[self.output_layer][0]

# パイプライン本体
import cv2

class GazePipeline:
    def __init__(self, model_paths):
        self.face = FaceDetector(model_paths["face"])
        self.landmark = LandmarkDetector(model_paths["landmark"])
        self.headpose = HeadPoseEstimator(model_paths["headpose"])
        self.gaze = GazeEstimation(model_paths["gaze"])
    
    def process_frame(self, frame):
        # Face Detection
        face_input = self.face.preprocess(frame)
        face_out = self.face.infer(face_input)
        faces = self.face.postprocess(face_out, frame)

        results = []
        