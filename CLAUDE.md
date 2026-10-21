# war-docu — 전쟁사 다큐 자동 제작 운영 규칙 (SOP)

사용자는 **주제 또는 대본만** 준다. 그 다음은 이 문서대로 끝까지 자동 진행해서
**한국어판 + 영문판(Tactical Map 채널) 두 개를 바로 렌더링**하고 결과물을 전달한다.
(이전 규칙 "한국어판 완료 후 영문판 진행 여부를 먼저 질문"은 폐지 — 질문 없이 둘 다 진행)

사용자는 PC방에서 작업한다. 로컬 설치를 요구하지 말고 모든 렌더링은 GitHub Actions에서 한다.

## 제작 이력 (기준 실측값)

| EP | id | 나레이션 | 한국어판 | 영문판 |
|---|---|---|---|---|
| 01 용문산 전투·파로호 (1951) | `yongmunsan` | 약 3,300자 · 70장면 | 8:18.6 | 8:20.1 |
| 02 다부동 전투 (1950) | `dabudong` | 3,367자 · 61장면 · target_sec 510 | 8:30.1 · -15.2 LUFS | 8:38.2 · -15.1 LUFS |
| 03 백마고지 전투 (1952) | `baengma` | 3,352자 · 59장면 · target_sec 510 | 8:30.1 · -15.4 LUFS | 8:36.3 · -15.4 LUFS (영문 7,113자) |
| 04 지평리 전투 (1951) | `jipyeong` | 3,332자 · 55장면 · target_sec 505 | 8:24.1 · -15.2 LUFS | 8:21.7 · -15.1 LUFS (영문 6,886자) |

→ 영문판은 한국어판보다 0~8초 길어진다. 영문 번역은 7,100자 안팎이면 +6초 수준 (7,200자는 +13초로 경고). 영문판까지 8:30 안에 넣으려면 한국어 3,300자 안팎으로 맞출 것.

---

## 1. 제작 순서 (Claude가 수행)

1. **대본** — `episodes/<ep>/script.md` (파일로 작성)
   - 다큐 성우 톤(~했습니다/~것이죠), 단문, 숫자는 구체적으로, 1차 사료 기반
   - 구조: 훅(0~50초) → 타이틀 → 1부 배경 → 2부 위기·혈투 → 3부 결정적 전투 → 4부 승패 요인 4가지(숫자) → 에필로그(인간적 여운) → 구독 요청
   - **분량: 한국어 나레이션 3,300~3,370자 = 8분 20초~8분 30초**. 영문 번역은 약 6,700자
   - 사실은 웹 검색으로 확인. 확정 못 한 것(발언 날짜, 직함, 증언성 표현, 좌표 등)은 목록으로 남겨 전달 때 사용자에게 알린다
   - 수치는 "한국 측 기록 기준" / "미군 기록 기준 (기간)"처럼 화면(`note`·콜아웃)과 설명글에 출처 병기
2. **스토리보드** — `episodes/<ep>/storyboard.json` (형식: `episodes/dabudong/storyboard.json`)
   - 장면 = 나레이션 1~3줄 + 화면 1개. 화면 종류: map / photo / ai / person / text / black / titlecard / chapterbig / versus / compare / bars / timeline / weekbar / gauges / document / hanja / factors / quotes / endcard / profile
   - `profile`(EP03 추가): 3D 지형 단면 모식도. `pts`=[[x 0~1, 고도m]…], `pts2`+`erodeAt`/`erodeDur`=포격 침식(숲→흰 산), `bare`=처음부터 벗겨진 색, `marks`(x·text·style·lift), `arrows`(from·to·color), `left`/`right`/`title`/`note`. 번역 필드: title·note·left·right·marks
   - **0초부터 바로 나레이션** (무음 오프닝 카드 금지, 첫 장면엔 flash 금지)
   - 숫자·부대명은 `{"t": "자막", "say": "읽을 발음"}`으로 발음 지정 (예: 1950년 6월 25일 → "천구백오십 년 유월 이십오 일")
   - 한 문장 안에서 화면을 바꾸려면 `visuals: [{"atLine": 1, ...}]` (`from`은 지도 시작 뷰 키라 쓰지 말 것)
   - 지도: `places`(좌표·이름), `views`(center/span), 아이템 `front`/`marker`/`unit`/`arrow`/`text`. 전선·도로 경로는 스토리보드에 직접 좌표로
   - 콜아웃이 지도 라벨·얼굴을 가리면 `pos`("top"=y120 / 기본 y430 / "lower"=y690) 또는 `until`(줄 번호까지만 표시)
   - `music` 큐는 공용 BGM id만: drone(훅) / theme(1부) / tension(2부) / march(3부) / analysis(4부) / somber(에필로그)
   - `target_sec` 기본 500(8:20). 분량이 많으면 510까지
   - **스토리보드를 생성 스크립트로 만들었더라도, 손으로 수정한 뒤에는 스크립트를 다시 돌리지 말 것** (수정 사항이 덮어써짐)
