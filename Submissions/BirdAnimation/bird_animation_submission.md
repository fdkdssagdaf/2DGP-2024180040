# 새의 비행 애니메이션 구현 보고서

## 과제 개요

이번 과제는 10마리의 새가 좌우로 반복적으로 비행하는 애니메이션을 구현하는 것이다. 새는 단순히 화면을 이동하는 것이 아니라, `bird_animation.png`의 스프라이트 시트를 이용해 날개 프레임을 순서대로 교체하며 실제로 퍼덕이는 듯한 효과를 보여야 한다. 또한 새가 화면 가장자리에서 반대편으로 다시 나타나도록 하여 연속적인 비행을 구현하였다.

## 구현 내용

- `bird_animation.png`를 로드하여 스프라이트 시트를 분리한다.
- 각 새는 위치, 속도, 방향, 프레임 인덱스, 타이머를 가진다.
- 일정 시간마다 날개 프레임을 변경하여 비행 애니메이션을 구현한다.
- 새가 화면 경계를 벗어나면 반대편으로 재배치하여 좌우 반복 비행 효과를 만든다.
- 이동 방향에 따라 이미지를 좌우 반전하여 자연스러운 비행 방향감을 표현한다.
- 10마리 새를 각각 다른 속도와 타이밍으로 배치하여 군집 비행처럼 보이게 한다.

## 개발 로직

새의 비행은 단순히 x 좌표를 이동시키는 것만으로는 부족하다. 실제로 비행을 보여주기 위해 스프라이트 프레임을 시간 기반으로 전환하는 로직이 필요하다. 매 프레임마다 타이머를 증가시키고, 일정 시간 이상이면 다음 프레임으로 변경한다. 이 과정이 반복되면 날개가 퍼덕이는 동작처럼 보인다.

또한 새가 화면 왼쪽 또는 오른쪽 경계를 벗어날 경우 위치를 반대편으로 재설정한다. 이 방식으로 새는 화면을 계속 왔다 갔다하면서 좌우 반복 비행을 수행한다. 방향에 따라 이미지를 좌우 반전시켜 새가 왼쪽으로 날아갈 때와 오른쪽으로 날아갈 때 모두 자연스럽게 보이도록 하였다.

## 최종 제출용 커밋 메시지

```text
feat: implement Pico-2D style 10-bird flight animation using bird_animation.png

- split the sprite sheet into sequential wing frames
- animate wing flapping with a timer-based frame cycle
- move each bird horizontally with looping wraparound motion
- flip the sprite for left/right direction changes
- control 10 birds individually with independent speed and timing
- create a natural flock-like flight effect in a 2D game scene
```

## 최종 설명 문장

10마리의 새는 bird_animation.png의 프레임을 순서대로 재생하며 날개를 퍼덕이고, 좌우 이동과 화면 경계 처리, 방향 반전을 통해 반복적인 비행 애니메이션을 구현하였으며, 각 새마다 다른 속도와 위치를 부여해 자연스러운 군집 비행 효과를 만들었다.
