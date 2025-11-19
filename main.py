from ultralytics import YOLO
from pathlib import Path
from collections import defaultdict
import cv2
import json

import config
import sectors as sector_mod


def load_model():
    model = YOLO(str(config.MODEL_PATH))
    # 클래스 이름 → id 매핑
    name_to_id = {name: idx for idx, name in model.names.items()}
    fire_id = name_to_id[config.FIRE_CLASS_NAME]
    return model, fire_id


def get_latest_image(image_dir: Path) -> Path:
    """폴더 안에서 가장 최근 jpg/png 한 장 찾기"""
    candidates = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    if not candidates:
        raise FileNotFoundError(f"No image found in {image_dir}")
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return latest


def crop_map_region(img_path: Path) -> tuple:
    """
    원본 이미지에서 맵 영역만 crop해서 반환.
    반환: (cropped_image, original_path)
    """
    img = cv2.imread(str(img_path))
    if img is None:
        raise RuntimeError(f"Failed to read image: {img_path}")
    
    img_h, img_w = img.shape[:2]
    
    # 경계 체크
    x1 = max(0, config.MAP_CROP_X1)
    y1 = max(0, config.MAP_CROP_Y1)
    x2 = min(img_w, config.MAP_CROP_X2)
    y2 = min(img_h, config.MAP_CROP_Y2)
    
    # crop
    cropped = img[y1:y2, x1:x2]
    
    print(f"Cropped map region: ({x1}, {y1}) to ({x2}, {y2}), size: {cropped.shape[1]}x{cropped.shape[0]}")
    return cropped, img_path


def infer_fire_sectors(model, fire_id: int, img):
    """
    이미지 한 장에서 불난 건물 섹터 번호 2개 뽑기.

    전제:
    - img 는 이미 "맵만 잘려 있는" 상태의 numpy 배열이다.
    - 따라서 이미지 전체 좌표계 (0 ~ width, 0 ~ height) 안에서
      config.BUILDING_CENTERS_NORM 에 정의된 건물 센터와 YOLO 박스 중심을 비교한다.
    """
    img_h, img_w = img.shape[:2]

    # YOLO 추론은 맵 전체 이미지를 그대로 사용
    results = model(img, verbose=False)[0]

    sector_best_conf = defaultdict(float)

    for box in results.boxes:
        cls = int(box.cls[0])
        if cls != fire_id:
            continue

        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        # 가장 가까운 건물 센터를 기준으로 섹터 판정
        sector = sector_mod.sector_by_nearest_building(cx, cy, img_w, img_h)

        # 같은 섹터에 여러 박스가 있으면 가장 높은 conf만 사용
        if conf > sector_best_conf[sector]:
            sector_best_conf[sector] = conf

    if not sector_best_conf:
        return []

    # 신뢰도 높은 순으로 정렬 후 상위 2개 선택
    ordered = sorted(sector_best_conf.items(), key=lambda x: (-x[1], x[0]))
    top_sectors = [sec for sec, _ in ordered[:2]]
    return top_sectors


def save_json(sectors):
    """AB12.json 파일 저장"""
    out_dir = config.JSON_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{config.MISSION_CODE}.json"

    data = {
        "mission_code": config.MISSION_CODE,
        "fire_sectors": sectors,  # 예: [2, 7]
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path} (sectors={sectors})")


def main():
    model, fire_id = load_model()
    latest_img_path = get_latest_image(config.IMAGE_DIR)
    print("Latest image:", latest_img_path)

    # 원본 이미지에서 맵 영역만 자동 crop
    cropped_img, _ = crop_map_region(latest_img_path)

    sectors = infer_fire_sectors(model, fire_id, cropped_img)

    if len(sectors) != 2:
        print("[WARN] 감지된 불난 건물 수가 2개가 아님:", sectors)
    else:
        save_json(sectors)


if __name__ == "__main__":
    main()