3. **사료 사진**
   - `episodes/<ep>/scout_queries.json`(검색어 50개 안팎, 영문 NARA 캡션 "WAR IN KOREA", 지명 영문 표기 Tabu-dong 등 포함) 작성 후 Actions `mode=scout` → `previews/scout_<ep>/scout_*.jpg` 번호 시트 + `catalog.json`
     (scout 모드는 일부러 실패(exit 1)로 끝남 — 정상)
   - 시트를 직접 보고, `catalog.json`의 설명(desc)으로 내용·날짜를 확인해서 고른다
   - 장면별 검색키 `q: "<장면id>-photo"` + `photo_pins.json`에 `"<장면id>-photo#0": "File:정확한파일명.jpg"`
   - 자동 검색 결과를 그대로 쓰지 말 것. 국적·시대가 다른 사진 금지, **같은 장소·같은 무리를 찍은 사진 두 장 중복 금지**, 라벨은 캡션 내용과 일치하게
   - 핀을 바꾸면 다음 실행 때 그 사진만 다시 받는다
4. **재연 일러스트** — `ai_images` 프롬프트: 볼(countryball) 캐릭터 반실사 스타일,
   "leaving calm uncluttered dark background area …, absolutely no speech bubbles, no text" 문구 필수 (말풍선은 영상에서 얹음). 1편당 8~9장
5. **지형** — 새 지역이면 `pipeline/geo.py`의 `RASTERS`에 bbox·줌 추가 (넓은 지역 z11, 전장 z12, 계곡 근접 z13). `geo.py auto`가 없는 것만 만들고, 하천·호수 bbox가 달라지면 다시 받는다
6. **영문 번역** — `episodes/<ep>_en/translation.json` (형식: `episodes/dabudong_en/translation.json`)
   - **장면별 줄 수는 한국어판과 반드시 동일** (`python3 pipeline/make_lang.py <ep> <ep>_en en`으로 로컬 검사)
   - 군사 다큐 톤(NARA 기밀해제 문서 스타일), 부대·지명 1:1 영문 매핑, `places`/`text` 맵에 지도 아이템 문구 전부
   - 장면 타입별 필드: label, callouts, chapter, bubbles, big/sub, text/accent, title/sub, name/role, items/head(factors), num/title(chapterbig), left/right, note/bars, quotes/quoteTitle
   - 위치 조정은 `callout_pos` / `callout_until` 맵
   - 사진·일러스트·지도·BGM·효과음은 한국어판 것을 자동 재사용 (추가 비용 0)
7. **커밋 → 미리보기 → 본 렌더링**
   - Actions "영상 만들기" → `episode=<ep>`, `mode=preview`, `english=true` → `previews/<ep>/`, `previews/<ep>_en/` `sheet_*.jpg` 전부 육안 확인
   - 확인 항목: 지도 라벨이 자막에 가리는지(뷰 center 조정), 콜아웃·라벨 겹침, 콜아웃이 얼굴 가림, 사진 중복·라벨 오류, 영문 넘침
   - 고친 뒤 `mode=full`, `english=true` (한 번 실행으로 한국어판 → 영문판 순서대로, 약 70분)
   - 이 세션에서는 GraphQL이 막혀 `gh workflow run` 불가 → REST로 실행:
     `gh api -X POST repos/korea1278/war-docu/actions/workflows/make-video.yml/dispatches -f ref=main -f 'inputs[episode]=<ep>' -f 'inputs[mode]=full' -f 'inputs[english]=true'`
   - **렌더링 요청(dispatch)이 접수된 직후 보내는 사용자 답변의 맨 첫 줄**에, 다른 설명보다 먼저 아래 안내를 그대로 출력할 것 (사용자가 PC방 컴퓨터를 끌 수 있게):
     ```
     ## 🛑 [안내] GitHub Actions 렌더링이 서버에 안착했습니다. 이제 피시방 컴퓨터를 끄셔도 됩니다!
     - 실행된 워크플로우: <에피소드명>
     - 진행 상태: In progress (클라우드 연산 중)
     ```
