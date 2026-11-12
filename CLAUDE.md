# war-docu — 전쟁사 다큐 자동 제작 운영 규칙 (SOP)

사용자는 **주제 또는 대본만** 준다. 그 다음은 이 문서대로 끝까지 자동 진행해서
**한국어판 + 영문판(Tactical Map 채널) 두 개를 바로 렌더링**하고 결과물을 전달한다.
> ⚠️ **2026-10-31 사용자 지시 (EP15부터)**: TTS 크레딧 절약·국내 5060 시청층 집중을 위해 **영문판 제작 전면 제외 — 한국어 단일 버전만** 만든다. 영문 번역(`<ep>_en/translation.json`)을 만들지 말고, Actions는 `english=false`로 실행한다. 사용자가 다시 영문판을 요청하기 전까지 이 지시가 아래 규칙보다 우선한다.
> ⚠️ **2026-11-12 고정 규칙 (사용자 지시)**: **영문판은 사용자가 요청할 때만 제작**하고, **영문판은 별도 저장소 `korea1278/map-of-war`(《Map of War》 영문 전용)에서 만든다**. 이 저장소(war-docu)는 한국어 '격전의 지도' 전용 — 새 영문 편·번역판을 여기에 넣지 않는다 (기존 `_en` 폴더는 기록용으로 유지). 영문 작업 지시가 오면 map-of-war를 세션에 연결해서 진행.
(이전 규칙 "한국어판 완료 후 영문판 진행 여부를 먼저 질문"은 폐지 — 질문 없이 둘 다 진행)

사용자는 PC방에서 작업한다. 로컬 설치를 요구하지 말고 모든 렌더링은 GitHub Actions에서 한다.

> 📌 **필수 참조 — `docs/LONGFORM_STANDARD.md` (2026-11-13 사용자 지시 · 롱폼 영구 표준)**: 새 롱폼은 대본·스토리보드를 만들기 전에 이 문서를 먼저 읽고 따른다 — 막 단위 통파일 TTS(`"tts_mode": "act"`), **절제된 다큐 효과음(`"sfx_policy": "doc"` · '꽝' 타격음·UI pop 금지, 같은 소리 15초 쿨다운, 막 전환·3D 비행 스윕·클라이맥스 먼 포성/바람 앰비언스·핵심 록온 레이더 핑만 나레이션 대비 -24~-32dB)**, BGM은 나레이션 대비 -22~-26dB(`"bgm_rel_db": -24`), 자막 싱크 ±0.5초·한 줄 25~35자, frame 기반 결정론 렌더. 이 문서의 아래 규칙과 부딪히면 LONGFORM_STANDARD.md가 우선한다 (예: 아래 '효과음' 행, 스토리보드 `sfx` 사용 예시)

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

| 14 지평리 전투 (1951) — 콜드 오프닝 + 6막 + 에필로그 | `chipyongni` | 약 7,900자 · 105장면 · target_sec 1185 | 19:33 (logs 기준) | (영문 약 17,900자 · 3,045단어) — 미드롤 `s18`·`s44`·`s81`(PART 2·4·6 직전 암전), 1막 끝 Mid-CTA `s17`, 지형 `jipyeong`/`jipyeong_zoom` 재사용, EP04 그림 9장·사진 21장 재사용(파일·서명 복사), 새 그림 8장 + thumb_subject. 썸네일 `MAPT.chipyongni`는 EP13 변형(floor 0.38 · Line 2 `#FF2828` · ring) |

| 15 흥남 철수 작전 (1950) — 콜드 오프닝 + Early-CTA + 6막 · **한국어 단일 제작(영문판 제외, 사용자 지시 2026-10-31)** | `hungnam` | 약 8,170자 · 108장면 · target_sec 1190 (첫 렌더 7,980자 = 19:20 → 목표 19:30~20:00 미달로 보강) | 19:44.8 · -15.2 LUFS | 없음 — 미드롤 `s25`·`s55`·`s88`(PART 2·4·6 직전 암전), **Early-CTA `s08`(콜드 오프닝 직후 · 새 화면 `cta`: 큼직한 구독·좋아요 카드)**, 엔딩 CTA `s107`, 지형 `hungnam2_sea`/`hungnam2_zoom_sea` 추가 — **북한 동해안 DEM은 바다가 0m라 기존 `sea` 옵션이 바다를 갈색 갯벌·저지대를 얼룩으로 칠함 → `seeds`(바다 좌표) flood fill로 바다만 칠하는 옵션 추가**, EP06 그림 5장 재사용(파일·서명 복사), 사진 28장 스카우트 핀. 썸네일 `MAPT.hungnam`은 EP13·14 변형 + `textW` 0.8(우측 하단 재생시간 배지 여백) |

| 16 낙동강 방어선 총력전 (1950) — 콜드 오프닝 + Early-CTA + PART 1~7 + 에필로그 · **한국어 단일 제작** · 목표 23분 | `naktong` | 약 9,530자 · 136장면 · target_sec 1380 (사용자 지정 8,800자는 실측 환산 약 21분이라 23분 사수를 위해 보강) | (렌더 후 기록) | 없음 — 미드롤 `s28`·`s65`·`s95`(PART 2·4·6 직전 암전), Early-CTA `s08`, 엔딩 CTA `s136`, 지도 45컷, 지형 `naktong_bulge`/`masan_zoom`/`waegwan_zoom` 추가, 낙동강 본류는 `water.json`에서 이어 붙인 `line`(glow)으로 강조, EP02·08·11 그림 7장 재사용(파일·서명 복사) + 새 그림 11장, 사진 36장 스카우트 핀, 썸네일 `MAPT.naktong`(EP13~15 변형 · 인물은 워커 중장 공개 사진 `thumb_photo`) |

