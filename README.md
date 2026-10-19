# war-docu — 전쟁사 다큐 자동 제작

대본(스토리보드)만 넣으면 **지도 애니메이션 + 사료 사진 + 재연 일러스트 + 나레이션 + 자막 + 효과음·배경음악**이 들어간 다큐 영상을 GitHub에서 자동으로 만듭니다. PC에 설치할 것은 없습니다.

## 사용한 오픈소스
| 역할 | 오픈소스 / 데이터 |
|---|---|
| 영상 합성·애니메이션 | [Remotion](https://github.com/remotion-dev/remotion) (React 기반 영상 엔진) |
| 지도 투영 | [d3-geo](https://github.com/d3/d3-geo), [topojson](https://github.com/topojson/topojson-client) |
| 국경·해안선 | [Natural Earth](https://www.naturalearthdata.com/) ([world-atlas](https://github.com/topojson/world-atlas)) |
| 지형 음영 | SRTM 고도 ([AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/)) → 자체 hillshade |
| 강·호수 | [OpenStreetMap](https://www.openstreetmap.org/) (Overpass API) |
| 사료 사진 | [Wikimedia Commons](https://commons.wikimedia.org/) (퍼블릭 도메인 미군 사진 등) |
| 폰트 | Black Han Sans, Do Hyeon, Noto Sans KR ([Fontsource](https://github.com/fontsource/fontsource)) |
| 나레이션·효과음·음악 | ElevenLabs API (유료 키) |
| 재연 일러스트 | OpenAI 이미지 API (유료 키) |

## 처음 한 번 설정
1. **Settings → Secrets and variables → Actions → Secrets**
   - `ELEVENLABS_API_KEY`, `OPENAI_API_KEY`
2. 같은 화면의 **Variables** 탭 (선택)
   - `ELEVENLABS_VOICE_ID` : 나레이션 목소리 ID
   - `TTS_SPEED` : 말 빠르기 (기본 1.0, 느리게 0.9)

## 영상 만들기
1. 저장소 위쪽 **Actions** → 왼쪽 **영상 만들기** → **Run workflow**
2. `episode` = `yongmunsan`, `mode` = `full` → 실행
3. 끝나면 저장소 오른쪽 **Releases**에서 MP4 다운로드
   - `preview` 모드: 재료만 만들고 `previews/<에피소드>/sheet_*.jpg` 미리보기만 저장 (렌더링 시간 절약)

비싼 재료(나레이션·이미지·음악)는 저장소에 저장되어, 다시 돌려도 **바뀐 장면만** 새로 만듭니다.
특정 재료를 처음부터 다시 만들려면 `redo` 칸에 `tts` / `photos` / `ai` / `music` 등을 적으세요.

## 수정하는 법
- `episodes/<에피소드>/storyboard.json` — 장면별 대사·화면·자막 강조·효과음
  - 대사 발음 교정: `{"t": "자막 글자", "say": "읽을 발음"}`
- `episodes/<에피소드>/photo_pins.json` — 사진 교체
  - `public/ep/<에피소드>/photos_review.jpg` 에서 후보 번호를 보고 `{"검색어#0": 3}` 처럼 지정
  - 또는 위키미디어 파일명 직접 지정: `{"검색어#0": "File:Korean War 1951.jpg"}`

## 화면 종류 (visual.type)
`map`(지도) · `photo`(사료 사진) · `ai`(재연 일러스트+말풍선) · `person`(인물 카드) · `text` · `black` · `titlecard` · `chapterbig`(요인 카드) · `versus` · `compare` · `bars` · `timeline` · `weekbar` · `gauges` · `document`(문서) · `hanja` · `factors` · `quotes` · `endcard`
