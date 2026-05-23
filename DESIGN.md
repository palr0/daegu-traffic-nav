# 대구대학교 교통·주차 내비게이션 — 설계문서

**버전:** v1.0  
**저장소:** https://github.com/palr0/daegu-traffic-nav  
**작성일:** 2026-05-23

---

## 1. 프로젝트 개요

### 목적

대구대학교 경산캠퍼스의 차량 혼잡, 주차 포화, 보행자-차량 충돌 위험 지점을 실시간으로 시각화하는 웹 기반 교통·주차 내비게이션 서비스.

### 핵심 목표

| 목표 | 설명 |
|------|------|
| 교통 흐름 시각화 | 정문·동문·서문별 진입/출구 방향, 일방통행 구간, 위험 지수 표시 |
| 주차 포화도 안내 | 5개 주차장의 현재 사용률·혼잡도를 색상 코드로 즉시 인식 |
| 전문가 인사이트 | 교통공학 관점의 위험지점 진단과 개선 권고를 지도에 직접 표시 |
| 혼잡시간 경로 안내 | 피크타임 자동 감지 후 권장 대체 경로 배너 노출 |

### 범위

- **포함:** 경산캠퍼스 내부 도로망, 3개 게이트, 5개 주차장, 9개 교통 세그먼트, 5개 위험지점
- **제외:** 실시간 차량 카운트 API 연동, 모바일 앱, 사용자 인증

---

## 2. 아키텍처

### 구조 원칙

**단일 파일(Single-File) 정적 앱.** 빌드 툴, 백엔드 서버, 데이터베이스 없음.  
모든 데이터는 JavaScript 인라인 GeoJSON 상수로 번들됨.

```
index.html (1,080 lines)
├── <style>        CSS 변수 시스템 + 전체 컴포넌트 스타일
├── <body>         Alpine.js 바인딩 HTML 마크업
└── <script>
    ├── PARKING_GEOJSON    주차장 폴리곤 데이터
    ├── TRAFFIC_GEOJSON    도로 세그먼트 라인 데이터
    ├── INSIGHT_GEOJSON    위험지점 포인트 데이터
    └── Alpine.data('app') 앱 상태·이벤트 처리
```

### 런타임 의존성 (CDN)

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Leaflet.js | 1.9.4 | 지도 렌더링, GeoJSON 레이어, 팝업 |
| Alpine.js | 3.14.1 | 리액티브 상태 관리, 조건부 렌더링 |
| CartoCDN dark_all | — | 다크 베이스맵 타일 |
| Google Fonts | — | Inter, JetBrains Mono |

### 데이터 흐름

```
브라우저 로드
    │
    ├─ CDN 타일 요청 (CartoCDN)
    ├─ 폰트 로드 (Google Fonts)
    │
    └─ alpine:init 이벤트
           │
           └─ app.init()
                  ├─ tick()         → 시계 + 혼잡시간 판정 (30초 주기)
                  └─ buildMap()
                         ├─ L.map() 초기화 (center: 35.8897N, 128.7584E, zoom: 16)
                         ├─ addParkingLayer()   PARKING_GEOJSON → L.geoJSON 폴리곤
                         ├─ addTrafficLayer()   TRAFFIC_GEOJSON → L.geoJSON 라인 + 화살표 마커
                         ├─ addInsightLayer()   INSIGHT_GEOJSON → L.divIcon 원형 마커
                         └─ addGateMarkers()    하드코딩 3개 게이트 라벨 마커
```

---

## 3. 디자인 시스템

### 디자인 철학

독립 오픈소스 개발자 감성: **날카로운 타이포그래피 + 고대비 유틸리티 + 모노크롬 톤**.  
과포화 네온 그래디언트, 과도한 글래스모피즘, 스테릴한 대시보드 템플릿을 명시적으로 배격.

### CSS 변수 팔레트