| 16 도솔산 전투 (1951) — 무적해병의 탄생 · 콜드 오프닝 + Early-CTA + 6막 · **한국어 단일 · 독백체(~했다, 사용자 지정)** | `ep16-dosolsan` | 8,498자 · 112장면 · target_sec 1230 (사용자 지정 8,500~9,000자 · 19분 — 실측 환산상 8,500자는 약 20분 30초) | (렌더 후 기록) | 없음 — ※ 사용자가 이 편을 'EP 16'으로 지정(낙동강 `naktong`과 번호 겹침). 미드롤 `s24`·`s56`·`s92`(제2·4·6막 직전 암전), Early-CTA `s08`, 엔딩 `s112`. **지도 새 기능**: 아이템 `obj`(목표 번호 링 · `n`, `takenAt`=줄 번호부터 푸른색+체크, `text`), `clash`(백병전 타격 플래시+폭발 링 반복 · `period`, `size`), 화면 `tilt`(도 · 16→지정값으로 1.6초 동안 기울임, 45도까지 확인 — 위쪽 빈 띠 방지용 scale·origin 자동). 지형 `dosol_zoom`(z14) 추가. 사진 17장 기존 에피소드 검증분 재사용(파일·서명 복사), 그림 2장 EP09 재사용 + 새 그림 12장(thumb_subject 포함). 목표 1~24 위치는 모식 배치(15 대암산 · 22 도솔산만 사료 번호). 썸네일 `MAPT["ep16-dosolsan"]`은 EP09 표준(스탬프+블랙 바) + **카피 시안 `alts` → `_ko_A2`·`_ko_A3`도 렌더** |

| 17 금성 전투 (1953) — 휴전 직전 최후의 결전 · 콜드 오프닝 + Early-CTA + 제1~8막 · **한국어 단일 · 독백체 · 목소리 ElevenLabs Minho(`U1cJYS4EdbaHmfR7YzHd`, 사용자 지정 — 스토리보드 `voice`)** · 목표 22분 | `ep17-kumsong` | 9,446자 · 115장면 (첫 미리보기 9,840자 = 22:54 → 5장면 삭제 · **Minho 1.05배속 실측 약 7.16자/초**) · target_sec 1320 (사용자 지정 약 10,000자) | 22:00.5 · -15.3 LUFS · 1.36GB (렌더 약 2시간 45분) | 없음 — EP10 `kumsong` 22분 확장판. 미드롤 `s34`·`s63`·`s94`(제3·5·7막 직전 암전), Early-CTA `s08`. **지도 새 기능 (전술 HUD, Lottie 대신 SVG 네이티브)**: `radar`(포병 발사 원점 레이더 스윕 · `size`, `color`, `text`), `shock`(연속 탄착 충격파 · `pts` 여러 점, `period`), `lock`(타깃 락온 브래킷 점멸 · `text`). 금성천은 시안 `#00E5FF` 네온 `line`(glow, 개략 좌표). EP10 그림 9장 재사용(파일·서명 복사) + 새 그림 6장, 사진 20장 기존 에피소드 검증분 재사용 + 펑더화이 공개 사진(`File:General Peng Dehuai.jpg`, 장면 `s14` + `thumb_photo`). 썸네일 `COLLAGE["ep17-kumsong"]`(v4 · 중공군 깃발 `cn` 추가 · 말풍선 `\n` 줄바꿈 지원) |

| 18 군우리 전투 & 청천강 철수전 (1950) — 인디언 태형 협곡(The Gauntlet) · 콜드 오프닝 + Early-CTA + 제1~7막 · **한국어 단일 · 독백체 · Minho** · 목표 21:30 | `ep18-kunuri` | 9,237자 · 109장면 · target_sec 1290 (미리보기 실측 21:30.0 — EP17 Minho 7.16자/초 환산으로 첫 미리보기에 맞음) | (렌더 후 기록) | 없음 — 사용자 지시서의 `src/data/ep18_script.json`·`generate_ep18_audio.py`·Lottie HUD는 이 저장소 파이프라인(storyboard.json·tts.py·지도 `radar`/`shock`/`lock`)으로 대응. 미드롤 `s35`·`s69`·`s93`(제3·5·7막 직전 암전). 지형 `chongchon`(z11)·`kunuri`(z12)·`gauntlet_zoom`(z14) 추가, 하천 `WEXTRA.chongchon`(첫 실행 Overpass 504로 실패 — 다음 실행 때 재시도). 협곡 도로·매복 고지 좌표는 개략. 사진 9장 기존 에피소드 검증분 재사용 + 13장 스카우트 핀, 그림 8장 EP06·14 재사용(파일·서명 복사) + 새 그림 12장. 사단장은 지시서의 '로버트 케이플러'가 아니라 실제 사단장 **로런스 카이저 소장**(공개 공식 초상 → 세션 rembg 누끼 `thumb_subject.png`). 썸네일 `COLLAGE["ep18-kunuri"]`(v4 · `sizes` [92,112] 옵션 추가) |

| 19 철의 삼각지대: 저격능선 & 삼각고지 (1952) — 쇼다운 작전 · 콜드 오프닝 + Early-CTA + 제1~7막 · **한국어 단일 · 독백체 · Minho** · 목표 20:00 | `ep19-sniper-ridge` | 8,500자 · 101장면 · target_sec 1200 (8,538자 미리보기 20:02~20:05 → 1줄 삭제 + 엔드카드 tail 3.0→1.0) | (렌더 후 기록) | 없음 — 미드롤 `s31`·`s55`·`s81`(제3·5·7막 직전 암전, 다음 장면에 `chapter`를 달아야 목차·미드롤 라벨이 나옴). 지형 `sniper_zoom`(z15) 추가, 지도 `obj`로 A고지·Y고지·돌바위·598고지 쟁탈 표시(좌표 개략). 그림 10장 baengma·bloodyridge·heartbreak·ep17 재사용(파일·서명 복사) + 새 그림 8장 + thumb_subject(세션 rembg isnet → `thumb_cut.png`), 사진 16장 전부 기존 에피소드 검증분 재사용(스카우트는 러너 설치 단계 멈춤으로 취소). **새 검사 `pipeline/check_sync.py`** — 장면별 목소리 끝(silencedetect) vs 마지막 자막 끝, 영상 전체 마지막 자막(SRT) vs 마지막 목소리 오차 ±1.0초 (사용자 지시), Actions에서 자막 노출 검사 다음·MP4 렌더 전 자동 실행, 결과 `logs/sync_check_<ep>.txt`. 썸네일 `COLLAGE["ep19-sniper-ridge"]` — **v4 개선 옵션**: 말풍선 `tailStyle: "short"`(좌측 하단 15~20px 짧은 꼬리, 긴 꼬리 폐지), `dim`(하단 딤 압축 `#000 0~38% → .85 55% → .4 70% → 투명`), `sizes` [108,112], 카피 시안 `alt` → `_ko_A2`. 지시서의 '포탄 28만 발·수류탄 20만 발'은 사료 미확인 — 나레이션은 중국 측 기록 190만여 발 등 확인 수치만, 썸네일 A는 지시 문구 그대로·A2는 190만 발 |

