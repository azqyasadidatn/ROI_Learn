from ultralytics import YOLO

# Load a pretrained YOLOv8n model
model=YOLO("Datasetnya/best (6).pt")

# Run inference on the source
results = model(source=0, show=True) # generator of Results objects

#source=0 --> camera
#source=1 --> ext webcam, etc