```css
/* 배경 계층 */
--bg-base:      #0d1117   /* 최하위 배경 (GitHub dark 기반) */
--bg-panel:     #161b22   /* 패널, 사이드바 */
--bg-panel-alt: #1c2128   /* 호버 상태, 입력 배경 */

/* 테두리 */
--border:       #30363d   /* 주요 테두리 */
--border-sub:   #21262d   /* 섹션 구분선 */

/* 텍스트 계층 */
--text-pri:     #e6edf3   /* 주요 텍스트 */
--text-sec:     #8b949e   /* 보조 텍스트, 레이블 */
--text-dim:     #484f58   /* 비활성, 메타데이터 */

/* 시맨틱 색상 */
--amber:        #d97706   /* 경고 (어두운) */
--amber-lt:     #f59e0b   /* 경고 (밝은), 혼잡시간 강조 */
--emerald:      #059669   /* 안전 (어두운) */
--emerald-lt:   #10b981   /* 안전 (밝은), 여유 주차 */
--red:          #dc2626   /* 위험 (어두운) */
--red-lt:       #ef4444   /* 위험 (밝은), 혼잡 주차 */
--blue:         #1f6feb   /* 강조 (어두운), 토글 on 상태 */
--blue-lt:      #60a5fa   /* 강조 (밝은), 일반 도로 */
```

### 타이포그래피

| 용도 | 폰트 | 사이즈 |
|------|------|--------|
| UI 본문, 레이블 | Inter | 9–14px |
| 수치, 좌표, 시계 | JetBrains Mono | 10–22px |
| 섹션 헤더 | Inter 700 + uppercase + letter-spacing | 9px |

### 지도 필터

```css
.leaflet-tile-pane { filter: saturate(0.6) brightness(0.68); }
```
CartoCDN 다크 타일을 추가로 탈채도·어둡게 처리해 오버레이 레이어와 명확히 분리.

---

## 4. 레이아웃 구조

```
┌──────────────────────────────────────────────────────────────┐
│  #sb-toggle (30×30px, z:1001)                                │
│                                                              │
│  ┌────────────┐  ┌──────────────────────────────────────┐   │
│  │  #sidebar  │  │              #map                    │   │
│  │  (296px)   │  │         (position:fixed, inset:0)    │   │
│  │            │  │                                      │   │
│  │ sb-header  │  │  게이트 마커 (정문/동문/서문)           │   │
│  │  - 제목    │  │  주차장 폴리곤                        │   │
│  │  - 시계    │  │  교통 세그먼트 라인 + 화살표           │   │
│  │  - 혼잡칩  │  │  인사이트 ! 마커                     │   │
│  │            │  │                                      │   │
│  │ sb-body    │  └──────────────────────────────────────┘   │
│  │  - 레이어  │                                             │
│  │  - 주차장  │  ┌───────────────┐  ┌──────────────────┐   │
│  │  - 게이트  │  │ #route-banner │  │  #info-panel     │   │
│  │  - 인사이트│  │ (혼잡시간 only)│  │  (캠퍼스 현황)    │   │
│  │  - 범례    │  └───────────────┘  └──────────────────┘   │
│  └────────────┘                                             │
└──────────────────────────────────────────────────────────────┘
```

### 주요 UI 컴포넌트

| 컴포넌트 | 위치 | 역할 |
|---------|------|------|
| `#sidebar` | 좌측 고정, 296px | 레이어 제어 + 데이터 패널 |
| `#sb-toggle` | 사이드바 우측 상단 | 사이드바 접기/펼치기 |
| `#info-panel` | 우하단 고정, 210px | 캠퍼스 전체 주차 통계 |
| `#route-banner` | 상단 (사이드바 우측) | 혼잡시간 권장 경로 (피크타임 자동 표시) |
| Leaflet 팝업 | 지도 요소 클릭 시 | 상세 데이터 표시 |

---

## 5. 데이터 레이어

### 5.1 주차장 레이어 (`PARKING_GEOJSON`)

**지오메트리 타입:** Polygon  
**렌더링:** `L.geoJSON` — fillColor/stroke는 `current_status` 기준 결정

| ID | 이름 | 총 면수 | 현재 사용 | 상태 |
|----|------|---------|----------|------|
| P1 | 공과대학 주차장 | 180 | 148 | peak (82%) |
| P2 | 사회과학대학 주차장 | 120 | 75 | moderate (63%) |
| P3 | 사범대학 주차장 | 95 | 32 | empty (34%) |
| P4 | 본관·행정동 주차장 | 200 | 170 | peak (85%) |
| P5 | 학생복지관 주차장 | 80 | 48 | moderate (60%) |