| 20 임진강(설마리) 전투 (1951) — 글로스터 대대 최후 항전 · 제1~7막 · **한국어 단일 · Minho** · 목표 20:30 | `ep20-imjin-river` | 8,909자 · 126장면 · target_sec 1230 (첫 미리보기 8,719자 = 19:59 → `s25b`·`s108b` 추가, 장면 번호 유지로 기존 TTS 재사용) | 20:25.1 · -15.2 LUFS · 1.26GB · 자막 286/286 · 싱크 ±1.0초 통과 | 없음 — 미드롤 `s37`·`s70`·`s107`. 지형 `imjin_w`(z12)·`gloster_zoom`(z14) 추가 — **z14 래스터는 뷰 span 0.1 이상**(0.06이면 2.7배 확대로 뭉개짐). 사진 15장 스카우트 핀(칸 중령·커티스 묘비·영국군 포로·설마리 전적비·75주년 추모식 등), 새 그림 47장. 썸네일 `COLLAGE["ep20-imjin-river"]` + **유니언 잭 깃발 `uk` 추가**, 인물은 AI 글로스터 베레모 병사(세션 rembg → `thumb_cut.png`) |

| 21 가평 전투 (1951) — 영연방 제27여단 · 제1~7막 · **한국어 단일 · Minho · 쇼츠 제작 안 함(사용자 지시)** · 목표 20:30 | `ep21-gapyeong` | 9,017자(대본) · 122장면 · target_sec 1230 (첫 미리보기 8,789자 = 19:58 → `s25b`·`s74b`·`s115b` 추가, 장면 번호 유지) | 20:28.1 · -15.2 LUFS · 1.27GB · 자막 260/260 · 싱크 ±1.0초 통과 | 없음 — 미드롤 `s36`·`s70`·`s104`(제3·5·7막 직전 암전). 구독 CTA 1 = 3막 끝 `cta` 장면 `s53`, 구독 CTA 2 = 7막 끝(EP22 포크찹 고지 예고 뒤). **새 기능: 장면 필드 `hudCta: {at, dur}`** → 오른쪽 위 전술 HUD 구독·좋아요 오버레이(`ui.tsx` `HudCta`, 4막 `s58` 지도 위). 지형 `gapyeong_zoom`(z14) 추가, 고지·하천 좌표는 개략. 스토리보드는 `make_board.py`가 script.md 문장을 순서대로 가져와 생성(자막 숫자 표기는 `SUBS` 표). 사진 17장 스카우트 핀 — ⚠️ 핀이 빠진 사진 장면은 장면 id로 자동 검색돼 엉뚱한 사진(예: `s117` → STS-117 우주왕복선)이 들어옴. 사진 장면마다 핀 확인 필수. 썸네일 `COLLAGE["ep21-gapyeong"]` — mode=thumb의 `thumb_subject.png`가 이미 투명 누끼라 그대로 사용, 지도 `thumbc/detail`·`gapyeong_zoom`은 세션에서 `thumb_color.py`로 생성. 계곡 규모 지도엔 손으로 그린 하천·도로 선 대신 실제 하천 데이터만 사용(어긋남 방지) |

| 22 포크찹 고지 전투 (1953) — 강뉴 대대 · 제1~7막 · **한국어 단일 · Minho · 쇼츠 없음** · 목표 20:30 | `ep22-pork-chop-hill` | 8,915자(대본) · 132장면 · target_sec 1230 (사용자 지시 6,000~6,500자는 약 14분이라 EP20·21처럼 8,900자로 작성) | 20:22.8 · -15.2 LUFS · 1.26GB · 자막 253/253 · 싱크 ±1.0초 통과 | 없음 — 미드롤 `s37`·`s76`·`s112`, CTA1 `s55`(cta), HUD 오버레이 `s67`, EP23 장사상륙작전 예고. 지형 `porkchop_zoom`(z14) 추가, 고지·전초 좌표 전부 개략. 사진 22장 스카우트 핀, 새 그림 44장(학도병·클레먼스 2장은 프롬프트 수정 재생성 — 학도병은 "NO stars, NO red insignia" 없으면 북한군 복장으로 나옴). **photo 장면에 `pos`(objectPosition) 옵션 추가** — 세로 사진 얼굴 잘림 방지. 썸네일 `COLLAGE["ep22-pork-chop-hill"]` + **에티오피아 삼색기 `et`** 추가, 인물은 1953년 강뉴 대대원 사료 사진(`Ethiopian Soldiers Korean War.jpg`) 세션 rembg 누끼(`thumb_cut.png`). 지시서의 '강뉴 대대가 포크찹 포위망을 뚫고 역습'은 사료 미확인 → 4. 17~18 역습은 미 제7사단(클레먼스 킹 중대)으로, 강뉴 대대는 같은 밤 철원 서쪽 전투·티본 정찰(마셜)·5월 요크 고지 백병전으로 구성 |

| 23 장사상륙작전 (1950) — 학도병 문산호 결사대 · 콜드 오프닝 + 제1~6막 · **한국어 단일 · Minho · 쇼츠 없음** · 목표 20:00 | `ep23-jangsari` | 8,912자(대본, 공백 제외 6,752자) · 127장면 · target_sec 1200 (공백 제외 6,466자 = 19:08 → `s16b`·`s16c`·`s31b`·`s111b` 추가) | 19:58.7 · -15.1 LUFS · 1.23GB · 자막 노출·싱크 검사 통과 | 없음 — 미드롤 `s38`·`s76`·`s95`, CTA1 `s51`(cta), HUD 오버레이 4막 지도(7번 국도), EP24 피의 능선 예고. 지형 `jangsa_sea`(z12)·`jangsa_zoom_sea`(z14, seeds로 바다 칠) 추가 — `ef`처럼 래스터보다 넓은 뷰에 `demSea`를 켜면 사각 경계가 비침. 고지·토치카·7번 국도 좌표는 개략. 사진 13장 스카우트 핀, 새 그림 50장(장교·교관 9장은 "no collar tabs, no shoulder boards, no red" 프롬프트로 재생성 — 없으면 북한군 복장). 썸네일 **v5 첫 적용** `PAROHO_STD["ep23-jangsari"]`(지시서 말풍선 문구는 `quote`로), v4 시안 `thumbnails/ep23-jangsari_ko_V4.png`, 인물 AI 상징 학도병. 지시서의 '구축함 헬레나함'은 중순양함으로 수정(상륙 지원 구축함은 엔디코트) |

