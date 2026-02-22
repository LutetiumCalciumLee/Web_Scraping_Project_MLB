<details>
<summary>ENG (English Version)</summary>

# MLB Game Prediction Data Collection

Web application for MLB game prediction through real-time pitcher and batter statistics from Fangraphs.

## Project Overview

Platform that automatically collects statistics from Fangraphs via web scraping, stores data in SQLite, and provides an interactive web interface for comparing game schedules and player statistics.

## Key Features

### Data Collection
- Automatic collection of 15 category statistics from Fangraphs
  - Starting pitcher base stats, High/Medium/Low Leverage situation analysis, batting performance
- Reliable data collection with rate-limited requests and robust retry handling
- Automatic database storage after scraping

### Data Management
- Centralized SQLite database storage
- 3-tier caching system (DB → file → scraping) to minimize unnecessary scraping
- Systematic management with date-based directory structure
- Automatic duplicate prevention

### Game Analysis
- MLB game schedule display by date
- Away/home team starting pitcher selection and statistics lookup
- Pitcher performance analysis by High/Medium/Low Leverage situations
- Team batting statistics and RISP (Runners in Scoring Position) analysis
- Display of pitchers with 2+ games in last 2 days

### Data Visualization
- Interactive comparison charts using Chart.js
- Automatic chart display on table header/cell hover
- Real-time away vs home team statistics comparison with bar graphs

## Technology Stack

| Category | Technology |
|----------|-----------|
| Backend | Python 3.12, Flask, SQLite3 |
| Scraping | Selenium, undetected_chromedriver, BeautifulSoup4 |
| Frontend | HTML/CSS, JavaScript, Chart.js |

## Project Structure

```

Web_Scraping_Project_MLB/
├── back/                          # Backend
│   ├── app.py                     # Flask main server
│   ├── load_json_to_db.py         # DB data import script
│   ├── fangraphs_data.db          # SQLite database
│   └── fangraphs_scraper/         # 15 scrapers
│       ├── fangraphs_scraper1.py
│       ├── fangraphs_scraper2.py
│       └── ...
│
└── front/                         # Frontend
├── MLB_Prediction.html        # Main page
├── MLB_Prediction.css         # Stylesheet
├── MLB_Frontend.js            # Main JavaScript logic
├── MLB_Schedule.js            # Game schedule data
└── MLB_Starters.js            # Team player information

````

## Installation and Execution

### Prerequisites
- Python 3.12
- Chrome browser (for Selenium WebDriver)

### Step 1: Clone Repository and Install Packages

```bash
git clone https://github.com/LutetiumCalciumLee/Web_Scraping_Project_MLB.git
cd Web_Scraping_Project_MLB
pip install flask flask-cors selenium undetected-chromedriver beautifulsoup4
````

### Step 2: Run Backend Server

```bash
cd back
python app.py
```