8. **검증 (필수)** — 릴리스 MP4를 REST API로 받아서
   - `curl -L -H "Authorization: token $(gh auth token)" -H "Accept: application/octet-stream" https://api.github.com/repos/korea1278/war-docu/releases/assets/<id>`
   - 길이 8:15~8:30(영문판 +10초까지 허용), 음량 -15 LUFS ±1 (`ffmpeg -af ebur128`), 장면 샘플 프레임 육안 확인, SRT 확인
   - `logs/errors.txt`에 경고가 있으면 원인 해결 후 재실행
9. **썸네일** — `remotion/Thumbnail.tsx`에 에피소드별 A/B 디자인 추가 (`ep.startsWith("<ep>")`로 분기, `lang="en"`이면 영문)
   - **한국 채널 '격전의 지도' 썸네일 디자인 시스템 (2026-10-21 확정, EP01~ 전체 적용 · 한국어 A안)** — `remotion/Thumbnail.tsx`의 `REF` 표에 에피소드 한 줄 추가로 적용
     1. 3단 텍스트 계층: 상단 `격전의 지도 EP 0X` 회색/흰 박스 태그 → 중단 2색 위기 카피 2줄(흰색/하늘색, **핵심 수치·위기어는 빨강**) → 하단 초대형 메인 키워드(크랙/스톤 질감 굵은 글자, 스타일 red / stone(흰 돌) / yellow(옐로·화이트))
     2. 우측 하단 25%는 재생시간 영역으로 비움 (글자·인물 금지)
     3. 배경: 2D·볼 캐릭터 배제. **흑백 다큐 아카이브 질감 + 붉은/오렌지 화염·포연만 컬러**인 거친 실사풍 전장 극화 → 스토리보드 `ai_images.thumb_ref` 프롬프트 (주제는 중앙·좌상단, 우하단은 어둡게 비우라는 문구 포함)
     4. 생성·렌더: Actions `mode=thumb` (그림 생성 → `thumbnails/<ep>_ko_A.png`, `_ko_B.png` 렌더 → 커밋). 영상 재렌더 없음
     5. B안은 이전 디자인을 A/B 테스트용으로 유지. 카피 수치는 대본·화면 수치와 일치하는지 확인하고 다르면 전달 때 알릴 것
   - **영문판 A안도 같은 배경(`thumb_ref`) 재사용 + [압축 영문 공식]** (2026-10-21) — `REF_EN` 표에 한 줄 추가
     - 폰트 Bebas Neue(좁고 두꺼운 고대비), 태그 `MAP OF WAR EP 0X`, 'Battle of' 전면 제외, 지명·직관적 숫자/단어만
     - 중단 2색 카피(빨강 강조 + 시안/흰색), 하단 지명 키워드(red/stone/yellow 크랙 질감). 예: EP01 YONGMUNSAN / EP02 TABU-DONG / EP03 WHITE HORSE / EP04 CHIPYONG-NI
     - 영문 B안은 기존 디자인 유지. `mode=thumb`가 `_en_A.png`도 함께 렌더
   - 렌더링은 세션 안에서: `npx remotion bundle remotion/index.ts --out-dir=/tmp/claude-0/bundle` →
     `npx remotion still /tmp/claude-0/bundle Thumbnail out.png --props='{"ep":"<ep>","variant":"A","lang":"ko"}' --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`
   - 1280×720, 시니어 가독성 큰 글씨, 어두운 밤 일러스트는 밝기 올리거나 밝은 그림으로 교체, 영문 문구가 화면 밖으로 나가지 않게
   - 결과는 `thumbnails/<ep>_<ko|en>_<A|B>.png`로 커밋
10. **전달** — 사용자에게 한 번에:
    - 한국어판·영문판 Releases 링크 (MP4 500MB 초과 → 링크로), SRT 2개, 썸네일 4장 (SendUserFile)
    - 한국어 제목 후보 3개(썸네일 A/B용 표시), 설명글, 태그(쉼표 구분), 카테고리 '교육'
    - 영문판 제목 3개·설명·태그
    - 설명글 규칙: 채널명·인사말 넣지 말 것, 시니어 시청자가 읽기 쉽게 자세히, **목차 타임스탬프는 SRT에서 각 부 첫 줄의 실제 시각**, 참고 자료 목록, 수치 출처·재연 일러스트 고지, 해시태그 3개
    - 사실 확인에서 확정 못 한 항목 목록

