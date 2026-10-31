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
| 05 춘천 전투 (1950) | `chuncheon` | 3,364자 · 56장면 · target_sec 500 | 8:20.1 · -15.4 LUFS | 8:27.3 · -15.3 LUFS (영문 7,334자) |
| 06 장진호 전투 (1950) | `jangjin` | 3,660자 · 57장면 · target_sec 540 (사용자 요청 9분) | 9:00.1 · -15.3 LUFS | 9:02.0 · -15.3 LUFS (영문 7,564자) |
| 07 베티고지 전투 (1953) | `betty` | 3,333자 · 51장면 · target_sec 495 | 8:15.1 · -15.3 LUFS | 8:14.5 · -15.2 LUFS (영문 6,822자) — 이미지 Gemini |
| 08 영천 전투 (1950) | `yeongcheon` | 3,424자 · 50장면 · target_sec 510 (3,343자 미리보기 8:19 → 보강) | 8:30.1 · -15.2 LUFS | 8:28.4 · -15.3 LUFS (영문 7,064자) |
| 09 피의 능선 전투 (1951) | `bloodyridge` | 3,481자 · 50장면 · target_sec 520 (사용자 요청 8:40) | 8:38.6 · -15.5 LUFS | 8:37.2 · -15.5 LUFS (영문 7,169자 — 6,993자 미리보기 8:28 → 보강) — 새 썸네일 표준 첫 적용 |
| 10 금성 전투 (1953) | `kumsong` | 3,372자 · 47장면 · target_sec 510 | 8:24.3 · -15.4 LUFS | 8:30.1 · -15.4 LUFS (영문 7,221자 — 6,854자 미리보기 8:09 → 보강) — 썸네일 누끼는 세션에서 rembg isnet으로 재처리(Gemini가 가로 그림을 줘 자동 누끼 실패) |

| 11 인천상륙작전과 서울 수복 (1950) — **20분 장편 첫 편** | `incheon` | 약 8,900자 · 93장면 · 8막 · target_sec 1280 | 21:08.5 · -15.1 LUFS | 21:20.1 · -15.1 LUFS (영문 약 18,400자) — 미드롤 3개(`midrolls`), 인천 해안은 DEM 바다·갯벌(`*_sea` 래스터 + 지도 `demSea`), 썸네일 인물은 공개 사진 누끼(`thumb_photo`) |

| 12 단장의 능선 전투 (1951) — 7막 | `heartbreak` | 약 8,300자 · 107장면 · 7막 · target_sec 1230 | 20:30.1 · -15.1 LUFS | 20:45.2 · -15.1 LUFS (영문 약 18,000자) — 지형 `bloody_zoom` 재사용(새 `heartbreak_zoom`은 geo.py에 추가), 썸네일 AI 상징 병사, PNG 2MB 초과로 JPG 전달 |

| 13 파로호(화천) 전투 (1951) — 6막 + 콜드 오프닝 | `paroho` | 약 7,700자 · 98장면 · 6막 · target_sec 1145 | 18:56.9 · -15.1 LUFS | 19:37.4 · -15.1 LUFS (영문 약 17,300자 — 한국어판보다 +40초) — 미드롤은 PART 2·4·6 직전 암전 장면(`s18`·`s42`·`s64`), 1막 끝 Mid-CTA, 지형 `paroho_zoom` 추가, 사진 18장 기존 에피소드 검증분 재사용 핀, EP01 그림 7장 재사용. **썸네일은 사용자 지정 레퍼런스 변형**(`MAPT.paroho`: `floor` 0.38 솔리드 블랙에 2줄 · Line 2 임팩트 레드 `#FF2B2B` · 상단 따옴표 `hook` · `ring` 타깃 링 · `lakes` 호수 칠 · 스탬프 없음) — 다른 에피소드 기본 표준은 그대로 |