| 24 현리 전투 & 오마치고개 (1951) — 제3군단 해체 · 제1~7막 · **한국어 단일 · Minho · 쇼츠 없음** · 목표 21:30 | `ep24-hyeonri` | 대본 약 9,450자 · 170장면 · target_sec 1290 (첫 미리보기 약 9,170자 = 20:58 → `s70b`·`s129b`·`s140b`·`s149b` 추가, 사용자 지시 6,000~6,500자는 약 15분이라 러닝타임 우선) | 21:30.1 · -15.1 LUFS · 1.33GB · 자막 287/287 · 싱크 ±1.0초 통과 · MP4 렌더 4시간 12분(EP23의 약 2.5배, 장면 수·기울임 지도 z14 영향 추정) | 없음 — 미드롤 `s47`·`s94`·`s142`, CTA1 3막 `cta`, HUD 오버레이 4막 지도, EP25 수도고지·지형능선 예고. 지형 `hyeonri`(z12)·`hyeonri_zoom`(z14) 추가, 오마치·침교·침투로·군단 경계 좌표 개략. 사진 13장 기존 핀 재사용, 새 그림 41장(국군은 "absolutely NO collar tabs, NO patches, NO red" 없으면 붉은 칼라 — 재생성해도 작은 표시 일부 남음). 썸네일 v5 `PAROHO_STD["ep24-hyeonri"]`, 인물 AI(프롬프트에 "clearly East Asian Korean face" 없으면 서양인). 지시서 '해발 800m 협곡'은 출처 없어 제외, '같은 시기'는 이듬해로, 해체 원인은 하진부리 재붕괴로, 전작권 통설 교정 |

| 25 수도고지·지형능선 전투 (1952) — 금성천의 방패 · 제1~7막 · **한국어 단일 · Minho · 쇼츠 없음** · 목표 20:30 | `ep25-capitalhill` | 대본 8,761자(공백 제외 6,757자 — 사용자 지시 6,000~6,500자는 러닝타임 미달이라 보강) · 151장면 · target_sec 1230 (첫 미리보기 19:57 → `s29b`·`s86b`·`s114b`·`s144b` 추가) | 20:30.1 · -15.2 LUFS · 1.26GB · 자막 274/274 · 싱크 ±1.0초 통과 · 렌더 약 2시간 54분 | 없음 — 미드롤 `s44`·`s91`·`s129`, CTA1 3막 `cta`, HUD 오버레이 4막 지도, EP26 승호리 철교 예고. **지도 새 기능 (사용자 지시서 'Awesome Opus 영상 기법')**: 화면 `flight`(뷰 키 목록 → THREE.CatmullRomCurve3와 같은 균일 Catmull-Rom으로 중심·log 폭을 이어 카메라 저공 비행, `flightDur` 초, 프레임 기반), 화면 `hud: true`(전술 HUD — 조준 레티클·회전 나침반 눈금·실시간 위경도/고도 카운터, 틸트 레이어 밖), 아이템 `swarm`(공세 축선 path를 따라 붉은 발광 파티클 `n`개(기본 200)가 진격, hash 결정론 배치 · `speed`·`width`·`size`). 지형 `capital_zoom`(z14) 추가 — 수도고지 CT 905493·지형능선 CT 878498(미군 그리드), 663고지·좌수동·주저항선·접근 축선은 개략. 그림 12장 ep17·19·22 재사용(파일·서명 복사) + 새 그림 24장 + thumb_subject, 썸네일 v5 `PAROHO_STD["ep25-capitalhill"]`(지시서 카피 그대로, 인물 AI thumb_subject → 세션 rembg isnet `thumb_cut.png` — mode=thumb 없이 미리보기에서 생성된 그림 사용), 사진 16장 핀(수도고지 실사 `SC 407542`, 기갑연대 `SC 383811`, 한국 공군 F-51 `NASM 4A 31753` 새로 핀). 제목·썸네일 '7번'은 사료 미확인이나 사용자 지시로 유지(대본은 '기록마다 다름'으로 서술). 진내사격은 수도고지 실시 기록 미확인 → 개념 + 같은 달 미 해병대 사례로 서술 |

| 26 승호리 철교 폭파작전 (1952) — 미군 500번 실패한 다리 · 제1~6막 · **한국어 단일 · Minho · 연출 스타일 v2 + 화면 업그레이드 2단계 첫 적용** · 목표 20:00 | `ep26-seungho` | 대본 약 8,750자 · 248장면(대부분 1문장 1장면) · target_sec 1200 | 20:00.1 · -15.1 LUFS · 1.23GB · 자막 노출·싱크 검사 통과 · 렌더 약 1시간 45분 · 최종본 릴리스 `ep26-seungho-20261112-1729` (첫 렌더 `-1418`은 효과음 과다 버전) | 없음 — 미드롤 `s054`·`s124`·`s164`, CTA1 3막 끝 `cta`. **2026-11-13 롱폼 표준 소급 적용**: `"sfx_policy": "doc"`(꽝·UI pop 금지, 막 전환 스윕·먼 포성·바람·레이더 핑 28개, 15초 쿨다운) + `"bgm_rel_db": -24`, TTS 재호출 없이 재렌더. 캐릭터 42장 첫 생성(`make-chars.yml`, 이후 재생성 금지), 지도 아이템 `plane`. 지형 `seungho`(z12)·`seungho_zoom`(z14) — 남강 하천 데이터는 Overpass 504로 실패(대동강 등 기존 하천만 표시), **철교 좌표 125.955E 39.008N은 개략**. 사진 17장 스카우트 핀(승호리 철교 폭격 전후 항공사진 `File:승호리 철교폭파작전 전후.jpg` 포함), 새 그림 35장 — ⚠️ 무스탕 날개 마크가 태극 대신 영국식 원형으로 나온 그림 있음(프롬프트에 "NOT RAF roundel" 필요). 썸네일 v5 `PAROHO_STD["ep26-seungho"]`(지시서 카피 그대로, 인물 AI → 세션 rembg `thumb_cut.png`). 지시서 교정: '제10전투비행전단'→제1전투비행단 제10전투비행전대, 1,500피트는 강하 아닌 투하 고도(강하 4,000), 1월 15일 편대장 윤응렬·옥만호(유치곤은 2편대 2번기) |

