from openvino.runtime import Core
import numpy as np
import cv2

def to_nchw(image):
    """入力画像(h,w,c)→(n,c,h,c)に変換する
    """
    image = np.transpose(image, (2, 0, 1))[np.newaxis, :]
    return image

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
        