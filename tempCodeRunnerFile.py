# Show drift info
        # if current_love_box:
        #     drift = calculate_drift(current_love_box, GRID_BOUNDS)
        #     drift_color = (0, 255, 0) if drift < DRIFT_THRESHOLD else (0, 0, 255)
        #     cv2.putText(frame, f"LOCKED | Drift: {drift:.0f}px", (10, 30),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, drift_color, 2)
        # else:
        #     cv2.putText(frame, "LOCKED | Love not visible", (10, 30),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)