| EN-08 장진호 전투 (1950) — 《Map of War》 영문 단독판 | `ep08-chosin` | → **2026-11-12 `korea1278/map-of-war`로 이전** (대본·스토리보드·재료·미리보기 전부). 이 저장소에 남은 관련 엔진 개선: `tts.py` 막 단위 모드(`tts_mode: "act"`), 지도 HUD `temp`, HUD 구독 오버레이 영문화, 지형 `yudam_zoom`·`funchilin_zoom` | | |

→ **분량 환산 (EP14·15 실측)**: 콜드 오프닝 6막 구조에서 190자 늘리면 약 25초 늘어남(약 7.6자/초) → **7,980자 = 19:20, 8,170자 = 19:45**. 19:30~20:00을 맞추려면 8,100~8,300자

→ **20분 장편 기준 (EP11 실측)**: 한국어 약 8,900자 = 21분. 렌더 한 편 약 2시간(한+영 약 4시간). 렌더 단계는 `TMPDIR`를 작업 디스크로 돌려야 함(러너 /tmp 용량 한도로 20분 오디오 믹싱 실패 — 수정됨), 실패 시 `logs/render_fail_<ep>.txt`에 로그가 남음. 미드롤·목차 시각은 `logs/midroll_<ep>.txt`

→ 영문판은 한국어판보다 0~8초 길어진다. 영문 번역은 7,100자 안팎이면 +6초 수준 (7,200자는 +13초로 경고). 영문판까지 8:30 안에 넣으려면 한국어 3,300자 안팎으로 맞출 것.

---

## ★ 기획 원칙 — 앵글 전환 & 도입부 1분 (2026-11-12 사용자 지시 · 유튜브 피드백 반영 · 다음 편부터 war-docu·map-of-war 공통 영구 적용)
1. **소재를 풀어내는 앵글 전환** — 전투명에 기대지 말고 **인간적 갈등 · 극적인 숫자 · 미스터리 질문**으로 포장한다
   - 제목·썸네일 카피·첫 문장은 '구체적 상황 묘사'로: "235고지 전투"(X) → "물도 탄약도 끊긴 영국군 700명이 버틴 사흘"(O)
   - 전투명은 검색용으로 제목 뒤쪽(콜론·괄호)이나 설명글·태그로 보낸다
   - 대본을 쓰기 전에 앵글 후보 3개(갈등형·숫자형·질문형)를 먼저 뽑고, 가장 강한 것을 제목·썸네일·훅에 일관되게 쓴다. 숫자는 사료로 확인된 것만
2. **도입부 1분 몰입감** — 영상 시작 직후 60초 안에 **결말의 긴박한 복선이나 질문**을 먼저 던진다 (긴 시청 시간이 조회수의 핵심)
   - 0~10초: 가장 극적인 순간(절정·결말 직전)으로 바로 시작 — 배경 설명·연도 나열로 시작 금지
   - 10~45초: "어떻게 / 왜 ~했을까?" 핵심 질문 + 끝까지 보면 답이 나온다는 약속, 결말을 암시하되 다 밝히지 않음
   - 45~60초: 타이틀 카드 → 그다음부터 시간 순 배경 설명
   - 도입부에서 던진 질문은 본편 후반에 반드시 명시적으로 회수한다 (회수 장면을 대본에 표시)
   - 미리보기 확인 때 첫 1분(장면 시트 앞부분)이 위 구조인지 따로 점검한다

## ★ 연출 스타일 v2 — 레퍼런스 '강뉴부대' 영상 방식 (2026-11-12 사용자 지시 · 다음 편부터 war-docu·map-of-war 공통 · EP08 영문 장진호는 제외)
- 스토리보드 최상단에 **`"style": 2`** 를 꼭 켠다 (켜지 않은 기존 편은 예전 방식 그대로 렌더됨)
- **뜻 단위 자막 (엔진 `timeline.py` `split_phrase`)**: 글자 수 균등 분할 대신 쉼표·문장 끝·이음말(~고/~는데/~지만, and/but/which)에서 우선 끊고, 사람·부대·지명 이름 안, 숫자+단위, '~의' 뒤, 보조 용언(~고 있다, ~지 않다)은 끊지 않는다. 한 줄 최대 한국어 21자·영어 44자(+3자 여유). 숫자로 바꿔 쓴 자막(t≠say)도 단어 대응(`disp2say`)으로 실제 발음 시각에 맞춘다
- **단어 동기 표시 (`"on": "단어"`)**: 콜아웃·말풍선(bubbles)·지도 아이템(items)·효과음(sfx)·`visuals`·`hudCta` 어디에나 `"at"` 대신 `"on": "포로 0명"`처럼 대사 속 단어를 적으면 그 단어를 **말하는 순간** 나타난다 (`untilOn`·`takenOn`도 가능). 대사(say 또는 자막 t)에 없는 단어면 `logs/errors.txt`에 경고
  - 쓰는 곳: 핵심 숫자("9,500km", "포로 0명", "단 1개국"), 연도·날짜("1935년"), 사건명("이탈리아의 침공"), 이름을 부르는 순서대로 국기·부대·지명 하나씩 강조, 효과음
- **대본 쓰는 법 (레퍼런스 분석)**
  1. **한 문장 = 자막 한 줄 = 화면 변화 하나**. 문장은 자막 한 줄(한국어 21자·영어 44자) 안팎으로 짧게, 긴 문장은 쉼표로 뜻 단위를 나눠 쓴다
  2. **3~5초마다 화면에 뭔가 바뀐다** — 장면 전환, 또는 같은 장면 안에서 `on`으로 숫자·라벨·하이라이트·말풍선이 뜬다 (레퍼런스: 첫 5분 컷 57번 ≈ 5초당 1번). 20분 편은 장면 약 180~220개
  3. **질문 → 짧은 답 → 반응**: "그런데 이 목록에 좀 뜻밖의 나라가 하나 끼어 있습니다" → "바로 아프리카의 에티오피아" → 캐릭터 반응 말풍선("어? 여긴..?", "도와주세요!!"). 어려운 개념은 생활 비유로("보험 증서", "보험료 납부")
  4. 문서·조약·신문은 `document` 카드로 요점 2~4줄 + 도장/붉은 X, 목록·이유는 체크리스트·번호 카드로 하나씩 `on`에 맞춰 띄우고 지워 나간다
  5. 사료 사진은 좌상단 작은 출처 라벨 + 말하는 순간 뜨는 노란/빨간 강조 라벨

