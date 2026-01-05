from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO(r"/home/azqya/Documents/BANDHA26/ROI_Learn/best (7).pt")

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

frame_count = 0
last_markers = []
last_love_box = None
last_all_box = []
last_grid = [["0"] * 3 for _ in range(3)]

CONF_THRESH = 0.3  # use lower threshold for stability

while cap.isOpened():
    ret, frame = cap.read()
    frame_count += 1
    if not ret:
        break

    # --- DETECTION (setiap 3 frame) ---
    if frame_count % 3 == 0:
        results = model(frame, conf=CONF_THRESH, stream=True, verbose=False)
        
        love_box = None
        markers = []
        all_box = []

        for r in results:
            for box in r.boxes:
                cls_name = model.names[int(box.cls[0])].lower()
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                all_box.append((cls_name, x1, y1, x2, y2, conf))

                if cls_name == "love":
                    love_box = (x1, y1, x2, y2)
                elif cls_name in ["uknow", "udontknow"]:
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    markers.append((cls_name, cx, cy))

        # Update cache SETELAH deteksi selesai
        last_love_box = love_box
        last_markers = markers
        last_all_box = all_box

    # --- VISUALISASI (setiap frame, pakai cache) ---
    for cls_name, x1, y1, x2, y2, conf in last_all_box:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 1)
        cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        if cls_name in ["uknow", "udontknow"]:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

    # --- GRID LOGIC ---
    grid = [["0"] * 3 for _ in range(3)]

    if last_love_box:
        lx1, ly1, lx2, ly2 = last_love_box
        cell_w = (lx2 - lx1) // 3
        cell_h = (ly2 - ly1) // 3

        # Draw board
        cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 255, 0), 3)

        # Draw grid lines
        for i in range(1, 3):
            cv2.line(frame, (lx1 + i * cell_w, ly1), (lx1 + i * cell_w, ly2), (255, 255, 255), 2)
            cv2.line(frame, (lx1, ly1 + i * cell_h), (lx2, ly1 + i * cell_h), (255, 255, 255), 2)

        # Fill matrix
        for name, cx, cy in last_markers:
            col = (cx - lx1) // cell_w
            row = (cy - ly1) // cell_h

            if 0 <= row < 3 and 0 <= col < 3:
                grid[row][col] = "B" if name == "uknow" else "R"

        # Display matrix inside grid
        for r in range(3):
            for c in range(3):
                text = grid[r][c]
                px = lx1 + c * cell_w + cell_w // 2 - 10
                py = ly1 + r * cell_h + cell_h // 2 + 10
                cv2.putText(frame, text, (px, py),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)

    # --- OUTPUT (hanya saat berubah) ---
    if grid != last_grid:
        print(grid)
        last_grid = [row[:] for row in grid]

    cv2.imshow("YOLO Grid Debug View", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
