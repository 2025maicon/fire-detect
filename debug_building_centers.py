# debug_building_centers.py
# 초기 설정용: 건물 중심 좌표를 클릭해서 config.py에 자동 저장
import cv2
from pathlib import Path
import re
import config


def get_latest_image(image_dir: Path) -> Path:
    candidates = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    if not candidates:
        raise FileNotFoundError(f"No image found in {image_dir}")
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest


def update_config_file(centers: dict[int, tuple[float, float]]):
    """config.py 파일의 BUILDING_CENTERS_NORM 딕셔너리를 업데이트"""
    config_path = Path("config.py")
    content = config_path.read_text(encoding="utf-8")
    
    # BUILDING_CENTERS_NORM 딕셔너리 부분 찾기
    pattern = r'BUILDING_CENTERS_NORM: dict\[int, tuple\[float, float\]\] = \{.*?\}'
    
    # 새 딕셔너리 문자열 생성
    new_dict_lines = ["BUILDING_CENTERS_NORM: dict[int, tuple[float, float]] = {"]
    for i in range(1, 10):
        if i in centers:
            x_norm, y_norm = centers[i]
            new_dict_lines.append(f"    {i}: ({x_norm:.6f}, {y_norm:.6f}),  # 섹터 {i}번 건물 중심")
        else:
            new_dict_lines.append(f"    {i}: (0.0, 0.0),  # 섹터 {i}번 건물 중심")
    new_dict_lines.append("}")
    new_dict_str = "\n".join(new_dict_lines)
    
    # 정규식으로 교체
    new_content = re.sub(pattern, new_dict_str, content, flags=re.DOTALL)
    
    config_path.write_text(new_content, encoding="utf-8")
    print(f"\n✓ config.py 업데이트 완료! {len(centers)}개 섹터 좌표가 저장되었습니다.")


def main():
    img_path = get_latest_image(config.IMAGE_DIR)
    print(f"[debug] Using image: {img_path}")

    # 원본 이미지 읽기
    original_img = cv2.imread(str(img_path))
    if original_img is None:
        raise RuntimeError(f"Failed to read image: {img_path}")

    # 맵 영역만 crop
    img_h, img_w = original_img.shape[:2]
    x1 = max(0, config.MAP_CROP_X1)
    y1 = max(0, config.MAP_CROP_Y1)
    x2 = min(img_w, config.MAP_CROP_X2)
    y2 = min(img_h, config.MAP_CROP_Y2)
    
    img = original_img[y1:y2, x1:x2]
    
    h, w = img.shape[:2]
    print(f"[debug] Original image size: {img_w}x{img_h}")
    print(f"[debug] Cropped map size: width={w}, height={h}")
    print(f"[debug] Crop region: ({x1}, {y1}) to ({x2}, {y2})")
    print("\n=== 건물 중심 좌표 설정 ===")
    print("1번부터 9번까지 순서대로 건물 중심을 클릭하세요.")
    print("각 클릭 시 섹터 번호와 좌표가 표시됩니다.")
    print("9개 모두 클릭하면 자동으로 config.py에 저장됩니다.")
    print("ESC 키(27)를 누르면 종료합니다.\n")

    # 섹터 번호별 좌표 저장 {섹터: (x_norm, y_norm)}
    centers: dict[int, tuple[float, float]] = {}

    def mouse_callback(event, x, y, flags, param):
        nonlocal centers, img, w, h
        if event == cv2.EVENT_LBUTTONDOWN:
            next_sector = len(centers) + 1
            
            if next_sector > 9:
                print(f"[경고] 이미 9개 모두 입력했습니다. (x={x}, y={y})")
                return
            
            x_norm = x / float(w)
            y_norm = y / float(h)
            centers[next_sector] = (x_norm, y_norm)
            
            print(f"[섹터 {next_sector}] 클릭: x={x}, y={y} -> 정규화: ({x_norm:.6f}, {y_norm:.6f})")

            # 디스플레이용 이미지 복사
            disp = img.copy()
            for sec, (px_norm, py_norm) in centers.items():
                px = int(px_norm * w)
                py = int(py_norm * h)
                cv2.circle(disp, (px, py), 10, (0, 255, 0), -1)
                cv2.putText(disp, str(sec), (px + 15, py), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("map_debug", disp)
            
            if len(centers) == 9:
                print("\n모든 좌표 입력 완료! config.py를 업데이트합니다...")

    cv2.namedWindow("map_debug", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("map_debug", mouse_callback)

    cv2.imshow("map_debug", img)

    while True:
        key = cv2.waitKey(10) & 0xFF
        if key == 27:  # ESC
            break
        if len(centers) == 9:
            # 잠시 대기 후 업데이트
            cv2.waitKey(500)
            update_config_file(centers)
            print("\n좌표 저장 완료! 창을 닫으려면 아무 키나 누르세요.")
            cv2.waitKey(0)
            break

    cv2.destroyAllWindows()
    if centers:
        print(f"\n[debug] 설정된 섹터 좌표: {centers}")


if __name__ == "__main__":
    main()