## ☑ 화면 업그레이드 2단계 — 레퍼런스 수준 디자인 통일 (2026-11-12 사용자 확정 · **EP26 승호리에서 구현 완료** · war-docu·map-of-war 공통)
> 구현: `remotion/Stage.tsx` (stage · flatmap · flaggrid · checklist · reasons · PhotoTag/PhotoMarks · 국기 SVG `Flag` kr/us/cn/nk/uk/su/un/et/jp/?), 종이 질감 `public/ui/paper.jpg`, 캐릭터 생성 `pipeline/chars.py` + Actions "캐릭터 라이브러리 만들기"(`make-chars.yml`, 입력 only=다시 만들 이름). 사용 예시는 `episodes/ep26-seungho/make_board.py` 헬퍼(C·pop·stage·flat·fpin·route·reasons·checklist)
> - 캐릭터 42장 `public/chars/<kr|us|cn|nk|uk|su|un>_<idle|plead|shrug|salute|point|shock>.png` — 그림이 없는 이름은 SVG 볼로 자동 대체. **누끼는 rembg 금지**(흰 국기·흰 눈까지 지움) → 테두리에서 이어진 흰 배경만 flood fill로 지움
> - stage: `chars[{c, x, y(발 위치 0~1), h, at|on, flip, until}]`, `pops[{kind: bubble|q|ex|label|flag|text, x, y, text, at|on, color}]`, `title`
> - flatmap: `center`, `span`(경도 폭), `fill`(나라 id→색), `pins[{ll, text, flag, side, at|on}]`, `routes[{from, to, label, bend, at|on, dash}]`, `labels[{ll, text, style:"sea"}]` — ⚠️ 좌표는 `ll`(at은 시간으로 바뀜)
> - checklist `items[{text, at|on, checkOn, bad}]` · reasons `items[{text, sub, at|on, xOn, later}]`(later=번호만) · flaggrid `items[{flag, name, at|on}]` · photo `tag`(좌상단 출처·연도), `marks[{text, x, y, at|on, color, ring}]`
> - 지도 아이템 `plane`(EP26): `path`, `n`(편대 대수), `dur`, `size`, `color`, `hit`(끝점 폭발), `trail`
> - timeline.py: `on` 외에 `checkOn`→checkAt, `xOn`→xAt 변환, 타임라인에 `chars` 목록
1. **캐릭터 라이브러리 = 이미 만든 42장을 계속 재사용 (2026-11-12 사용자 지시: 수익 창출 전이라 추가 그림 비용 금지)** — `public/chars/` 7개국 × 6포즈는 EP26 때 한 번 생성 완료(일회성 비용, 다시 만들지 말 것 — `make-chars.yml` 재실행 금지). 새 나라가 필요하면 Gemini로 그리지 말고 `Stage.tsx`의 **SVG 볼 자동 대체**(국기 SVG `Flag`에 나라 추가)로 0원 처리. 아이콘이 필요하면 무료 오픈소스 `lucide`(ISC)
2. **새 화면 `stage` (종이 무대)** — 구겨진 흰 종이 배경(SVG 노이즈 필터로 생성, 이미지 파일 불필요) 위 캐릭터 1~3명 배치, 말풍선·아이콘·물음표·느낌표가 `on` 단어 타이밍에 팝업, 살짝 흔들리는 등장 애니메이션
3. **새 화면 `flatmap` (플랫 지도)** — 바다 청록·땅 베이지·국가 단색 칠하기, 거리 곡선 + 라벨("직선 약 9,500km"), 국기 핀. 세계·지역 개요 설명용 (전투 장면은 기존 3D 전술 지도 유지 — 채널 강점)
4. **설명 카드 3종** — `flaggrid`(국기 줄 세우기 + 이름 부를 때 하나씩 강조·"?" 칸), `checklist`(노란 체크가 하나씩), `reasons`(이유 1·2·3 번호 카드 + 붉은 X로 지우기). 배경은 어두운 석판 질감 (`document` 카드도 같은 톤으로)
5. 사료 사진: 좌상단 작은 출처·연도 라벨 + `on`에 맞춰 뜨는 노랑/빨강 강조 라벨

