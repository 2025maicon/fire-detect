from __future__ import annotations

from typing import Dict, Tuple
import config


# === 구 3x3 격자 방식 함수 (더 이상 사용하지 않음) ===
# def pos_to_sector(cx: float, cy: float) -> int:
#     """
#     YOLO 박스 중심(cx, cy)을 섹터 1~9로 변환.
#     맵 영역을 3x3 격자로 나눈 뒤 어떤 칸에 들어가는지 계산.
#     """
#     ...


def sector_by_nearest_building(cx: float, cy: float, img_w: int, img_h: int) -> int:
    """
    YOLO 박스 중심 좌표 (cx, cy)를 입력으로 받아,
    config.BUILDING_CENTERS_NORM 에 정의된 9개 건물 센터 중
    '가장 가까운' 건물의 섹터 번호(1~9)를 반환한다.

    전제:
    - img_w, img_h 는 현재 맵 이미지의 width, height 이다.
    - BUILDING_CENTERS_NORM 의 좌표는 (x_norm, y_norm) = (x / W, y / H) 형태이다.
    """
    centers: Dict[int, Tuple[float, float]] = config.BUILDING_CENTERS_NORM
    if not centers:
        raise ValueError("BUILDING_CENTERS_NORM is empty; configure building centers in config.py")

    # YOLO 박스 중심의 정규화 좌표
    if img_w <= 0 or img_h <= 0:
        raise ValueError(f"Invalid image size: width={img_w}, height={img_h}")

    cx_norm = cx / float(img_w)
    cy_norm = cy / float(img_h)

    best_sector: int | None = None
    best_dist2: float = float("inf")

    for sector, (bx_norm, by_norm) in centers.items():
        dx = cx_norm - bx_norm
        dy = cy_norm - by_norm
        d2 = dx * dx + dy * dy

        if d2 < best_dist2:
            best_dist2 = d2
            best_sector = sector

    if best_sector is None:
        raise ValueError("No valid building centers configured in BUILDING_CENTERS_NORM")

    return best_sector