**속성 스키마:**
```js
{
  id, name, college_zone,
  total_spaces, current_occupied, current_status,   // "peak" | "moderate" | "empty"
  disabled_spaces, ev_chargers, shuttle_stop,
  saturation_index,                                  // 0.0–1.0
  peak_hours: string[],
  recommended_gates: string[]
}
```

**상태별 색상:**
- `peak` → `rgba(239,68,68,0.30)` / stroke `#ef4444`
- `moderate` → `rgba(245,158,11,0.30)` / stroke `#f59e0b`
- `empty` → `rgba(16,185,129,0.30)` / stroke `#10b981`

---

### 5.2 교통 레이어 (`TRAFFIC_GEOJSON`)

**지오메트리 타입:** LineString  
**렌더링:** `L.geoJSON` + `L.divIcon` 화살표 마커 (세그먼트 중간점 기준)

| ID | 이름 | 방향 | 일방 | risk |
|----|------|------|------|------|
| T1 | 정문 진입로 | inbound | ✓ | 1.8 (주의) |
| T2 | 정문 출구로 | outbound | ✓ | 1.5 (주의) |
| T3 | 정문–본관 내부도로 | both | — | 1.2 |
| T4 | 복지관 앞 일방통행 | eastbound | ✓ | **2.1 (고위험)** |
| T5 | 도서관 진입로 | both | — | 1.6 (주의) |
| T6 | 공과대학 진입로 | inbound | — | 1.3 |
| T7 | 동문 진입로 | inbound | — | 1.1 |
| T8 | 서문 우회 진입로 | inbound | — | 0.8 (안전/우회) |
| T9 | 캠퍼스 외곽 순환로 | 반시계 | ✓ | 0.7 (안전/우회) |

**risk_multiplier 색상 함수:**
```js
r >= 2.0  → #ef4444  (고위험)
r >= 1.5  → #f59e0b  (주의)
r < 0.9   → #10b981  (안전/우회)
else      → #60a5fa  (보통)
```

**일방통행 표시:** `dashArray: '9 5'` 적용, 화살표(▲) `atan2` 각도 계산 후 `transform:rotate()`

**속성 스키마:**
```js
{
  id, name, flow_direction, one_way,
  risk_multiplier, road_type, peak_volume,   // "high" | "medium" | "low"
  desc
}
```

---

### 5.3 인사이트 레이어 (`INSIGHT_GEOJSON`)

**지오메트리 타입:** Point  
**렌더링:** `L.divIcon` — 원형 `!` 배지, 위험 등급별 색상

| ID | 위치 | 위험 등급 | 충돌지수 | 연간사고 |
|----|------|----------|---------|---------|
| I1 | 복지관 앞 횡단보도 | critical | 9.2 | 3건 |
| I2 | 도서관 진입로 병목 | high | 6.8 | 1건 |
| I3 | 정문–공과대학 사거리 | high | 7.1 | 2건 |
| I4 | 서문 경사로 구간 | moderate | 4.2 | 0건 |
| I5 | 동문 전방 접근로 | low | 1.5 | 0건 |

**등급별 색상:**
- `critical` → `#ef4444`
- `high` → `#f97316`
- `moderate` → `#f59e0b`
- `low` → `#10b981`

---

### 5.4 게이트 마커 (하드코딩)

| 이름 | 좌표 | 방면 |
|------|------|------|
| 정문 | [35.8858, 128.7542] | 하양읍 방면 |
| 동문 | [35.8875, 128.7642] | 내리리 방면 |
| 서문 | [35.8893, 128.7505] | 우회 진입 |

---

## 6. 앱 상태 (Alpine.js)

```js
{
  open: true,          // 사이드바 열림 상태
  clock: '--:--',      // HH:MM 문자열 (30초 갱신)
  isPeak: false,       // 혼잡시간 여부
  mapObj: null,        // Leaflet Map 인스턴스
  mapLayers: {},       // { parking, traffic, insights } → L.LayerGroup
  arrowMarkers: [],    // 교통 방향 화살표 L.Marker[]

  layers: { parking: true, traffic: true, insights: true },

  lots: [...],         // 사이드바 주차 목록 (정적 복사본)
  gates: [...],        // 사이드바 게이트 목록
  insights: [...],     // 사이드바 인사이트 요약 목록

  // computed
  totalSpaces,         // lots.total 합산
  totalOcc,            // lots.occ 합산
  satPct               // totalOcc/totalSpaces × 100
}
```

