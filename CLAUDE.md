# war-docu — 전쟁사 다큐 자동 제작 운영 규칙 (SOP)

사용자는 **주제 또는 대본만** 준다. 그 다음은 이 문서대로 끝까지 자동 진행해서
**한국어판 + 영문판(Tactical Map 채널) 두 개를 바로 렌더링**하고 결과물을 전달한다.
(이전 규칙 "한국어판 완료 후 영문판 진행 여부를 먼저 질문"은 폐지 — 질문 없이 둘 다 진행)

사용자는 PC방에서 작업한다. 로컬 설치를 요구하지 말고 모든 렌더링은 GitHub Actions에서 한다.

---

## 1. 제작 순서 (Claude가 수행)

1. **대본** — `episodes/<ep>/script.md` (파일로 작성)
   - 다큐 성우 톤(~했습니다/~것이죠), 단문, 숫자는 구체적으로, 1차 사료 기반
   - 5단 구조: 훅 → 배경 → 위기 전개 → 승패 요인 분석(숫자) → 결말·인간적 여운 → 구독 요청
   - **분량: 한국어 나레이션 약 3,300자 = 8분 20초** (yongmunsan 기준 실측). 영문 번역은 약 6,700자
   - 불확실한 사실(인물 발언, 포탄 수, 현장 방문 등)은 출처 확인. 못 찾으면 사용자에게 표시해서 알린다
   - 전과 수치는 "한국 측 공식 전사 기준"처럼 출처를 화면·설명에 병기
2. **스토리보드** — `episodes/<ep>/storyboard.json` (형식은 `episodes/yongmunsan/storyboard.json` 참고)
   - 장면 = 나레이션 1~3줄 + 화면 1개. 화면 종류: map / photo / ai / person / text / black / titlecard / chapterbig / versus / compare / bars / timeline / weekbar / gauges / document / hanja / factors / quotes / endcard
   - **0초부터 바로 나레이션** (무음 오프닝 카드 금지, 첫 장면엔 flash 금지)
   - 숫자·부대명은 `{"t": "자막", "say": "읽을 발음"}`으로 발음 지정 (예: 제2연대 → "제이연대")
   - 한 문장 안에서 화면을 바꾸려면 `visuals: [{"atLine": 1, ...}]`
   - 콜아웃이 지도 라벨을 가리면 `pos`("top"/"lower") 또는 `until`(줄 번호)로 조정
   - `music` 큐는 반드시 공용 BGM id만 사용: drone / theme / tension / march / analysis / somber
3. **사료 사진** — Actions `mode=scout` 실행 → `previews/scout/scout_*.jpg` 번호 시트를 직접 보고 고른다
   - 장면별 고유 검색키 `q: "<장면id>-photo"` + `photo_pins.json`에 `"<장면id>-photo#0": "File:정확한파일명.jpg"`
   - 자동 검색 결과를 그대로 쓰지 말 것 (엉뚱한 사진이 많음). 국적·시대가 다른 사진 금지, 라벨은 사진 내용과 일치하게
4. **재연 일러스트** — `ai_images` 프롬프트: 볼(countryball) 캐릭터 반실사 스타일,
   "leaving calm uncluttered dark background area …, absolutely no speech bubbles, no text" 문구 필수 (말풍선은 영상에서 얹음)
5. **영문 번역** — `episodes/<ep>_en/translation.json` (형식은 `episodes/yongmunsan_en/translation.json`)
   - **장면별 줄 수는 한국어판과 반드시 동일** (`make_lang.py`가 검사)
   - 군사 다큐 톤(NARA 기밀해제 문서 스타일), 부대·지명·인포그래픽 1:1 영문 매핑, `places`/`text` 맵 채우기
   - 사진·일러스트·지도·BGM은 한국어판 것을 자동 재사용 (추가 비용 0)
6. **커밋 → 실행**: Actions "영상 만들기" → `episode=<ep>`, `mode=full`, `english=true`
   - 한 번 실행으로 한국어판 → 영문판이 순서대로 렌더링됨
   - 필요하면 먼저 `mode=preview`로 `previews/<ep>/sheet_*.jpg` 확인 후 full