---

## 2. 고정 규격 (바꾸지 말 것)

| 항목 | 값 |
|---|---|
| 러닝타임 | **8분 20초~8분 30초** (중간 광고). `timeline.py`가 장면 간격을 0.35~0.55초에서 자동 조정해 `target_sec`에 맞춤. 10초 넘게 벗어나면 대본 분량 조정 |
| 해상도 / 인코딩 | 1920×1080, 30fps, H.264 `--crf=20 --x264-preset=veryfast --concurrency=4`, AAC 192k |
| 음량 | 렌더 후 `loudnorm` -15 LUFS |
| 한국어 나레이션 | ElevenLabs 목소리 `ZJCNdZEjYwkOElxugmW2`, 1.05배속(`tighten.py`, 피치 유지) |
| 영문 나레이션 | ElevenLabs 'Adam' `pNInz6obpgDQGcFmaJgB`, 1.02배속 |
| 무음 | 문장 안 0.45초 넘는 무음 → 약 0.42초로 단축, 장면 사이 0.35~0.55초 |
| 하단 자막 | 64px, 흰 박스 + 초록 테두리(모서리 장식 없음). 한국어 Do Hyeon·한 줄 21자 / 영어 Roboto Condensed·44자. SRT는 다음 줄 시작 전에 끝나게 자동 정리 |
| 제목 글꼴 | 한국어 Black Han Sans / 영어 Oswald |
| BGM | **`public/bgm/` 공용 6곡 고정** (drone·theme·tension·march·analysis·somber), +2.5dB. **Music API 호출 금지** (`NO_MUSIC_API=1`) |
| 효과음 | `public/sfx/` 공용 캐시 재사용 (새 효과음만 생성) |
| 화면 질감 | 필름 그레인 4프레임마다 갱신, 불투명도 0.09 (파일 용량 때문에 올리지 말 것) |
| 사진 표기 | 우상단 출처(영문판은 자동 영어 변환) + 내용 라벨(연월 포함), AI 그림은 "재연 일러스트 / Dramatization" |
| 유튜브 카테고리 | 교육 |

---

## 3. 저장소 구조

- `episodes/<ep>/` script.md · storyboard.json · photo_pins.json · scout_queries.json — `<ep>_en/translation.json` (+ 생성된 storyboard.json)
- `pipeline/` photos · ai_images · tts · tighten · sfx · timeline(+SRT) · make_lang · preview · scout · geo · check_api · common
- `remotion/` 영상 컴포넌트 (Video, MapView, Visuals, ui, theme, Thumbnail, Root)
- `public/` geo(지형·하천, 한 번 생성 후 재사용) · bgm · sfx · ui · ep/<ep>/(사진·일러스트·TTS, 저장소에 커밋되어 재사용)
- `previews/` scout_<ep>/ (사진 후보 시트) · <ep>/ (미리보기 시트)
- `thumbnails/` 에피소드별 썸네일 PNG
- Actions: `make-video.yml`(실행용, 한→영. 입력: episode, mode=full/preview/free/check/scout/thumb, english, redo) → `render-episode.yml`(에피소드 1개 렌더)
- 결과: Releases `<ep>-<날짜>` 태그에 `<ep>.mp4`, `<ep>.srt`, 미리보기 시트

## 4. 주의

- Actions 실행 중에는 재료 파일(`public/ep`, `episodes`, `previews`)을 push 하지 말 것 (재료 커밋 충돌). 코드·썸네일처럼 겹치지 않는 파일은 괜찮지만 가급적 실행 후에
- 이 세션 환경에서는 ElevenLabs·OpenAI·위키미디어 직접 접속 불가 → 해당 작업은 전부 Actions에서. `gh` CLI는 GraphQL 불가, REST(`gh api`)만 사용
- 비용: 일레븐랩스 문자 크레딧(한+영 1편 ≈ 1만 자), OpenAI 이미지 장당 과금 — 재생성은 꼭 필요할 때만 (`redo` 입력). 장면 위치·콜아웃·사진 핀 수정은 TTS·그림 재생성 없이 반영됨
- API 키는 GitHub Secrets(`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`)에만. 대화에 키를 적지 말 것
