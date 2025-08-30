from ultralytics import YOLO
import cv2
from camera_usb import Camera

# YOLOv8 の軽量モデルをロード
model = YOLO("yolov8n.pt")

# 画像を読み込み
#image_path = "./images/captured.jpg"   # 検出したい画像を用意
cam = Camera()
image_path = cam.take_photo()  # 保存された画像ファイルのパスが返る
results = model(image_path)

# 結果を描画して表示
for result in results:
    for box in result.boxes:
        annotated_frame = result.plot()  # バウンディングボックスなどを描画
        cv2.imwrite("output.jpg", annotated_frame)
        cv2.waitKey(0)
        cls_id = int(box.cls[0])         # クラスID
        cls_name = model.names[cls_id]  # クラス名
        conf = float(box.conf[0])        # 信頼度
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # 座標（左上x,y,右下x,y）

        w = x2 - x1
        h = y2 - y1
        cx = x1 + w // 2
        cy = y1 + h // 2
        print(f"{cls_name}: conf={conf:.2f}, center=({cx},{cy}), size=({w}x{h})")

cv2.destroyAllWindows()
