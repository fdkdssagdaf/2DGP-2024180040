# LEC08 애니메이션 뷰어

## 실행

프로젝트의 Python 환경에서 다음 명령을 실행합니다.

```powershell
python LEC08/animation_viewer.py
```

`ESC` 키를 누르면 종료합니다.

## 구성

- `animation_viewer.py`: 중앙에서 대기, 걷기, 점프, 공격 애니메이션을 차례로 재생합니다.
- `character_sheet.png`: 직접 만든 투명 배경 캐릭터 스프라이트 시트입니다.
- `character_sheet.json`: 애니메이션별 프레임 좌표와 프레임 크기입니다.
- `make_sprite_sheet.py`: 시트와 좌표 파일을 다시 생성하는 표준 라이브러리 스크립트입니다.

각 동작은 5회 반복되고 1초 쉰 뒤 다음 동작으로 넘어갑니다. 프레임 수와 프레임 크기는 애니메이션마다 다릅니다. 시트 파일이 없으면 뷰어가 생성기를 실행해 준비합니다.