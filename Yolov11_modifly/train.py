from ultralytics import YOLO

model = YOLO("yolo11m.pt") 

model.train(data="dataset_custom.yaml", epochs=100, imgsz=640, batch=8, workers = 0, device = 0)

