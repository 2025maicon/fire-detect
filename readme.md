# maicon_fire v1 사용 가이드

아까 팀장님이랑 이야기 나눈 방식으로 일단 만들어 보았습니다. 이 코드를 살리거나 죽이거나 어떤 방식이든 상관 없습니다.. 화재감지 관련 내용을 두 분께 맡기고 자러 가보겠습니다.. 
학습은 일단 기존에 있던 데이터로 해 놓았습니다. 메인 컴퓨터에 있을겁니다. 화재건물만을 라벨링해 학습을 진행했기 때문에 추가 데이터가 필요하다면 연습용 경기장에서도 수급이 가능할 것 같습니다.

## 1. 프로젝트 개요
- 드론이 촬영한 원본 이미지를 입력으로 받아, 자동으로 맵 영역만 crop한 뒤 YOLO 모델로 불 난 건물을 찾고, 섹터 번호 2개를 JSON으로 저장합니다.
- 섹터는 정규화된 건물 중심 좌표(`config.BUILDING_CENTERS_NORM`) 중 가장 가까운 건물을 선택하는 방식입니다.

## 2. 기본 구조
- `config.py`: 경로, 미션 코드, 모델 경로, 맵 crop 좌표, 건물 중심 좌표 설정
- `main.py`: 최신 이미지 자동 crop → YOLO 추론 → 섹터 2개 추출 → JSON 저장
- `sectors.py`: YOLO 박스 중심과 가장 가까운 건물 센터 계산
- `debug_building_centers.py`: 원본 이미지를 자동 crop한 뒤 건물 중심 좌표를 클릭해 정규화 값 확인
- `models/best.pt`: YOLO 가중치(직접 추가 필요)

## 3. 환경 준비
1. Python 3.11 가상환경 생성 및 활성화 (예시)
   ```bash
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   ```
2. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
3. `models/best.pt`를 `models` 폴더에 복사합니다.

## 4. 입력/출력 경로 설정
- `config.IMAGE_DIR`: 원본 드론 이미지가 떨어지는 폴더 (기본: `~/Documents/maicon/local_inbox`)
- `config.JSON_OUT_DIR`: 결과 JSON을 저장할 폴더 (기본: `~/Documents/ai_outbox`)
- `config.MISSION_CODE`: 저장될 JSON 파일 이름(`MISSION_CODE.json`)

## 5. 맵 영역 crop 좌표 설정
1. `config.py`에서 `MAP_CROP_X1, MAP_CROP_Y1, MAP_CROP_X2, MAP_CROP_Y2` 값을 설정합니다.
   - 원본 이미지에서 맵 영역의 좌상단/우하단 픽셀 좌표입니다.
   - 예: `MAP_CROP_X1, MAP_CROP_Y1 = 150, 120` (좌상단)
   - 예: `MAP_CROP_X2, MAP_CROP_Y2 = 1150, 920` (우하단)
2. 이 좌표는 원본 이미지 기준이므로, 실제 드론 이미지에서 맵 영역을 확인해서 수정하세요.

## 6. 건물 중심 좌표 초기 설정 (한 번만 수행)
**주의: 이 과정은 초기 설정 시 한 번만 수행하면 됩니다. 이후 실제 테스트 시에는 자동으로 미리 설정된 좌표를 사용합니다.**

1. 원본 드론 이미지를 `IMAGE_DIR`에 넣습니다.
2. `python debug_building_centers.py` 실행
   - 프로그램이 최신 원본 이미지를 자동으로 crop해서 보여줍니다.
   - **1번부터 9번까지 순서대로** 각 섹터의 건물 중심을 클릭합니다.
   - 각 클릭 시 터미널에 섹터 번호와 정규화 좌표가 출력됩니다.
   - 9개 모두 클릭하면 **자동으로 `config.py`에 저장**됩니다.
   - ESC(27) 키로 종료할 수 있습니다.
3. 저장된 좌표 확인
   - `config.py`의 `BUILDING_CENTERS_NORM` 딕셔너리에 섹터 번호별로 좌표가 저장됩니다.
   - 좌표는 0~1 범위의 정규화 좌표이며 해상도와 무관하게 동일하게 사용됩니다.
   - 형식: `{1: (x_norm, y_norm), 2: (x_norm, y_norm), ..., 9: (x_norm, y_norm)}`

## 7. 추론 실행 방법 (실제 테스트)
1. `config.py`에서 다음을 확인합니다:
   - `MAP_CROP_X1, MAP_CROP_Y1, MAP_CROP_X2, MAP_CROP_Y2`가 올바르게 설정되었는지
   - `BUILDING_CENTERS_NORM`가 실제 값으로 채워졌는지 (초기 설정 완료 여부)
2. 원본 드론 이미지를 `IMAGE_DIR`에 넣습니다.
3. `python main.py` 실행
   - `config.IMAGE_DIR`의 최신 원본 이미지를 자동으로 선택합니다.
   - 자동으로 맵 영역만 crop합니다.
   - **미리 설정된 `BUILDING_CENTERS_NORM` 좌표를 자동으로 사용**합니다.
   - YOLO 추론 후 감지된 불 박스 중심과 가장 가까운 건물 2개를 선택합니다.
   - 두 섹터가 감지되지 않으면 경고만 출력하고 JSON은 저장하지 않습니다.
   - 두 섹터가 감지되면 `config.JSON_OUT_DIR/MISSION_CODE.json`이 생성됩니다.

**중요: 실제 테스트 시에는 좌표를 직접 찍는 과정이 없습니다. 미리 설정된 좌표를 자동으로 사용합니다.**

## 8. 기타 유의 사항
- 원본 이미지를 `IMAGE_DIR`에 넣으면 자동으로 맵 영역만 crop해서 사용합니다.
- 촬영 편차가 있더라도 정규화 좌표 덕분에 동일하게 동작합니다.
- **건물 중심 좌표는 초기 설정 시 한 번만 설정하면 되며, 이후 모든 테스트에서 자동으로 사용됩니다.**
- `BUILDING_CENTERS_NORM` 값을 수동으로 변경할 때마다 저장 후 `main.py`를 다시 실행하세요.
- `MAP_CROP_X1, MAP_CROP_Y1, MAP_CROP_X2, MAP_CROP_Y2` 값도 드론 촬영 각도가 바뀌면 조정이 필요할 수 있습니다.
- 각 섹터 번호(1~9)는 `BUILDING_CENTERS_NORM` 딕셔너리의 키로 저장되어 있어, 좌표별로 섹터 번호가 명확히 매핑됩니다.
- 로그와 좌표 출력은 터미널에 표시되므로, IDE 터미널이나 CMD에서 실행하면 편리합니다.
