from ultralytics import YOLO
import cv2

model = YOLO("Datasetnya/best (7).pt")
cap = cv2.VideoCapture(0)

CONF = 0.5

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO inference (FAST MODE)
    results = model(frame, conf=CONF, verbose=False)

    love = None
    markers = []

    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue

        for b in boxes:
            cls = model.names[int(b.cls)].lower()
            x1, y1, x2, y2 = map(int, b.xyxy[0])

            if cls == "love":
                love = (x1, y1, x2, y2)

            elif cls == "uknow" or cls == "udontknow":
                markers.append((cls, (x1 + x2) >> 1, (y1 + y2) >> 1))

    # Initialize grid
    grid = [["0"] * 3 for _ in range(3)]

    if love:
        lx1, ly1, lx2, ly2 = love
        cw = (lx2 - lx1) // 3
        ch = (ly2 - ly1) // 3

        for cls, cx, cy in markers:
            c = (cx - lx1) // cw
            r = (cy - ly1) // ch

            if 0 <= r < 3 and 0 <= c < 3:
                grid[r][c] = "B" if cls == "uknow" else "R"

        # Minimal visualization (OPTIONAL)
        cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 255, 0), 2)

    print(grid)

    cv2.imshow("Fast Grid", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