### 혼잡시간 판정 로직

```js
const t = hours * 60 + minutes;
isPeak = (t >= 510 && t <= 570)    // 08:30–09:30
      || (t >= 1050 && t <= 1110); // 17:30–18:30
```

---

## 7. 인터랙션 명세

| 액션 | 동작 |
|------|------|
| 사이드바 토글 버튼 클릭 | `open` 토글 → sidebar `translateX(-296px)` + 토글 버튼 `left` 전환 + `invalidateSize()` 호출 (240ms 딜레이) |
| 레이어 토글 스위치 클릭 | `layers[name]` 토글 → `mapObj.addLayer/removeLayer` 호출. traffic 레이어는 arrowMarkers 동기화 |
| 주차장 폴리곤 클릭 | 팝업: 이름, 단과대학, 전체/사용 면수, 포화율%, 장애인/EV/셔틀, 혼잡시간대, 권장 게이트 |
| 교통 라인 클릭 | 팝업: 이름, 통행방향, 일방통행여부, 위험지수, 혼잡도, 설명 |
| 주차장 폴리곤 호버 | `weight: 3, fillOpacity: 0.6` → mouseout 시 `resetStyle()` |
| 인사이트 마커 클릭 | 팝업: 위치, 이슈유형, 위험등급, 충돌지수, 연간사고, 혼잡시간대, 전문가 권고 |
| 게이트 마커 클릭 | 팝업: 이름, 방면 설명 |
| 혼잡시간 진입 (`isPeak = true`) | `#route-banner` 페이드인: "서문 진입 → 외곽 순환로 경유 → 사범대·공과대 방면" |

---

## 8. 팝업 컴포넌트 설계

모든 팝업은 CSS 클래스 통일:

```
.pu-title    → 제목 (border-bottom 구분)
.pu-row      → key-value 한 줄 (space-between)
  .pu-key    → 10px, --text-sec
  .pu-val    → 11px JetBrains Mono, --text-pri
.pu-note     → border-top 구분 후 보조 설명
  .pu-note-label → 9px uppercase, --text-dim
```

---

## 9. 현재 제약 및 개선 과제

### 정적 데이터

현재 모든 주차 점유율·교통 상태는 **스냅샷 정적 데이터**. 실제 운영을 위해서는:

- 주차 센서 API 연동 (주기적 `fetch` + 상태 갱신)
- 교통 카메라·루프 디텍터 데이터 파이프라인

### 좌표 정밀도

GeoJSON 폴리곤과 라인 좌표는 **개략적 추정값**. 실 운영 시 GNSS 측량 또는 항공 GIS 데이터 기반으로 교정 필요.

### 모바일 대응

`overflow: hidden` + 고정 레이아웃으로 모바일 화면 미최적화.  
반응형 breakpoint 및 터치 인터랙션 개선 필요.

### 향후 기능 후보

| 기능 | 우선순위 |
|------|---------|
| 실시간 API 폴링 (주차 점유율) | 높음 |
| 경로 탐색 (A* 또는 Leaflet Routing Machine) | 중간 |
| VMS 연동 정보 표시 | 중간 |
| 모바일 반응형 레이아웃 | 중간 |
| 다크/라이트 테마 전환 | 낮음 |
| 공사·행사 임시 규제 레이어 | 낮음 |

---

## 10. 파일 구조

```
daegu-traffic-nav/
├── index.html      앱 전체 (HTML + CSS + JS 단일 파일)
├── DESIGN.md       본 설계문서
└── .gitignore
```

---

## 11. 배포

정적 파일 단독 배포 가능. 별도 빌드 불필요.

```bash
# 로컬 확인
python -m http.server 8080
# → http://localhost:8080

# GitHub Pages 배포
# Settings → Pages → Branch: main / root
```

CDN 의존성이 있으므로 오프라인 환경에서는 동작하지 않음.