| 14 지평리 전투 (1951) — 콜드 오프닝 + 6막 + 에필로그 | `chipyongni` | 약 7,900자 · 105장면 · target_sec 1185 | (렌더 후 기록) | (영문 약 17,900자 · 3,045단어) — 미드롤 `s18`·`s44`·`s81`(PART 2·4·6 직전 암전), 1막 끝 Mid-CTA `s17`, 지형 `jipyeong`/`jipyeong_zoom` 재사용, EP04 그림 9장·사진 21장 재사용(파일·서명 복사), 새 그림 8장 + thumb_subject. 썸네일 `MAPT.chipyongni`는 EP13 변형(floor 0.38 · Line 2 `#FF2828` · ring) |

→ **20분 장편 기준 (EP11 실측)**: 한국어 약 8,900자 = 21분. 렌더 한 편 약 2시간(한+영 약 4시간). 렌더 단계는 `TMPDIR`를 작업 디스크로 돌려야 함(러너 /tmp 용량 한도로 20분 오디오 믹싱 실패 — 수정됨), 실패 시 `logs/render_fail_<ep>.txt`에 로그가 남음. 미드롤·목차 시각은 `logs/midroll_<ep>.txt`

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
   - 확인 항목: **지도 장면에도 하단 자막·콜아웃이 보이는지** (EP10까지 놓친 항목 — 아래 [자막 렌더링 무결성 원칙]), 지도 라벨이 자막에 가리는지(뷰 center 조정), 콜아웃·라벨 겹침, 콜아웃이 얼굴 가림, 사진 중복·라벨 오류, 영문 넘침
   - Actions가 MP4 렌더 직전에 `pipeline/check_subs.py`(자막 노출 검사)를 돌린다. 실패하면 렌더가 멈추고 `logs/errors.txt`에 "자막 안 보임 — <장면> <줄>"이 남는다 → 원인 고친 뒤 재실행
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
   - 길이 8:15~8:30(영문판 +10초까지 허용), 음량 -15 LUFS ±1 (`ffmpeg -af ebur128`), 장면 샘플 프레임 육안 확인(**지도 장면 프레임을 반드시 1장 이상 포함해 자막 확인**), SRT 확인
   - `logs/errors.txt`에 경고가 있으면 원인 해결 후 재실행
