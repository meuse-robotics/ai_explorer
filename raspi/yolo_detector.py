from ultralytics import YOLO
import cv2
import json

class YoloDetector:
    def __init__(self, model_path="yolov8n.pt", target_class="cup", conf_threshold=0.1):
        """YOLO モデルを初期化"""
        self.model = YOLO(model_path)
        self.target_class = target_class
        self.conf_threshold = conf_threshold

    def detect_cup(self, image_path):
        """
        画像から cup を検出し、(center_x, center_y), (width, height) を返す
        見つからなければ None を返す
        """
        results = self.model(image_path, verbose=False)

        for result in results:
            for box in result.boxes:
                annotated_frame = result.plot()  # バウンディングボックスなどを描画
                cv2.imwrite("output.jpg", annotated_frame)
                cv2.waitKey(0)
                cls_id = int(box.cls[0])         # クラスID
                cls_name = self.model.names[cls_id]  # クラス名
                conf = float(box.conf[0])        # 信頼度
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # 座標（左上x,y,右下x,y）

                # 対象クラスのみ処理
                if cls_name == self.target_class and conf > self.conf_threshold:
                    w = x2 - x1
                    h = y2 - y1
                    cx = x1 + w // 2
                    cy = y1 + h // 2
                    
                    detection = {
                        "class": cls_name,
                        "confidence": round(conf, 2),
                        "position": cx,
                        "height": h
                    }
                    print(detection)
                    return json.dumps(detection, ensure_ascii=False, indent=2)

        return None  # 見つからなかった場合

# ===== 使い方 =====
"""if __name__ == "__main__":
    detector = YoloDetector()
    image_path = "./images/captured.jpg"
    result = detector.detect_cup(image_path)

    if result:
        center, size = result
        print(f"Cup center={center}, size={size}")
    else:
        print("Cup not found")"""