7. **검증 (필수)** — 릴리스 MP4를 REST API로 받아서
   - 길이 8:15~8:30 (자동 맞춤), 음량 -15 LUFS ±1, 장면 샘플 프레임 육안 확인, SRT 확인
   - `logs/errors.txt`에 경고가 있으면 원인 해결 후 재실행
8. **전달** — 사용자에게 한 번에:
   - 한국어판·영문판 Releases 링크 (MP4 500MB 초과 → 링크로), SRT 2개
   - 썸네일 A/B (Remotion `Thumbnail` 컴포지션, 1280×720, 시니어 가독성 큰 글씨)
   - 한국어 제목 후보 2~3개, 설명글(채널명·인사말 넣지 말 것, 목차 타임스탬프는 실제 장면 시각), 태그, 카테고리 '교육'
   - 영문판 제목·설명·태그

---

## 2. 고정 규격 (바꾸지 말 것)

| 항목 | 값 |
|---|---|
| 러닝타임 | **8분 20초 목표** (중간 광고). `timeline.py`가 장면 간격을 0.35~0.55초에서 자동 조정. 10초 넘게 벗어나면 대본 분량 조정 |
| 해상도 / 인코딩 | 1920×1080, 30fps, H.264 `--crf=20 --x264-preset=veryfast`, AAC 192k |
| 음량 | 렌더 후 `loudnorm` -15 LUFS |
| 한국어 나레이션 | ElevenLabs 목소리 `ZJCNdZEjYwkOElxugmW2`, 1.05배속(`tighten.py`, 피치 유지) |
| 영문 나레이션 | ElevenLabs 'Adam' `pNInz6obpgDQGcFmaJgB`, 1.02배속 |
| 무음 | 문장 안 0.45초 넘는 무음 → 약 0.4초로 단축, 장면 사이 ≈ 0.4~0.5초 |
| 하단 자막 | 64px, 흰 박스 + 초록 테두리(모서리 장식 없음). 한국어 Do Hyeon·한 줄 21자 / 영어 Roboto Condensed·44자 |
| 제목 글꼴 | 한국어 Black Han Sans / 영어 Oswald |
| BGM | **`public/bgm/` 공용 6곡 고정** (drone·theme·tension·march·analysis·somber), +2.5dB. **Music API 호출 금지** (`NO_MUSIC_API=1`) |
| 효과음 | `public/sfx/` 공용 캐시 재사용 (새 효과음만 생성) |
| 사진 표기 | 우상단 출처(영문판은 자동 영어 변환) + 내용 라벨, AI 그림은 "재연 일러스트 / Dramatization" |
| 유튜브 카테고리 | 교육 |

---

## 3. 저장소 구조

- `episodes/<ep>/` script.md · storyboard.json · photo_pins.json — `<ep>_en/translation.json`
- `pipeline/` photos · ai_images · tts · tighten · sfx · timeline(+SRT) · make_lang · preview · scout · geo · check_api
- `remotion/` 영상 컴포넌트 (MapView, Visuals, ui, Thumbnail)
- `public/` geo(지형·하천, 한 번 생성) · bgm · sfx · ui · ep/<ep>/(생성 재료, 저장소에 커밋되어 재사용)
- Actions: `make-video.yml`(실행용, 한→영) → `render-episode.yml`(에피소드 1개 렌더)
- 결과: Releases `<ep>.mp4`, `<ep>.srt`, 미리보기 시트

## 4. 주의

- Actions 실행 중에는 저장소에 push 하지 말 것 (재료 커밋 충돌)
- 이 세션 환경에서는 ElevenLabs·OpenAI·위키미디어 직접 접속 불가 → 해당 작업은 전부 Actions에서
- 비용: 일레븐랩스 문자 크레딧(한+영 1편 ≈ 1만 자), OpenAI 이미지 장당 과금 — 재생성은 꼭 필요할 때만 (`redo` 입력)
