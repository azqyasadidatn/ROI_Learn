from ultralytics import YOLO
import cv2
import numpy as np

# Load YOLO model
model = YOLO(r"/home/azqya/Documents/BANDHA26/ROI_Learn/best (7).pt")

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# ============== CONFIGURATION ==============
CONF_THRESH = 0.3           # Minimum confidence untuk deteksi
STABILITY_FRAMES = 10       # Jumlah frame stabil untuk auto-lock grid
STABILITY_THRESHOLD = 20    # Maksimal pergeseran bbox (pixel)
MIN_CONFIDENCE = 0.5        # Minimum confidence untuk auto-lock

# ============== STATE VARIABLES ==============
frame_count = 0

# Auto-calibration
CALIBRATED = False
GRID_BOUNDS = None          # (lx1, ly1, lx2, ly2) - FIXED setelah kalibrasi
CELL_W = 0
CELL_H = 0
love_box_history = []       # History untuk stabilisasi

# Cache
last_markers = []
last_all_box = []
last_grid = [["0"] * 3 for _ in range(3)]


# ============== HELPER FUNCTIONS ==============
def is_bbox_stable(history, threshold):
    """Cek apakah bbox stabil selama N frame"""
    if len(history) < STABILITY_FRAMES:
        return False
    
    recent = history[-STABILITY_FRAMES:]
    x1s, y1s, x2s, y2s = zip(*recent)
    
    return (max(x1s) - min(x1s) < threshold and
            max(y1s) - min(y1s) < threshold and
            max(x2s) - min(x2s) < threshold and
            max(y2s) - min(y2s) < threshold)


def get_average_bbox(history):
    """Hitung rata-rata bbox dari history"""
    recent = history[-STABILITY_FRAMES:]
    x1 = int(np.mean([b[0] for b in recent]))
    y1 = int(np.mean([b[1] for b in recent]))
    x2 = int(np.mean([b[2] for b in recent]))
    y2 = int(np.mean([b[3] for b in recent]))
    return (x1, y1, x2, y2)


def get_cell(cx, cy):
    """Hitung cell (row, col) dari koordinat center"""
    if not CALIBRATED or GRID_BOUNDS is None:
        return None, None
    
    lx1, ly1, lx2, ly2 = GRID_BOUNDS
    
    if not (lx1 <= cx <= lx2 and ly1 <= cy <= ly2):
        return None, None
    
    col = (cx - lx1) // CELL_W
    row = (cy - ly1) // CELL_H
    
    if 0 <= row < 3 and 0 <= col < 3:
        return int(row), int(col)
    return None, None


def validate_marker(cx, cy, x1, y1, x2, y2):
    """Validasi apakah marker overlap >= 50% dengan cell"""
    if not CALIBRATED or GRID_BOUNDS is None:
        return False
    
    row, col = get_cell(cx, cy)
    if row is None:
        return False
    
    lx1, ly1, _, _ = GRID_BOUNDS
    
    cell_x1 = lx1 + col * CELL_W
    cell_y1 = ly1 + row * CELL_H
    cell_x2 = cell_x1 + CELL_W
    cell_y2 = cell_y1 + CELL_H
    
    overlap_x = max(0, min(x2, cell_x2) - max(x1, cell_x1))
    overlap_y = max(0, min(y2, cell_y2) - max(y1, cell_y1))
    overlap_area = overlap_x * overlap_y
    marker_area = (x2 - x1) * (y2 - y1)
    
    return marker_area > 0 and (overlap_area / marker_area) >= 0.5


# ============== MAIN ==============
print("=" * 60)
print("VISION NODE - Tic-Tac-Toe Board Detection")
print("=" * 60)
print(f"Auto-calibration: {STABILITY_FRAMES} frame stabil untuk lock")
print("Tekan 'r' untuk reset, ESC untuk keluar")
print("=" * 60)