Server starts at [http://0.0.0.0:5001](http://0.0.0.0:5001) and browser opens automatically.

### Step 3: Initialize Database (Optional)

To batch import existing JSON files into the database:

```bash
cd back
python load_json_to_db.py
```

## Usage

1. Select Date

   * Use date arrows at top to move to previous/next day
   * Click date to select from calendar

2. Select Game

   * Click desired game from list of games on selected date

3. Select Starting Pitchers

   * Choose starting pitchers for away/home teams from dropdown menus

4. Auto Statistics Lookup

   * Once both pitchers are selected, 15 category statistics automatically load

5. Data Visualization

   * Hover over table headers or cells to display comparison chart
   * Compare away and home team statistics with bar graph

## Data Flow

```
User Selection (date/game/pitcher)
       ↓
Frontend calls 15 APIs simultaneously
       ↓
Backend processes by priority
  ├─ Attempt database lookup
  ├─ Check JSON files if not found
  └─ Run scraper to collect if not found
       ↓
Auto save to database after scraping
       ↓
Return JSON data to frontend
       ↓
Parse data and display as table/chart
```

## API Endpoints

All POST endpoints receive requests in the following format:

```json
{
  "selectedDate": "YYYY-MM-DD"
}
```

| Endpoint                | Description                                     |
| ----------------------- | ----------------------------------------------- |
| /scrape-fangraphs       | Starting pitcher base stats (statgroup=1)       |
| /scrape-fangraphs-2     | IP, BB/9 and additional pitcher stats           |
| /scrape-fangraphs-3     | RISP batter stats                               |
| /scrape-fangraphs-4~6   | High Leverage situation pitcher stats           |
| /scrape-fangraphs-7~9   | Medium Leverage situation pitcher stats         |
| /scrape-fangraphs-10~12 | Low Leverage situation pitcher stats            |
| /scrape-fangraphs-13    | Pitcher fatigue check (2+ games in last 2 days) |
| /scrape-fangraphs-14    | Team batting stats                              |
| /scrape-fangraphs-15    | RISP team batting stats                         |
| /load-json-to-db        | Batch save all JSON files to database           |

## Database Schema

fangraphs_data table:

| Field                                                                               | Description           |
| ----------------------------------------------------------------------------------- | --------------------- |
| id                                                                                  | Primary key           |
| date                                                                                | Date (YYYY-MM-DD)     |
| file_index                                                                          | File index (1-15)     |
| rank, season, name, team                                                            | Basic information     |
| games, tbf, era, hits, doubles, triples, runs, earned_runs, home_runs, ip, bb_per_9 | Pitcher stats         |
| walks, intentional_walks, hit_by_pitch, strikeouts                                  | Pitcher stats (cont.) |
| avg, obp, slg, woba                                                                 | Batter stats          |
| created_at                                                                          | Data creation time    |

## Key Features

### Efficient Data Retrieval

Queries in order (DB → file → scraping) to minimize unnecessary web requests and provide fast response times.

### Automated Data Management

JSON files from scrapers automatically save to database, maintaining latest data without manual intervention.

### Robust Collection Strategy

Uses retry handling, randomized pacing, and lightweight interactions (e.g., scrolling when needed) to improve scraping stability and reduce unnecessary load.

### RESTful API Design

15 independent endpoints provide dedicated API for each statistics category with consistent JSON responses.

### Client-Side Rendering

Server provides only data; all UI rendering handled on client side for fast user experience.

## Notes

* Chrome browser installation required for Selenium
* Randomized pacing is applied during collection to reduce unnecessary requests and improve stability
* Large data collection may take time (initial: 1-2 minutes)
* Database file (fangraphs_data.db) automatically generated in project directory

</details>

<details>
<summary>KOR (한국어 버전)</summary>

# MLB 경기 예측 데이터 수집

Fangraphs에서 실시간 투수/타자 통계를 자동 수집하여 MLB 경기 예측을 분석하는 웹 애플리케이션입니다.

## 프로젝트 개요

웹 스크래핑으로 Fangraphs 통계를 자동 수집하고 SQLite에 저장한 후, 인터랙티브 웹 인터페이스에서 경기 일정과 선수 통계를 비교 분석할 수 있는 플랫폼입니다.

## 주요 기능

### 데이터 수집

* Fangraphs 15개 카테고리 통계 자동 수집

  * 선발투수 기본 통계, High/Medium/Low Leverage 상황별 분석, 타격 성적
* 요청 빈도 제어(페이싱)와 재시도 처리로 안정적인 수집
* 스크래핑 후 자동으로 데이터베이스 저장

### 데이터 관리

* SQLite 데이터베이스 중앙 집중식 저장
* 3단계 캐싱 시스템 (DB → 파일 → 스크래핑)으로 불필요한 스크래핑 최소화
* 날짜별 디렉토리 구조로 체계적 관리
* 중복 데이터 자동 방지

### 경기 분석

* 날짜별 MLB 경기 일정 표시
* 원정팀/홈팀 선발투수 선택 및 통계 조회
* High/Medium/Low Leverage 상황별 투수 성적 분석
* 팀별 타격 통계 및 RISP(득점권 타율) 분석
* 최근 2일 내 2경기 이상 출전한 투수 표시

### 데이터 시각화

* Chart.js를 활용한 인터랙티브 비교 차트
* 테이블 헤더/셀 호버 시 자동 차트 표시
* 원정팀과 홈팀 통계를 막대 그래프로 실시간 비교

## 기술 스택

| 분류       | 기술                                                |
| -------- | ------------------------------------------------- |
| Backend  | Python 3.12, Flask, SQLite3                       |
| Scraping | Selenium, undetected_chromedriver, BeautifulSoup4 |
| Frontend | HTML/CSS, JavaScript, Chart.js                    |

## 프로젝트 구조

```
Web_Scraping_Project_MLB/
├── back/                          # 백엔드
│   ├── app.py                     # Flask 메인 서버
│   ├── load_json_to_db.py         # DB 데이터 임포트 스크립트
│   ├── fangraphs_data.db          # SQLite 데이터베이스
│   └── fangraphs_scraper/         # 15개 스크래퍼
│       ├── fangraphs_scraper1.py
│       ├── fangraphs_scraper2.py
│       └── ...
│
└── front/                         # 프론트엔드
    ├── MLB_Prediction.html        # 메인 페이지
    ├── MLB_Prediction.css         # 스타일시트
    ├── MLB_Frontend.js            # 메인 JavaScript 로직
    ├── MLB_Schedule.js            # 경기 일정 데이터
    └── MLB_Starters.js            # 팀별 선수 정보
```

## 설치 및 실행

### 필수 요구사항

* Python 3.12
* Chrome 브라우저 (Selenium WebDriver용)

### 1단계: 저장소 클론 및 패키지 설치

```bash
git clone https://github.com/LutetiumCalciumLee/Web_Scraping_Project_MLB.git
cd Web_Scraping_Project_MLB
pip install flask flask-cors selenium undetected-chromedriver beautifulsoup4
```

### 2단계: 백엔드 서버 실행

```bash
cd back
python app.py
```

서버는 [http://0.0.0.0:5001](http://0.0.0.0:5001) 에서 시작되며 자동으로 브라우저가 열립니다.

### 3단계: 데이터베이스 초기화 (선택사항)

기존 JSON 파일을 데이터베이스에 일괄 저장하려면:

```bash
cd back
python load_json_to_db.py
```

## 사용 방법

1. 날짜 선택

   * 화면 상단의 날짜 화살표로 이전/다음 날 이동
   * 날짜를 클릭하여 캘린더에서 원하는 날짜 선택

2. 경기 선택

   * 선택한 날짜의 경기 목록에서 원하는 경기 클릭

3. 선발투수 선택

   * 원정팀/홈팀의 선발투수 드롭다운 메뉴에서 선택

4. 통계 자동 조회

   * 양 팀 투수가 모두 선택되면 자동으로 15개 카테고리 통계 로드

5. 데이터 시각화

   * 테이블의 통계 헤더나 셀에 마우스를 올리면 비교 차트 자동 표시
   * 원정팀과 홈팀의 통계를 막대 그래프로 비교

## 데이터 흐름

```
사용자 선택 (날짜/경기/투수)
       ↓
프론트엔드에서 15개 API 동시 호출
       ↓
백엔드 데이터 우선순위 처리
  ├─ 데이터베이스에서 조회 시도
  ├─ 없으면 JSON 파일 확인
  └─ 없으면 스크래퍼 실행하여 수집
       ↓
스크래핑 완료 후 자동으로 DB 저장
       ↓
JSON 데이터 프론트엔드 반환
       ↓
데이터 파싱 및 테이블/차트로 표시
```

## API 엔드포인트

모든 POST 엔드포인트는 다음 형식의 요청을 받습니다:

```json
{
  "selectedDate": "YYYY-MM-DD"
}
```

| 엔드포인트                   | 설명                       |
| ----------------------- | ------------------------ |
| /scrape-fangraphs       | 선발투수 기본 통계 (statgroup=1) |
| /scrape-fangraphs-2     | IP, BB/9 등 추가 투수 통계      |
| /scrape-fangraphs-3     | RISP 타자 통계               |
| /scrape-fangraphs-4~6   | High Leverage 상황 투수 통계   |
| /scrape-fangraphs-7~9   | Medium Leverage 상황 투수 통계 |
| /scrape-fangraphs-10~12 | Low Leverage 상황 투수 통계    |
| /scrape-fangraphs-13    | 투수 피로도 체크 (최근 2일 2경기+)   |
| /scrape-fangraphs-14    | 팀 타격 통계                  |
| /scrape-fangraphs-15    | RISP 팀 타격 통계             |
| /load-json-to-db        | 모든 JSON 파일을 DB에 일괄 저장    |

## 데이터베이스 스키마

fangraphs_data 테이블:

| 필드                                                                                  | 설명              |
| ----------------------------------------------------------------------------------- | --------------- |
| id                                                                                  | 기본 키            |
| date                                                                                | 날짜 (YYYY-MM-DD) |
| file_index                                                                          | 파일 인덱스 (1-15)   |
| rank, season, name, team                                                            | 기본 정보           |
| games, tbf, era, hits, doubles, triples, runs, earned_runs, home_runs, ip, bb_per_9 | 투수 통계           |
| walks, intentional_walks, hit_by_pitch, strikeouts                                  | 투수 통계 (계속)      |
| avg, obp, slg, woba                                                                 | 타자 통계           |
| created_at                                                                          | 데이터 생성 시간       |

## 주요 특징

### 효율적인 데이터 조회

DB → 파일 → 스크래핑 순서로 조회하여 불필요한 웹 요청 최소화하고 빠른 응답 속도를 제공합니다.

### 자동화된 데이터 관리

스크래퍼 실행 후 JSON 파일 생성 시 자동으로 데이터베이스에 저장되어 수동 작업 없이 최신 데이터를 유지합니다.

### 안정적인 수집 전략

재시도 처리, 랜덤 페이싱(요청 간 간격), 필요 시 최소한의 사용자 상호작용(예: 스크롤)으로 수집 안정성을 높이고 불필요한 부하를 줄입니다.

### RESTful API 설계

15개의 독립적인 엔드포인트로 각 통계 카테고리별 전용 API를 제공하며 일관된 JSON 응답을 반환합니다.

### 클라이언트 사이드 렌더링

서버는 데이터만 제공하고 모든 UI 렌더링을 클라이언트에서 처리하여 빠른 사용자 경험을 제공합니다.

## 주의사항

* Selenium 사용으로 Chrome 브라우저 필수 설치
* 수집 과정에서 안정성 확보를 위해 페이싱(요청 간 간격)을 적용
* 대량의 데이터 수집 시 시간 소요 (초기: 1-2분)
* 데이터베이스 파일(fangraphs_data.db)은 프로젝트 디렉토리에 자동 생성

</details>
