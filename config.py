from pathlib import Path

# === YOLO / 클래스 설정 ===
MODEL_PATH = Path("models/best.pt")   # 같은 폴더 안 models/best.pt
FIRE_CLASS_NAME = "fire"     # Roboflow에서 쓴 클래스 이름

# === 미션/입출력 경로 ===
MISSION_CODE = "AB12"

# 드론 이미지가 떨어지는 폴더
IMAGE_DIR = Path.home() / "Documents" / "maicon" / "local_inbox"
# json을 저장할 폴더
JSON_OUT_DIR = Path.home() / "Documents" / "ai_outbox"

# === 섹터(건물) 중심 좌표 (정규화 버전) ===
# YOLO 입력 이미지는 이미 "맵만" 잘려 있는 상태라고 가정한다.
# 이때 이미지의 width=W, height=H 라면, 각 건물 중심 좌표를
#   x_norm = x_pixel / W
#   y_norm = y_pixel / H
# 와 같은 방식으로 0~1 범위로 정규화해서 저장한다.
#
# 이 좌표들은 초기 설정 시 debug_building_centers.py로 한 번만 설정하면 되며,
# 이후 실제 테스트 시에는 이 미리 설정된 좌표를 자동으로 사용합니다.
# 각 섹터 번호(1~9)에 대응하는 건물 중심 좌표가 딕셔너리로 저장되어 있습니다.
#
BUILDING_CENTERS_NORM: dict[int, tuple[float, float]] = {
    1: (0.0, 0.0),  # 섹터 1번 건물 중심 (정규화 좌표)
    2: (0.0, 0.0),  # 섹터 2번 건물 중심
    3: (0.0, 0.0),  # 섹터 3번 건물 중심
    4: (0.0, 0.0),  # 섹터 4번 건물 중심
    5: (0.0, 0.0),  # 섹터 5번 건물 중심
    6: (0.0, 0.0),  # 섹터 6번 건물 중심
    7: (0.0, 0.0),  # 섹터 7번 건물 중심
    8: (0.0, 0.0),  # 섹터 8번 건물 중심
    9: (0.0, 0.0),  # 섹터 9번 건물 중심
}

# === 원본 이미지에서 맵 영역 crop 좌표 ===
# local_inbox에 들어온 원본 이미지에서 맵 영역만 자르기 위한 좌표
# 좌상단 (MAP_CROP_X1, MAP_CROP_Y1), 우하단 (MAP_CROP_X2, MAP_CROP_Y2)
# TODO: 실제 원본 이미지에서 맵 영역 좌표를 확인해서 수정하세요
MAP_CROP_X1, MAP_CROP_Y1 = 150, 120
MAP_CROP_X2, MAP_CROP_Y2 = 1150, 920