## ★ 캐릭터 반복 방지 규칙 (2026-11-12 사용자 지시 · EP26 다음 편부터 · war-docu·map-of-war 공통 · 추가 비용 0원)
> 캐릭터 42장(`public/chars/`)은 계속 재사용하되, 매 편 같은 장면처럼 보이지 않게 아래를 지킨다. 전부 코드로 처리 — 그림을 새로 생성하지 말 것
1. **표정 덧그리기** — 같은 캐릭터 그림 위에 SVG로 표정을 얹는다: 화난 눈썹·땀방울·눈물·놀란 입·반짝 눈·식은땀 줄 (stage `chars[].face`: angry·sweat·tears·shock·smug·worried 등). 아직 없으면 다음 편 작업 때 `Stage.tsx`에 먼저 구현
2. **소품 씌우기** — 시대·인물에 맞는 소품을 SVG로 얹는다: 군모·철모·장교모·왕관·안경·훈장·담배 파이프·서류 가방 (`chars[].prop`)
3. **움직임** — 말하는 캐릭터는 통통 튀기, 고개 갸웃, 부들부들 떨기, 화면 밖에서 걸어 들어오기·나가기, 눈 깜빡임 (`chars[].anim`: bounce·tilt·shake·enter·exit)
4. **사용 규칙**
   - 캐릭터 무대(`stage`)는 전체 장면의 **25% 이하**
   - 같은 나라·같은 포즈 조합을 **연달아 두 장면** 쓰지 않는다. 한 편 안에서 같은 조합이 3번 넘게 나오지 않게 (좌우 뒤집기·위치·크기·표정·소품으로 반드시 변화)
   - 스토리보드 생성기에서 위 두 조건을 자동 검사해 어기면 경고(가능하면 assert)
   - 말풍선 문구는 매번 그 장면 대사에 맞춰 새로 쓴다 (편마다 같은 문구 재사용 금지)

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
   - ★ **렌더 완료 후 자동 정리 (2026-11-06 사용자 지시 — "무조건 기억")**: 본 렌더 dispatch 직후 `send_later`(예상 소요 + 여유, 보통 2시간 10분)로 이 세션에 확인 메시지를 예약해 둔다. "끝나면 말씀해 주세요"로 미루지 말 것. 렌더가 끝나면 사용자가 다시 묻지 않아도 8번 검증(길이·LUFS·싱크·지도 프레임)과 10번 전달 패키지(Releases 링크·SRT·썸네일·제목 3개·목차 넣은 설명글·태그·확인 덜 된 항목)를 한 번에 보낸다
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
9. **썸네일** — ★★★★★ **썸네일 표준 v5 = '파로호 공식' (2026-11-08 사용자 지시서 · 채널 최고 성과 EP13 분석 · 앞으로 만드는 모든 롱폼 한국어 A안 기본 — 아래 v4 이하는 기존 에피소드 기록용)**
   - 구현: `remotion/Thumbnail.tsx`의 `PAROHO_STD` 표에 에피소드 한 줄(`ThumbnailProps`) → `ParohoThumb`가 렌더 (COLLAGE·FRONT·MAPT보다 우선). 기존 에피소드는 표에 없으므로 그대로. `paroho:sample`은 지시서 예시 검수용
   - 필수: `quote`(따옴표 자동) · `titleLine1` · `titleLine2` · `mapImage` · `characterCutout` (public 기준 경로), 선택: `stampText` · `targets`(타깃 링 `{x,y,r,label}`) · `arrows`(`{pts,color}`, 마지막 점이 화살촉 · color는 `red`=적 / `ally`=아군 노랑 `#FFD400` — **강·호수와 같은 파랑 금지**, 2026-11-08 사용자 수정) · `mapCrop`(`{cx,cy,zoom}`) · `characterPos` · `stampPos` — 좌표는 캔버스 픽셀(1920×1080), 전황은 x 1056 안쪽에
   - 규격: 좌 55% 흑백 고대비 지도 + 붉은 타깃 링·진격 화살표 / 우 45% 인물 흑백 누끼 + 흰 림 외곽선 / 좌상단 따옴표 56~64px `#FF2222` / 하단 2줄 좌측 정렬 left 60 — Line 1 흰색, Line 2 `#FF2222`, Pretendard Black. **글자 크기 (2026-11-08 사용자 수정, 지시서의 고정 104/116px 대체)**: 더 중요한 줄(`emphasis`, 기본 2)이 안전 폭을 꽉 채우고(상한 190px), 다른 줄도 강조 줄의 86% 안에서 최대한 폭을 채워 빈 공간을 없앰. 글자 묶음 높이 400px 상한으로 얼굴 보호 / 그라데이션은 텍스트 높이만큼만
   - ★ **지형지물은 한눈에 (2026-11-08 사용자 수정)**: 지도 필터 `grayscale(1) brightness(0.58) contrast(1.7)`로 산세를 또렷하게. `mapImage` 파일명이 `rasters.json`에 있으면 호수·강을 `water.json`에서 선명한 파랑 `#1E8FFF` + 짙은 테두리로 자동 칠함. 호수·강·산 이름표는 `places`(`{x,y,label}`, 46px)로 표기 — 핵심 지형지물 1~3개는 꼭 넣을 것
   - ★ **재생시간 배지 안전 여백**: 오른쪽 200px 비움(글자 x 1720 이내). 모든 크기는 실측 폭으로 계산, Line 2가 한 줄로 84px 밑으로 내려가야 하면 가운데 띄어쓰기에서 두 줄로 나눔
   - 렌더 후 확인: 글자가 x 1720을 넘지 않음, 얼굴을 글자·도장이 가리지 않음, 타깃 링·화살표가 인물과 안 겹침
   - (v4) ★★★★ **썸네일 표준 v4 = '스토리텔링 꼴라주 + 3D 몬스터 타이포' (2026-11-02 사용자 지시서 · 레퍼런스 별별역사 · EP15 낙동강(`naktong`)·EP16 도솔산(`ep16-dosolsan`)부터 한국어 A안 기본 — 아래 v3/v3.1 '선 넘는 지도' 방식은 폐기, 기록용)**
   - 구현: `remotion/Thumbnail.tsx`의 `COLLAGE` 표에 에피소드 한 줄 → `CollageThumb`가 한국어 A안을 렌더 (1920×1080 픽셀 단위 그대로, FRONT·MAPT보다 우선). 기준 결과물 `thumbnails/naktong_ko_A.png`, `thumbnails/ep16-dosolsan_ko_A.png`
   - [최상단] 인용구 배너: top 25 · 가운데 · 네온 레드 `#FF2222` · “ ” 큰따옴표 · 40px Pretendard Black · `-webkit-text-stroke: 4px #000` + 그림자 (`quote`)
   - [중단 좌] 핵심 인물 고대비 흑백 누끼 left 30 · bottom 350 (`person`: src·h·w·pos — 하단·오른쪽 가장자리는 마스크로 녹임) + 입가 말풍선(흰 라운드 박스 · 6px 검정 보더 · 꼬리 `tail`은 입 좌표) + 15도 기울어진 붉은 사각 직인(`stamp`, 붉은 바탕 흰 글자 · 흰 이중 테두리)
     - 인물 누끼가 배경째 남아 있으면 세션에서 `rembg`(isnet-general-use)로 다시 따서 `public/ep/<ep>/ai/thumb_cut.png`로 저장 (EP16에서 thumb_subject.png가 배경 불투명이라 재처리함)
   - [중단 우] 흑백 전장 지도(`public/geo/thumbc/<래스터>` grayscale) + 타깃 영역 붉은 반투명 하이라이트(`red` 폴리곤 — 지형 위 #FF1A1A multiply라 산 질감이 살아 있음, 육지 안 경계면 `outline: true`) + 아군 방어선 푸른 라인(`blue`) + 대형 군기(`flags`: `kr` 태극기 / `nk` 인공기 / `marine` 해병대기, 깃대 밑동 좌표 `at`, `h`=깃발 높이) + **3D 골드 돌격 화살표 3개**(`arrows`, 옐로-골드 `#FFE600→#FFAA00` · 8px 블랙 보더 · 16px 돌출 측면 + 깊은 드롭섀도우, `arrowW` 굵기)
     - 지도는 화면 전체에 깔되 전황이 오른쪽 위(x 1000~1900, y 60~650)에 오도록 `view`(center·span)를 맞춘다. 깃발·화살표가 상단 인용구(가운데 x 560~1360, y 25~75)와 겹치지 않게
   - [하단 45%] 칠흑 블랙 딤: `linear-gradient(to top, #000 0%, #000 65%, rgba(0,0,0,.9) 85%, transparent 100%)`
   - [최하단] 2줄 3D 몬스터 텍스트 bottom 25 · 가운데: Black Han Sans(400) · Line 1 흰색 96px / Line 2 레드 `#FF2222` 114px(핵심 키워드는 ‘ ’) · line-height 1.02 · 자간 -4px · `-webkit-text-stroke: 8px #000; paint-order: stroke fill; text-shadow: 0 3px 0 #000, 0 6px 0 #000, 0 9px 0 #000, 0 12px 0 #000, 0 16px 20px #000`. **96:114 비율 그대로 공통 배율** — 가장 긴 줄이 화면 폭 95%를 채우게 자동 확대·축소(실측 글꼴 폭)
   - 렌더 후 확인: 인물 얼굴을 말풍선·직인이 가리지 않음, 말풍선 꼬리가 입을 가리킴, 깃발·화살표가 인용구·하단 텍스트와 안 겹침, Line 2가 화면 폭을 거의 꽉 채움. PNG 1.9MB 넘으면 JPG로 전달 (`_ko_A.jpg`도 함께 갱신)
   - 이 아래 v3/v3.1은 **기록용** (`COLLAGE`에 없는 에피소드만 FRONT로 렌더됨)
   - (v3 · 기록용) ★★★ **썸네일 표준 v3 = '선 넘는 지도' 스타일 (2026-11-02 사용자 지정 · EP15 낙동강(`naktong`)·EP16 도솔산부터 한국어 A안 기본 — 아래 v2(EP09 피의 능선 기준)보다 우선)**
   - 구현: `remotion/FrontThumb.tsx`의 `FRONT` 표에 에피소드 한 줄 → `remotion/Thumbnail.tsx`가 한국어 A안을 이 디자인(1920×1080)으로 렌더. 기준 결과물 `thumbnails/naktong_ko_A.png`, `thumbnails/ep16-dosolsan_ko_A.png`
   - ★ **v3.1 (2026-11-02 사용자 지시서 '실전 전황 디테일 & 3D 입체 텍스트' — 아래 v3 원안보다 우선)**. 규격은 레퍼런스(1280×720) 단위로 적고 1.5배로 출력
     1. **우측 상단 연월 뱃지 완전 삭제** (카피 느낌 — 다시 넣지 말 것)
     2. 적 공세 구역: 붉게 달군 지형 + 불타는 전선 화염 + 폭격 연기 기둥(`smoke`), 방어선에 꽂히는 **굵은 레드 네온 화살표 3~4개**(`arrows`, w 20~22), 화살표 사이로 진격하는 **전차·돌격 보병 실루엣**(`units`: `tank`/`inf`, 검은 몸체 + 붉은 림), **함락 도시 핀**(`fallen`: `x` = 붉은 X / `hit` = 붉은 타격 원 + 검정 칩 지명)
     3. 아군 방어선: 형광 시안 `#00E5FF` 네온 6px + 다층 발광, **핵심 거점 도트 핀 + 미니 칩**(`pins`), 방어선 중심 **네온 강조 뱃지**(`badges`, 예: `낙동강`·`도솔산`). 칩 위치는 `side`(below/right/left/above)로 겹침 회피. 화면 밖·하단 타이틀 영역(하단 45%)에 들어가는 핀은 지도 영역 가장자리로 끌어와 ▲▼◀▶ 방향 표시
     4. 하단 45% 칠흑 그라데이션: `linear-gradient(to top, #000 0%, rgba(0,0,0,.98) 35%, rgba(0,0,0,.85) 65%, transparent 100%)`
     5. 타이틀: Black Han Sans, 화면 폭 90% 점유, Line 1 흰색 90~94px / Line 2 `#FFD000` 110~116px (길면 90% 안으로 자동 축소, Line 2는 Line 1의 1.18배 이상), line-height 1.05, 자간 -3px, bottom 35, `-webkit-text-stroke: 6px #000; paint-order: stroke fill; text-shadow: 0 4px 0 #000, 0 8px 0 #000, 0 12px 2px #000, 0 16px 25px rgba(0,0,0,.95)`. (v3의 우측 120px 재생시간 여백은 폐지)
     6. 겹쳐 까는 고해상도 지형(두 번째 래스터부터)은 가장자리를 마스크로 녹여 타일 경계가 안 보이게 자동 처리. 적 영역(`enemyClose`)은 바다 위로 넘어가지 않게 해안선 안쪽으로 닫을 것 (바다가 검게 칠해짐)
   - (v3 원안 · 기록용) 우측 상단 시대 뱃지(X 1040·Y 40) / 지명·좌표 라벨 전부 숨김 / 하단 40% 블랙 그라데이션 / Line 1 68~72px·Line 2 78~84px, line-height 1.15, 오른쪽 120px 비움. 인물 누끼·스탬프 없음
   - 지도: 컬러 지형(`public/geo/thumbc/<래스터>.webp` — 새 래스터는 `python3 pipeline/thumb_color.py <이름…>`로 만들어 커밋). `front`(아군 방어선 = 형광 블루 `#00E5FF` 네온, 적 영역 경계) + `enemyClose`(화면 밖으로 돌아 닫는 점) = 붉게 달군 적 공세 영역, `fires`(불길·불씨·포연 중심), `arrows`(red = 적 돌격 / cyan = 아군 돌격), `points`(라벨 없는 빛나는 점), `river`(선택)
   - 썸네일 PNG가 2MB를 넘으면 업로드용 `_ko_A.jpg`도 만들어 JPG로 전달
   - (이전) v2 표준은 아래 그대로 기록용 — `FRONT`에 없는 에피소드의 A안·영문 A안은 여전히 `MAPT`(v2)로 렌더됨
   - (v2) **썸네일** — ★ **공통 썸네일 표준 (2026-10-25 사용자 확정 · EP09부터 모든 새 에피소드 A안 기본, 새 세션에서도 그대로 적용)**
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
| 해상도 / 인코딩 | 1920×1080, 30fps, H.264 `--video-bitrate=8M --x264-preset=veryfast --concurrency=4`, AAC 192k (2026-11-01 변경: crf 20은 23분 영상이 2GB를 넘어 Releases 업로드 실패(HTTP 422) → 8Mbps 고정, 23분 약 1.4GB. 렌더 후 1.9GB 초과 시 1.5GB 목표로 자동 재인코딩. Releases 스텝 `continue-on-error`, Artifacts 백업은 `if: always()`) |
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
- (2026-11-01 보강) 공용 `CalloutBox`(텍스트 카드·암전 강조·요인 카드·타임라인·대결 라벨)도 `fitFont`로 한 줄 폭(기본 1760px, 타임라인은 칸 폭)에 맞춰 자동 축소 + `keep-all`. 막대그래프 라벨도 한 줄 고정
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