while cap.isOpened():
    ret, frame = cap.read()
    frame_count += 1
    if not ret:
        break

    # --- DETECTION (setiap 3 frame) ---
    if frame_count % 3 == 0:
        results = model(frame, conf=CONF_THRESH, stream=True, verbose=False)
        
        temp_love_box = None
        temp_love_conf = 0
        markers = []
        all_box = []

        for r in results:
            for box in r.boxes:
                cls_name = model.names[int(box.cls[0])].lower()
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                all_box.append((cls_name, x1, y1, x2, y2, conf))

                if cls_name == "love":
                    temp_love_box = (x1, y1, x2, y2)
                    temp_love_conf = conf
                elif cls_name in ["uknow", "udontknow"]:
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    if CALIBRATED:
                        if validate_marker(cx, cy, x1, y1, x2, y2):
                            markers.append((cls_name, cx, cy, x1, y1, x2, y2))
                    else:
                        markers.append((cls_name, cx, cy, x1, y1, x2, y2))

        last_markers = markers
        last_all_box = all_box

        # === AUTO-CALIBRATION ===
        if not CALIBRATED:
            if temp_love_box and temp_love_conf >= MIN_CONFIDENCE:
                love_box_history.append(temp_love_box)
                if len(love_box_history) > STABILITY_FRAMES * 2:
                    love_box_history.pop(0)
                
                if is_bbox_stable(love_box_history, STABILITY_THRESHOLD):
                    GRID_BOUNDS = get_average_bbox(love_box_history)
                    lx1, ly1, lx2, ly2 = GRID_BOUNDS
                    CELL_W = (lx2 - lx1) // 3
                    CELL_H = (ly2 - ly1) // 3
                    CALIBRATED = True
                    print("=" * 60)
                    print("✅ AUTO-CALIBRATED! Grid locked.")
                    print(f"   Bounds: {GRID_BOUNDS}")
                    print(f"   Cell: {CELL_W} x {CELL_H}")
                    print("=" * 60)
            else:
                love_box_history.clear()

    # --- VISUALISASI ---
    for cls_name, x1, y1, x2, y2, conf in last_all_box:
        color = (0, 255, 255) if cls_name == "love" else (255, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
        cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # --- GRID LOGIC ---
    grid = [["0"] * 3 for _ in range(3)]

    if CALIBRATED and GRID_BOUNDS:
        lx1, ly1, lx2, ly2 = GRID_BOUNDS
        
        cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 255, 0), 3)
        for i in range(1, 3):
            cv2.line(frame, (lx1 + i * CELL_W, ly1), (lx1 + i * CELL_W, ly2), (0, 255, 0), 2)
            cv2.line(frame, (lx1, ly1 + i * CELL_H), (lx2, ly1 + i * CELL_H), (0, 255, 0), 2)

        for item in last_markers:
            name, cx, cy = item[0], item[1], item[2]
            row, col = get_cell(cx, cy)
            if row is not None:
                grid[row][col] = "B" if name == "uknow" else "R"
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        for r in range(3):
            for c in range(3):
                text = grid[r][c]
                px = lx1 + c * CELL_W + CELL_W // 2 - 10
                py = ly1 + r * CELL_H + CELL_H // 2 + 10
                cv2.putText(frame, text, (px, py),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
        
        cv2.putText(frame, "CALIBRATED", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        progress = min(len(love_box_history) / STABILITY_FRAMES * 100, 100)
        cv2.putText(frame, f"Calibrating... {progress:.0f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        bar_w = 200
        filled = int(bar_w * progress / 100)
        cv2.rectangle(frame, (10, 40), (10 + bar_w, 60), (100, 100, 100), -1)
        cv2.rectangle(frame, (10, 40), (10 + filled, 60), (0, 255, 0), -1)

    # --- OUTPUT: ALWAYS SEND ---
    if grid != last_grid:
        print(grid)
        last_grid = [row[:] for row in grid]

    cv2.imshow("YOLO Grid - Vision Node", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord('r'):
        CALIBRATED = False
        GRID_BOUNDS = None
        CELL_W = CELL_H = 0
        love_box_history.clear()
        print("🔄 Reset kalibrasi")

cap.release()
cv2.destroyAllWindows()
