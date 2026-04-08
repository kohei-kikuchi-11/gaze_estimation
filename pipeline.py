# pipeline.py
# パイプライン本体
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

    def get_square_roi(face_img, cx, cy, size=20):
        h, w = face_img.shape[:2]
        half size // 2

        
    
    def process_frame(self, frame):
        # Face Detection
        face_input = self.face.preprocess(frame)
        face_out = self.face.infer(face_input)
        faces = self.face.postprocess(face_out, frame)

        results = []

        for (conf, xmin, ymin, xmax, ymax) in faces:
            face_img = frame[ymin:ymax, xmin:xmax]

            # Landmark

            lm_input = self.landmark.preprocess(face_img)
            lm_out = self.landmark.infer(lm_input)
            landmarks = self.landmark.postprocess(lm_out, face_img)
            # 目の中心座標を計算
            lx, ly = (landmarks[0][0] + landmarks[1][0]) // 2, (landmarks[0][1] + landmarks[1][1]) // 2
            rx, ry = (landmarks[2][0] + landmarks[3][0]) // 2, (landmarks[2][1] + landmarks[3][1]) // 2

            # 目の切り出し
            left_eye = face_img[max(0, ly - 10):ly+ 10, max(0, lx-10):lx+ 10]
            right_eye = face_img[max(0, ry - 10):ry + 10, max(0, rx -  10): rx + 10]
    
            # head pose

            hp_input = self.headpose.preprocess(face_img)
            hp_out = self.headpose.infer(hp_input)
            head_pose = self.headpose.postprocess(hp_out)

            # gaze
            gaze_input = self.gaze.preprocess(left_eye, right_eye, head_pose)
            gaze_out = self.gaze.infer(gaze_input)
            gaze_vec = self.gaze.postprocess(gaze_out)
            gaze_vec.flatten()

            results.append({
                "face": (xmin, ymin, xmax, ymax),
                "face_conf": conf,
                "landmarks" : [(xmin + x, ymin + y) for (x, y) in landmarks],
                "left_eye": (xmin+lx-10, ymin+ly-20, xmin+lx+10, ymin+ly+10),
                "right_eye": (xmin+rx-10, ymin+ry-10, xmin+rx+10, ymin+ry+10),
                "head_pose":head_pose,
                "gaze": gaze_vec
            })
        return results