9. **썸네일** — ★ **공통 썸네일 표준 (2026-10-25 사용자 확정 · EP09부터 모든 새 에피소드 A안 기본, 새 세션에서도 그대로 적용)**
   - 구현: `remotion/MapThumb.tsx`의 `MAPT` 표에 에피소드 한 줄 추가 → `Thumbnail`이 A안을 이 표준으로 렌더(`Root.tsx`가 자동으로 **1920×1080**).
   - ★★ **기준 결과물 = `thumbnails/bloodyridge_ko_A.png`, `_en_A.png` (2026-10-26 사용자 최종 확정 — "앞으로 썸네일이 이렇게 나오도록")**. 새 에피소드 썸네일은 반드시 이 두 장과 같은 모양·글꼴·배치로 만들고, 렌더 후 나란히 놓고 비교할 것. 사용자가 바꾸라고 하기 전에는 디자인을 임의로 바꾸지 말 것
   - **새 에피소드 썸네일 절차 (체크리스트)**
     1. 대본을 쓰면서 카피 공식(아래)으로 스탬프·Line 1·Line 2를 한·영 함께 정한다
     2. 스토리보드 `ai_images.thumb_subject`에 그 전투의 상징 인물 프롬프트 추가 (흰 배경·허리 위·얼굴 보이게 — 아래 3번 문구)
     3. `MAPT`에 한 줄: `raster`(그 에피소드 `_zoom` 지형), `view`, `items`(전선·능선·핀·화살표 — 스토리보드 좌표 그대로), `stampPos`, `ko`/`en` 카피
     4. 영상 렌더가 끝난 뒤 Actions `mode=thumb` → PNG 두 장을 직접 열어 확인(얼굴 가림·겹침·꽉 찬 글자) → 필요하면 `stampPos`·핀 `lift`·`view`만 조정해 세션 안에서 다시 렌더·커밋
   - **레이어 구조 (1920×1080)**
     1. 배경: 흑백 3D 지형 — 에피소드 지형 래스터(`public/geo/<raster>.webp`, 보통 `<ep>_zoom`)를 `grayscale(1) brightness(0.45) contrast(1.2)` (2026-10-26 수정: 지도 밝기 대폭 하향). `view.span`은 래스터가 2배 넘게 확대되지 않게(질감 뭉개짐) 0.2 안팎
     2. 작전선: 전선 흰 점선(`front`), 핵심 능선·목표(`ridge`), 거점 핀(`pin`, 라벨 겹치면 `lift`), 진격 화살표(`arrow`, red/blue) — 좌표는 스토리보드와 동일하게
     3. 피사체: 전장 핵심 지휘관 또는 상징적 인물 **흑백 누끼**를 **얼굴 위주로 크게**(높이 1100, top -20 — 머리가 화면 위쪽에 닿을 만큼) 우측(`subjectX` 기본 1460)에, 외곽은 흰 림 라이트만(**주황 글로우 금지**, 2026-10-26). 인물 하단은 `mask-image: linear-gradient(to bottom, black 72%, transparent 96%)`로 블랙 바 속으로 사라지게. 실존 인물은 저작권·초상 문제가 없는 공개 사진만, 아니면 상징적 병사를 AI로
        - 그림: 스토리보드 `ai_images.thumb_subject` 프롬프트 — "photorealistic black-and-white, waist-up, face clearly visible and turned slightly toward the left of the frame, isolated on a plain pure white background, no shadows on the background, no text"
        - `mode=thumb`가 그림 생성 후 `rembg`로 배경 제거 → `public/ep/<ep>/ai/thumb_subject.png` (rembg 실패 시 흰 배경 알파로 자동 대체)
     4. 스탬프: 승패의 결정적 요인을 암시하는 붉은 사각 스탬프 — `rotate(-6~-8deg)`, **큼직하게**(2026-10-26: 테두리 6px + 바깥선 3px `#D32F2F`, 글자 한 86px / 영 62px). 지도 위 인물 왼쪽(`stampPos`, 중심 좌표 기준 — EP09는 x 790·y 520). **인물 얼굴·입을 절대 가리지 말 것** (얼굴 옆에 두면 영문처럼 긴 스탬프가 입을 덮음), 블랙 판보다 80px 이상 위에 자동 고정
     5. **하단 구조 = 레퍼런스 '역사 사랑방'과 같은 형태 (2026-10-26 확정)**: **Line 2만** 맨 아래 솔리드 블랙 바(불투명 100% `#000000`, 높이는 Line 2 크기 + 위아래 18px로 자동) 위에. **Line 1은 그 바로 위 사진(지도·인물) 위에** 얹고, Line 1 뒤에만 어두운 띠(`transparent → rgba(0,0,0,.72) → .88`)를 깐다
     6. 텍스트: 좌측 56px부터 2줄 질문형 카피 (구석 정렬 금지). Line 1이 인물 어깨·가슴에 겹치는 것은 레퍼런스와 같아서 OK — 얼굴만 피할 것
   - **타이포그래피·색**
     - 폰트 (2026-10-26 변경 — '눈에 확 띄게'): 한국어 **Pretendard Black(900)** (`public/fonts/Pretendard-Black.woff2`, SIL OFL) / 영문 **Montserrat Black(900)** (@fontsource/montserrat). 둘 다 실제 900 굵기 파일이라 `font-weight: 900` 그대로 사용. 자간 -0.02em. 핀 라벨·스탬프도 같은 글꼴
     - ★ **꽉 찬 글자 (2026-10-26 사용자 요청 — '꽉 차 보이게, 누르고 싶게')**: 글자 크기는 고정 px가 아니라 **실제 글꼴 폭을 재서 가로를 꽉 채우도록 자동 계산**(`useMeasured`). Line 1 = 화면 폭 90%, Line 2 = 92% (상한 150/170px). Line 2는 항상 Line 1보다 8% 이상 크게
     - Line 1 (상황·전제): 스톤 화이트 `#FFFFFF`, 사진 위라서 **굵은 검정 외곽선**(글자 크기의 9%, `paint-order: stroke fill`) + 그림자
     - Line 2 (호기심 질문): 머스터드 옐로 `#FFD000`, 블랙 바 위라 외곽선 없이 깔끔하게
     - 빈틈 없이 빽빽하게. 카피가 짧을수록 글자가 커지므로 Line 2는 10~14자 안팎이 적당
     - ⚠️ 굵기: 예전 글꼴 Black Han Sans·Anton은 단일 굵기 서체라 900을 주면 가짜 볼드로 뭉개짐 — 다시 쓸 일이 있으면 `font-weight: 400`으로
   - **카피 자동 생성 공식 (Curiosity-Gap)** — 새 에피소드 대본·파이프라인을 만들 때 썸네일 카피를 이 공식으로 함께 도출해 `MAPT`에 넣는다
     - 스탬프: [승패를 가른 결정적 요인 2~4단어]
     - Line 1: [압도적 우위·유리했던 상황] + "~하고도 왜"
     - Line 2: [충격적인 패배/승리 결과 질문] + "~했을까?"
     - 영문은 같은 뜻의 질문형 2줄(WHY ... / ...?)
     - ⚠️ **카피·스탬프의 수치는 대본·화면에 쓴 사료 확인 수치만** 사용. 확인 안 된 숫자(예: EP09 제안 '포탄 36만 발' — 출처 미확인)는 넣지 말고, 확인된 사실(결정적 요인 등)로 대체한 뒤 전달 때 알릴 것
   - 생성·렌더: Actions `mode=thumb` → `thumbnails/<ep>_ko_A.png`, `_en_A.png` (영상 재렌더 없음). PNG가 1.9MB를 넘으면 업로드용 `.jpg`(유튜브 2MB 한도)도 자동 생성 — 그 경우 전달은 JPG로 (EP09 최종본 한 1.4MB · 영 1.6MB로 PNG 그대로 업로드 가능). 렌더 후 PNG를 직접 열어 확인: 얼굴 가림 없음, 스탬프·핀·화살표 겹침 없음, 블랙 판 뒤로 아무것도 비치지 않음, Line 2가 가장 크고 노랑, 한글 글자 속이 뭉개지지 않음
   - 아래 '격전의 지도 디자인 시스템'·`split` 레이아웃은 **이전 표준(EP01~08 기록용)** — 새 에피소드에는 쓰지 않는다 (`MAPT`에 항목이 있으면 A안은 항상 새 표준이 우선)
   - (이전 표준 · EP01~08) **한국 채널 '격전의 지도' 썸네일 디자인 시스템 (2026-10-21 확정, 한국어 A안)** — `remotion/Thumbnail.tsx`의 `REF` 표에 에피소드 한 줄 추가로 적용
     1. 3단 텍스트 계층: 상단 `격전의 지도 EP 0X` 회색/흰 박스 태그 → 중단 2색 위기 카피 2줄(흰색/하늘색, **핵심 수치·위기어는 빨강**) → 하단 초대형 메인 키워드(크랙/스톤 질감 굵은 글자, 스타일 red / stone(흰 돌) / yellow(옐로·화이트))
     2. 우측 하단 25%는 재생시간 영역으로 비움 (글자·인물 금지)
     3. 배경: 2D·볼 캐릭터 배제. **흑백 다큐 아카이브 질감 + 붉은/오렌지 화염·포연만 컬러**인 거친 실사풍 전장 극화 → 스토리보드 `ai_images.thumb_ref` 프롬프트 (주제는 중앙~중앙 왼쪽에 전신·얼굴이 보이게 — 아래 `split` 구도 참고)
     4. 생성·렌더: Actions `mode=thumb` (그림 생성 → `thumbnails/<ep>_ko_A.png`, `_ko_B.png` 렌더 → 커밋). 영상 재렌더 없음
     5. B안은 이전 디자인을 A/B 테스트용으로 유지. 카피 수치는 대본·화면 수치와 일치하는지 확인하고 다르면 전달 때 알릴 것
     6. **(2026-10-22 수정) 하단 메인 타이틀 색: 다크 레드 전면 금지** → 머스터드 옐로 `#FFD000`(keyStyle `yellow`, 지명 노랑·'전투' 흰색) 또는 스톤 화이트 `#FFFFFF`(keyStyle `stone`)만 사용 (red·ice 금지)
     7. **(2026-10-22 수정) 배경 밝기**: 순흑(#000) 금지. `thumb_ref` 프롬프트에 "NO crushed pure-black areas, smoke/fog/haze backlit, lifted shadows ~20% brighter, strong rim light outlining soldiers/vehicles" 필수, 우하단은 '어둡게'가 아니라 '안개 낀 빈 공간'으로. 합성 단계도 밝기·대비 +20%(`brightness(1.2) contrast(1.2)`), screen 안개 레이어로 암부 들어올림, 비네트 약하게
   - (이전 표준 · EP08) **좌우 분할 레이아웃 `split`** — EP09부터는 위 공통 썸네일 표준으로 대체
     - 기준 결과물: `thumbnails/yeongcheon_ko_A.png`, `thumbnails/yeongcheon_en_A.png` — 새 편은 이 두 장과 같은 모양으로 만든다
     - 이유: 전체 화면 위에 글자를 얹으면 인물 얼굴을 가린다 (사용자 지적). 그림과 글자를 좌우로 나눠 둘 다 살린다
     - 적용법: `REF`/`REF_EN` 항목에 `split`을 꼭 넣는다 (없으면 예전 겹침 레이아웃이 나옴)
       ```
       yeongcheon: { ep: "08", mid: [...], key: "영천 대역전", keyStyle: "yellow",
         split: { imgX: "22%", midSize: 72, keys: [{ text: "영천", style: "stone", size: 128 }, { text: "대역전", style: "yellow", size: 205 }] } },
       // 영문
       yeongcheon: { ep: "08", mid: [[["THE LAST LINE:", "r"]], [["SAVING THE", "w"]], [["PUSAN PERIMETER", "s"]]], key: "BATTLE OF YEONGCHEON", keyStyle: "stone",
         split: { imgX: "22%", midSize: 78, keys: [{ text: "BATTLE OF", style: "stone", size: 100 }, { text: "YEONGCHEON", style: "yellow", size: 160 }] } },
       ```
     - 화면 구성
       1. **오른쪽 약 60% = 선명한 그림 전용** (글자 금지). 인물 얼굴이 오른쪽 중앙(x≈760~860)에 오도록 `imgX`(그림 가로 위치, 0%=왼쪽 끝)를 조정. 왼쪽 가장자리는 부드럽게 녹아듦
       2. **왼쪽 = 같은 그림을 크게 흐리고 어둡게 깐 포연 패널** (순흑 금지, 왼쪽 아래 붉은 기운) 위에 글자만
       3. 글자 순서(위→아래): 회색 박스 태그 → 위기 카피(한국어 2줄 72px / 영문 3줄 78px, 핵심 위기어 빨강·지명 하늘색) → **하단 키워드 2줄**
       4. **하단 키워드 2줄 공식 (한·영 동일)**: 위 줄 = 흰 돌(`stone`) 작게(한 128px / 영 100px), **맨 아래 줄 = 머스터드 옐로(`yellow`, #FFD000) 가장 크게(한 205px / 영 160px)**. 맨 아래 줄이 반드시 가장 크고 노랑이어야 함 (위 줄이 더 크면 어색하다는 사용자 지적)
          - 한국어 예: `영천`(흰) / `대역전`(노랑). 지명 + 사건 핵심어(대역전·혈전·사수 등) 2~3자 단어로 나눠 쌓기. 맨 아래 줄은 3~4자 이내로 패널 폭 안에 들어가게
          - 영문 예: `BATTLE OF`(흰) / `YEONGCHEON`(노랑). 분할 레이아웃에서는 'Battle of'를 위 줄로 넣어도 됨 (사용자가 자연스럽다고 확인). 지명이 10자를 넘으면 size를 줄여 x 700 안쪽에 맞출 것
       5. 키워드 질감은 `soft`(균열 틈을 흐린 같은 색으로 채움, 시니어 가독성) — `SplitThumb`에서 자동 적용
       6. 우측 하단 25%(x>960, y>540)에는 글자 없음 (재생시간 자리). 그림 쪽 인물 다리·땅이 와도 됨, 얼굴은 금지
     - `thumb_ref` 프롬프트 구도: "the main soldier and vehicle in the center / center-left of the frame, full figure, face clearly visible" — 렌더 시 오른쪽 60%로 잘라 쓰므로 주제가 화면 가장자리에 붙지 않게. 밝기·림 라이트 문구(위 7번)는 그대로 필수
     - 렌더 후 반드시 PNG를 직접 열어 확인: 얼굴 가림 없음, 맨 아래 줄이 가장 크고 노랑, 글자가 패널 밖(x>700)으로 넘치지 않음
   - (이전 표준) **영문판 A안도 같은 배경(`thumb_ref`) 재사용 + [압축 영문 공식]** (2026-10-21) — `REF_EN` 표에 한 줄 추가
     - 폰트 Bebas Neue(좁고 두꺼운 고대비), 태그 `MAP OF WAR EP 0X`, 'Battle of' 전면 제외, 지명·직관적 숫자/단어만 (※ 'Battle of' 제외는 예전 겹침 레이아웃 기준 — 지금 기본인 `split`에서는 위 하단 키워드 2줄 공식이 우선)
     - 중단 2색 카피(빨강 강조 + 시안/흰색), 하단 지명 키워드(red/stone/yellow 크랙 질감). 예: EP01 YONGMUNSAN / EP02 TABU-DONG / EP03 WHITE HORSE / EP04 CHIPYONG-NI
     - 영문 B안은 기존 디자인 유지. `mode=thumb`가 `_en_A.png`도 함께 렌더
   - 렌더링은 세션 안에서: `npx remotion bundle remotion/index.ts --out-dir=/tmp/claude-0/bundle` →
     `npx remotion still /tmp/claude-0/bundle Thumbnail out.png --props='{"ep":"<ep>","variant":"A","lang":"ko"}' --browser-executable=<브라우저>` (브라우저 경로는 `ls -d /opt/pw-browsers/*/`로 확인 — 2026-10-25 기준 `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`)
   - 이전 표준은 1280×720 / 새 표준은 1920×1080. 시니어 가독성 큰 글씨, 어두운 밤 일러스트는 밝기 올리거나 밝은 그림으로 교체, 영문 문구가 화면 밖으로 나가지 않게
   - 결과는 `thumbnails/<ep>_<ko|en>_<A|B>.png`로 커밋
10. **전달** — 사용자에게 한 번에:
    - 한국어판·영문판 Releases 링크 (MP4 500MB 초과 → 링크로), SRT 2개, 썸네일 (새 표준: _ko_A·_en_A 2장 / 이전 에피소드는 A·B 4장) (SendUserFile)
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
| 하단 자막 | 64px, 흰 박스(불투명) + 초록 테두리 `#22594a`(모서리 장식 없음). 한국어 Do Hyeon·한 줄 21자 / 영어 Roboto Condensed·44자. SRT는 다음 줄 시작 전에 끝나게 자동 정리. **루트 글로벌 오버레이에서만 렌더** — 컨테이너 `position:absolute; bottom:60; left:0; right:0; zIndex:9999; pointerEvents:none; display:flex; justifyContent:center` (2026-10-27) |
| 제목 글꼴 | 한국어 Black Han Sans / 영어 Oswald |
| BGM | **`public/bgm/` 공용 6곡 고정** (drone·theme·tension·march·analysis·somber), +2.5dB. **Music API 호출 금지** (`NO_MUSIC_API=1`) |
| 효과음 | `public/sfx/` 공용 캐시 재사용 (새 효과음만 생성) |
| 화면 질감 | 필름 그레인 4프레임마다 갱신, 불투명도 0.09 (파일 용량 때문에 올리지 말 것) |
| 사진 표기 | 우상단 출처(영문판은 자동 영어 변환) + 내용 라벨(연월 포함), AI 그림은 "재연 일러스트 / Dramatization" |
| 유튜브 카테고리 | 교육 |

### [카드 텍스트 줄바꿈 원칙] (2026-10-31 패치 · EP15부터 적용)
- 버그: 비교 카드 키워드가 640px 박스·160px 글자에서 넘쳐 마지막 한 글자만 다음 줄로 밀림 ("압록강 선" / "봉")
- 수정: `Video.tsx` 루트에 `word-break: keep-all` 기본 적용(음절 단위로 쪼개지지 않음). `theme.ts`의 `fitFont(text, maxW, base, min)`이 글자 폭을 추정해 한 줄(`nowrap`/`pre`)에 들어가게 크기를 줄임 — 비교 카드(키워드 5자 이상이면 박스 폭 640→780), 타이틀 카드 제목·부제, 4요인 카드, 교훈 문구에 적용
- 줄을 나누고 싶으면 문구에 `\n`을 직접 넣을 것 (자동 줄바꿈에 맡기지 말 것)

### [자막 렌더링 무결성 원칙] (2026-10-27 사용자 확정 · EP11부터 모든 에피소드 영구 적용)

> - 모든 에피소드는 씬의 종류(MapView, Illustration, DocCard 등)와 무관하게 최상위 글로벌 자막 레이어(`z-index: 9999`)를 통해 음성과 100% 일치하는 싱크로 자막을 화면에 표시해야 한다.
> - 특히 `MapView` 애니메이션 실행 구간에서 자막이 블록되거나 누락되지 않도록 빌드 전 prop 전달 및 컴포넌트 마운트를 검증한다.

- **버그 기록 (EP01~10)**: 확대 지도 장면에서 TTS는 나오는데 자막·콜아웃·우상단 지도 출처가 통째로 안 보였다 (EP10 기준 지도 27줄). 데이터(자막 청크)는 정상이었고, 원인은 `MapView`의 3D 틸트 레이어(`perspective + rotateX`). 확대 지도에서도 전국 래스터(`korea`)가 가로 수만 px로 함께 붙어 이 레이어가 크롬 합성 한계를 넘었고, 그 뒤에 그리는 요소가 전부 사라졌다. z-index만으로는 해결되지 않았다
- **구조 (바꾸지 말 것)**
  1. 자막은 `remotion/Video.tsx` 루트에 `<GlobalSubtitleOverlay scenes={tl.scenes} />` **한 곳에서만** 그린다 (`remotion/ui.tsx`). 장면 Sequence 안에 자막을 다시 넣지 말 것. 싱크는 장면 Sequence와 같은 반올림(`round(start*fps)`)으로 계산
  2. 레이어 순서는 `ui.tsx`의 `Z` 표로 고정: 장면 화면 0 (`isolation: isolate`) < 라벨·콜아웃·챕터 9000 < 필름 그레인 9500 < **자막 9999** < 끝 암전 10000 (마지막 1.2초 페이드아웃만 자막 위)
  3. `MapView` 루트는 `isolation: isolate`, 3D 틸트 컨테이너는 **`overflow: hidden` 필수** (틸트 레이어를 2160×1320으로 잘라 합성 한계 방지). 지도에 새 레이어·래스터를 추가할 때도 이 컨테이너 안에 넣을 것
  4. 새 화면 종류(Visual)를 추가하면 화면 레이어 안에서만 그리고, 화면 전체를 덮는 3D transform·거대 이미지는 같은 방식으로 잘라 둔다
- **검증 (빌드 전)**: `pipeline/check_subs.py <ep> <번들>` — 모든 장면의 모든 줄에서 첫 자막 청크 가운데 시점을 스틸로 렌더해 하단에서 자막 테두리 색 픽셀을 센다. 하나라도 없으면 exit 1. Actions `render-episode.yml`이 미리보기 저장 뒤·MP4 렌더 전에 자동 실행 (preview/full 모두). 세션에서 돌릴 때는 `REMOTION_BROWSER=<크롬 경로>` 지정. 결과 `logs/subs_check_<ep>.txt`
  - 검사기 자체 검증: 수정 전 코드로 EP10을 돌리면 68/95 통과(지도 27줄 실패), 수정 후 95/95 통과 (2026-10-27)
- 기존 배포 영상(EP01~10)은 다시 만들지 않는다 (사용자 지시). 다시 렌더하면 새 구조가 자동 적용됨

---

## 3. 저장소 구조

- `episodes/<ep>/` script.md · storyboard.json · photo_pins.json · scout_queries.json — `<ep>_en/translation.json` (+ 생성된 storyboard.json)
- `pipeline/` photos · ai_images · tts · tighten · sfx · timeline(+SRT) · make_lang · preview · check_subs(자막 노출 검사) · scout · geo · check_api · common
- `remotion/` 영상 컴포넌트 (Video, MapView, Visuals, ui, theme, Thumbnail, Root)
- `public/` geo(지형·하천, 한 번 생성 후 재사용) · bgm · sfx · ui · ep/<ep>/(사진·일러스트·TTS, 저장소에 커밋되어 재사용)
- `previews/` scout_<ep>/ (사진 후보 시트) · <ep>/ (미리보기 시트)
- `thumbnails/` 에피소드별 썸네일 PNG
- Actions: `make-video.yml`(실행용, 한→영. 입력: episode, mode=full/preview/free/check/scout/thumb, english, redo) → `render-episode.yml`(에피소드 1개 렌더)
- 결과: Releases `<ep>-<날짜>` 태그에 `<ep>.mp4`, `<ep>.srt`, 미리보기 시트

## 4. 주의

- Actions 실행 중에는 재료 파일(`public/ep`, `episodes`, `previews`)을 push 하지 말 것 (재료 커밋 충돌). 코드·썸네일처럼 겹치지 않는 파일은 괜찮지만 가급적 실행 후에
- **이미지 엔진 (2026-10-22 변경)**: OpenAI 크레딧 소진 → **Gemini 2.5 Flash Image**(`GEMINI_API_KEY`, AI Studio 선불·Tier 1, 장당 약 55원)가 기본. `ai_images.py`가 GEMINI → Cloudflare(`CF_ACCOUNT_ID`/`CF_API_TOKEN`) → Pollinations(무료, 품질 낮아 썸네일 불가) 순으로 자동 선택, `vars.IMAGE_PROVIDER`로 고정 가능. 기존 그림 서명은 예전 공식 유지(엔진 바꿔도 재생성 없음). 썸네일 배경(`thumb_*`)은 `mode=thumb`에서만 다시 그림. 키·잔액 확인은 `mode=check`(episode는 렌더 중이 아닌 것으로 — 같은 에피소드는 대기열에 묶임) → `logs/api_check.txt`
- 이 세션 환경에서는 ElevenLabs·OpenAI·Gemini·위키미디어 직접 접속 불가 → 해당 작업은 전부 Actions에서. `gh` CLI는 GraphQL 불가, REST(`gh api`)만 사용
- 비용: 일레븐랩스 문자 크레딧(한+영 1편 ≈ 1만 자), OpenAI 이미지 장당 과금 — 재생성은 꼭 필요할 때만 (`redo` 입력). 장면 위치·콜아웃·사진 핀 수정은 TTS·그림 재생성 없이 반영됨
- API 키는 GitHub Secrets(`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`)에만. 대화에 키를 적지 말 것
