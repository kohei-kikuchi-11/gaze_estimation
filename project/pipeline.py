# pipeline.py
# パイプライン本体
import numpy as np
from models import FaceDetector, LandmarkDetector, HeadPoseEstimator, GazeEstimation

class GazePipeline:
    def __init__(self, model_paths):
        """
        モデルパスの出力を受け取る
        """
        self.face = FaceDetector(model_paths["face"])
        self.landmark = LandmarkDetector(model_paths["landmark"])
        self.headpose = HeadPoseEstimator(model_paths["headpose"])
        self.gaze = GazeEstimation(model_paths["gaze"])

    def get_square_roi(self, face_img, cx, cy,landmarks):
        '''

        '''
        left_w = np.linalg.norm(np.array(landmarks[0]) - np.array(landmarks[1]))
        right_w = np.linalg.norm(np.array(landmarks[2]) - np.array(landmarks[3]))
        size = int(max(left_w, right_w) * 1.5)
        h, w = face_img.shape[:2]
        half =  size // 2

        start_x = max(0, min(cx - half, w - size))
        start_y = max(0, min(cy -half, h -size))
        # 開始位置から確実に固定サイズを確保する
        end_x = start_x + size
        end_y = start_y + size

        roi_img = face_img[start_y:end_y, start_x:end_x]

        return roi_img, (start_x, start_y,end_x, end_y)

    def process_frame(self, frame):
        # Face Detection
        face_input = self.face.preprocess(frame)
        face_out = self.face.infer(face_input)
        faces = self.face.postprocess(face_out, frame)

        results = []
        # Landmark
        for (conf, xmin, ymin, xmax, ymax) in faces:
            face_img = frame[ymin:ymax, xmin:xmax]

            lm_input = self.landmark.preprocess(face_img)
            lm_out = self.landmark.infer(lm_input)
            landmarks = self.landmark.postprocess(lm_out, face_img)
            # 目の中心座標を計算 左目p0,p1 右目p2,p3
            lx, ly = (landmarks[0][0] + landmarks[1][0]) // 2, (landmarks[0][1] + landmarks[1][1]) // 2
            rx, ry = (landmarks[2][0] + landmarks[3][0]) // 2, (landmarks[2][1] + landmarks[3][1]) // 2

            # 目の切り出し
            left_eye_img ,left_coords = self.get_square_roi(face_img, lx, ly, landmarks)
            right_eye_img ,right_coords = self.get_square_roi(face_img, rx, ry, landmarks)
    
            # head pose
            hp_input = self.headpose.preprocess(face_img)
            hp_out = self.headpose.infer(hp_input)
            head_pose = self.headpose.postprocess(hp_out)

            # gaze
            gaze_input = self.gaze.preprocess(left_eye_img, right_eye_img, head_pose)
            gaze_out = self.gaze.infer(gaze_input)
            gaze_vec = self.gaze.postprocess(gaze_out)
            gaze_vec = gaze_vec.flatten()
            # それぞれの結果を格納
            results.append({
                "face": (xmin, ymin, xmax, ymax),
                "face_conf": conf,
                "landmarks" : [(xmin + x, ymin + y) for (x, y) in landmarks],
                "left_eye": (xmin + left_coords[0], ymin + left_coords[1], xmin + left_coords[2], ymin + left_coords[3]),
                "right_eye": (xmin + right_coords[0], ymin + right_coords[1], xmin + right_coords[2], ymin + right_coords[3]),
                "head_pose":head_pose,
                "gaze": gaze_vec
            })
        return results
