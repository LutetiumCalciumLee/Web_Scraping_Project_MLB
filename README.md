<details>
<summary>ENG (English Version)</summary>

# Web Scraping and Data Collection Techniques

## 1. Overview of Web Scraping

Web scraping is a technique for extracting data from websites and converting unstructured web data into structured formats. It involves automated collection of information from web pages using various tools and libraries.

### Key Concepts

**Web Crawling vs. Web Scraping:**
- Web Crawling: Systematically visits all links on a website, builds an index, and stores data in a database
- Web Scraping: Extracts specific information from web pages, focuses on data extraction from targeted sources

**Popular Tools and Libraries:**
- Selenium: Browser automation for JavaScript-heavy websites
- BeautifulSoup: HTML/XML parsing for static content
- Requests: Lightweight HTTP library for fetching web pages
- Scrapy: Full-featured web scraping framework
- Octoparse, HTTrack, Cytoek WebCopy: GUI-based crawling tools

## 2. Naver News Scraping with Selenium

Purpose: Collect news articles from Naver News search results

### 2.1 Setup and Dependencies

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv
```

### 2.2 Key Functions

**Page Down Navigation:**
```python
def pagedown(num, body):
    driver.findElement(By.CSS_SELECTOR, body).click()
    for i in range(num):
        body.sendKeys(Keys.PAGEDOWN)
        time.sleep(3)
```

### 2.3 Main Scraping Workflow

```python
url = "https://www.naver.com"
driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)
driver.implicitly_wait(10)

# Find search box and enter query
searchbox = driver.findElement(By.CSS_SELECTOR, "input[query]")
searchbox.sendKeys(query)
searchbox.sendKeys(Keys.RETURN)
driver.implicitly_wait(10)

# Click on News tab
driver.findElement(By.LINK_TEXT, "News").click()

# Handle "More Results" button
while True:
    btn = driver.findElement(By.LINK_TEXT, "More Results")
    if btn.isDisplayed():
        btn.click()
        driver.implicitly_wait(10)
        time.sleep(3)
        break
    else:
        driver.findElement(By.LINK_TEXT, "Next Page").click()

# Page down for loading more content
pagedown(100)

# Extract news data
newstitles = driver.findElements(By.CSS_SELECTOR, ".fender-ui228e3bd1.SR2LrlI9g02spd3asYd0")
newspress = driver.findElements(By.CSS_SELECTOR, ".fender-ui228e3bd1.CuEBGQMQA1RcBJH6fbf")
newsdate = driver.findElements(By.XPATH, "//div[@class='sds-comps-vertical-layout sds-comps-full-layout zc470m0U4oRqtEfZ3YqXd']//div[1]//div[1]//div[2]//span[2]//div//span")
newsdes = driver.findElements(By.CSS_SELECTOR, ".fender-ui228e3bd1.UCEthQP80sQ2n8CkLMc8")

# Save to CSV
with open('filename.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    attributes = ['Press', 'Date', 'Title', 'Link', 'Description']
    writer.writerow(attributes)
    
    for i in range(len(newspress)):
        press = newspress[i].text
        date = newsdate[i].text
        title = newstitles[i].text
        link = newstitles[i].getAttribute('href')
        des = newsdes[i].text
        
        datarows = [press, date, title, link, des]
        writer.writerow(datarows)
```

## 3. IMDB Series Data Scraping

Purpose: Extract episode information from IMDB TV series pages

### 3.1 URL Structure

```python
url = "https://www.imdb.com/title/tt0898266/episodes?ref=tt_eps"
```

### 3.2 Episode Extraction

```python
hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

res = requests.get(url, headers=hdr)
res.raise_for_status()

soup = BeautifulSoup(res.text, 'lxml')

# Find all episodes
episodes = soup.find_all('article', attrs={'class': 'sc-64257d69-1 mOJzu episode-item-wrapper'})

for episode in episodes:
    # Extract title
    title = episode.find('a', attrs={'class': 'ipc-title-link-wrapper'}).getText()
    
    # Extract date
    dateexist = episode.find('span', attrs={'class': 'sc-5372d523-10 knzESm'})
    date = dateexist.getText() if dateexist != None else ""
    
    # Extract rating and vote count
    ratingvotecountexist = episode.find('span', attrs={
        'class': 'ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating'
    })
    
    if ratingvotecountexist != None:
        ratingvotecount = ratingvotecountexist.getText()
        rating = ratingvotecount[0:3]
        votecount = ratingvotecount[8:11]
    else:
        rating = "0"
        votecount = "0"
    
    # Extract description
    descrexist = episode.find('div', attrs={'class': 'ipc-html-content-inner-div'})
    descr = descrexist.getText() if descrexist != None else ""
    
    print(title, date, rating, votecount, descr)
    
    # Save to CSV
    datarows = [title, date, rating, votecount, descr]
    writer.writerow(datarows)
```

## 4. Naver Map Scraping

Purpose: Extract location information from Naver Map search results

### 4.1 Setup with Explicit Wait

```python
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

loc = ""
url = f"https://map.naver.com/v5/search.{loc}"

driver = webdriver.Chrome()
driver.get(url)

# Wait for element with 10 second timeout
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inputsearch"))
    )
finally:
    pass

driver.implicitly_wait(10)
```

### 4.2 Data Collection Loop

```python
res = pd.DataFrame()

# Switch to search iframe
driver.switch_to.frame("searchIframe")

for i in range(10):
    while True:
        pagedown(5)
        
        # Find all location items
        lists = driver.findElements(By.CSS_SELECTOR, "li.VLTHu")
        names = driver.findElements(By.CSS_SELECTOR, ".YwYLL")
        types = driver.findElements(By.CSS_SELECTOR, ".YzBgS")
        addrs = driver.findElements(By.CSS_SELECTOR, ".Pb4bU")
        dist = driver.findElements(By.CSS_SELECTOR, ".NVngW")
        
        # Extract data
        for index in range(len(addrs)):
            print(names[index].text, types[index].text, 
                  addrs[index].text, dist[index].text[8:])
            
            res = pd.concat([res, pd.DataFrame({
                'name': [names[index].text],
                'type': [types[index].text],
                'address': [addrs[index].text],
                'distance': [dist[index].text[8:]]
            })])
        
        # Save to CSV
        res.to_csv('naverMap_locations.csv', index=False, encoding='utf-8-sig')
        
        # Find and click next page button
        e = driver.findElement(By.XPATH, "id('app-root')")
        b = e.findElements(By.CLASS_NAME, "eUTV2")
        
        if b[1].getAttribute('aria-disabled') == 'false':
            b[1].click()
            time.sleep(5)
        else:
            break

driver.close()
```

### 4.3 Pagination Handling

The script implements automatic pagination by:
1. Detecting the "Next" button state using aria-disabled attribute
2. Clicking next button if available (aria-disabled = false)
3. Breaking loop when no more pages available (aria-disabled = true)

## 5. Best Practices

Selector Priority:
1. ID selectors (most specific)
2. Class selectors
3. XPath selectors
4. CSS selectors
5. Link text selectors

Timing Strategies:
- Use implicit_wait() for general element loading
- Use explicit WebDriverWait for critical elements
- Add time.sleep() between major actions
- Page down for lazy-loading content

Data Validation:
- Check for None values before accessing attributes
- Verify element existence before interaction
- Handle exceptions for failed element finds

CSV Output Standardization:
- Use utf-8-sig encoding for Korean characters
- Set newline='' to prevent blank rows
- Include proper headers
- Reset index when concatenating DataFrames

</details>

<details>
<summary>KOR (한국어 버전)</summary>

# 웹 스크래핑 및 데이터 수집 기법

## 1. 웹 스크래핑 개요

웹 스크래핑은 웹사이트에서 데이터를 추출하고 비정형 웹 데이터를 정형화된 형식으로 변환하는 기법입니다. 다양한 도구와 라이브러리를 사용하여 웹 페이지에서 정보를 자동으로 수집합니다.

### 주요 개념

**웹 크롤링 vs. 웹 스크래핑:**
- 웹 크롤링: 웹사이트의 모든 링크를 체계적으로 방문하고 인덱스를 구축하며 데이터베이스에 저장
- 웹 스크래핑: 웹 페이지에서 특정 정보를 추출하고 목표 소스에서 데이터 추출에 중점

**인기 있는 도구 및 라이브러리:**
- Selenium: JavaScript가 많은 웹사이트를 위한 브라우저 자동화
- BeautifulSoup: 정적 콘텐츠를 위한 HTML/XML 파싱
- Requests: 웹 페이지를 가져오기 위한 경량 HTTP 라이브러리
- Scrapy: 완전한 기능의 웹 스크래핑 프레임워크
- Octoparse, HTTrack, Cytoek WebCopy: GUI 기반 크롤링 도구

## 2. Selenium을 사용한 네이버 뉴스 스크래핑

목적: 네이버 뉴스 검색 결과에서 뉴스 기사 수집

### 2.1 설정 및 의존성

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv
```

### 2.2 주요 함수

**페이지 다운 네비게이션:**
```python
def pagedown(num, body):
    driver.findElement(By.CSS_SELECTOR, body).click()
    for i in range(num):
        body.sendKeys(Keys.PAGEDOWN)
        time.sleep(3)
```

### 2.3 메인 스크래핑 워크플로우

```python
url = "https://www.naver.com"
driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)
driver.implicitly_wait(10)

# 검색 상자 찾기 및 쿼리 입력
searchbox = driver.findElement(By.CSS_SELECTOR, "input[query]")
searchbox.sendKeys(query)
searchbox.sendKeys(Keys.RETURN)
driver.implicitly_wait(10)

# 뉴스 탭 클릭
driver.findElement(By.LINK_TEXT, "뉴스").click()

# "더보기" 버튼 처리
while True:
    btn = driver.findElement(By.LINK_TEXT, "더보기")
    if btn.isDisplayed():
        btn.click()
        driver.implicitly_wait(10)
        time.sleep(3)
        break
    else:
        driver.findElement(By.LINK_TEXT, "다음 페이지").click()

# 더 많은 콘텐츠 로드를 위해 페이지 다운
pagedown(100)

# 뉴스 데이터 추출
newstitles = driver.findElements(By.CSS_SELECTOR, ".fender-ui228e3bd1.SR2LrlI9g02spd3asYd0")
newspress = driver.findElements(By.CSS_SELECTOR, ".fender-ui228e3bd1.CuEBGQMQA1RcBJH6fbf")
newsdate = driver.findElements(By.XPATH, "//div[@class='sds-comps-vertical-layout sds-comps-full-layout zc470m0U4oRqtEfZ3YqXd']//div[1]//div[1]//div[2]//span[2]//div//span")
newsdes = driver.findElements(By.CSS_SELECTOR, ".fender-ui228e3bd1.UCEthQP80sQ2n8CkLMc8")

# CSV에 저장
with open('파일명.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    attributes = ['언론사', '날짜', '제목', '링크', '설명']
    writer.writerow(attributes)
    
    for i in range(len(newspress)):
        press = newspress[i].text
        date = newsdate[i].text
        title = newstitles[i].text
        link = newstitles[i].getAttribute('href')
        des = newsdes[i].text
        
        datarows = [press, date, title, link, des]
        writer.writerow(datarows)
```

## 3. IMDB 드라마 데이터 스크래핑

목적: IMDB TV 시리즈 페이지에서 에피소드 정보 추출

### 3.1 URL 구조

```python
url = "https://www.imdb.com/title/tt0898266/episodes?ref=tt_eps"
```

### 3.2 에피소드 추출

```python
hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

res = requests.get(url, headers=hdr)
res.raise_for_status()

soup = BeautifulSoup(res.text, 'lxml')

# 모든 에피소드 찾기
episodes = soup.find_all('article', attrs={'class': 'sc-64257d69-1 mOJzu episode-item-wrapper'})

for episode in episodes:
    # 제목 추출
    title = episode.find('a', attrs={'class': 'ipc-title-link-wrapper'}).getText()
    
    # 방영일 추출
    dateexist = episode.find('span', attrs={'class': 'sc-5372d523-10 knzESm'})
    date = dateexist.getText() if dateexist != None else ""
    
    # 평점 및 투표 수 추출
    ratingvotecountexist = episode.find('span', attrs={
        'class': 'ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating'
    })
    
    if ratingvotecountexist != None:
        ratingvotecount = ratingvotecountexist.getText()
        rating = ratingvotecount[0:3]
        votecount = ratingvotecount[8:11]
    else:
        rating = "0"
        votecount = "0"
    
    # 설명 추출
    descrexist = episode.find('div', attrs={'class': 'ipc-html-content-inner-div'})
    descr = descrexist.getText() if descrexist != None else ""
    
    print(title, date, rating, votecount, descr)
    
    # CSV에 저장
    datarows = [title, date, rating, votecount, descr]
    writer.writerow(datarows)
```

## 4. 네이버 지도 스크래핑

목적: 네이버 지도 검색 결과에서 위치 정보 추출

### 4.1 명시적 대기를 사용한 설정

```python
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

loc = ""
url = f"https://map.naver.com/v5/search.{loc}"

driver = webdriver.Chrome()
driver.get(url)

# 10초 타임아웃을 사용하여 요소 대기
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inputsearch"))
    )
finally:
    pass

driver.implicitly_wait(10)
```

### 4.2 데이터 수집 루프

```python
res = pd.DataFrame()

# 검색 iframe으로 전환
driver.switch_to.frame("searchIframe")

for i in range(10):
    while True:
        pagedown(5)
        
        # 모든 위치 항목 찾기
        lists = driver.findElements(By.CSS_SELECTOR, "li.VLTHu")
        names = driver.findElements(By.CSS_SELECTOR, ".YwYLL")
        types = driver.findElements(By.CSS_SELECTOR, ".YzBgS")
        addrs = driver.findElements(By.CSS_SELECTOR, ".Pb4bU")
        dist = driver.findElements(By.CSS_SELECTOR, ".NVngW")
        
        # 데이터 추출
        for index in range(len(addrs)):
            print(names[index].text, types[index].text, 
                  addrs[index].text, dist[index].text[8:])
            
            res = pd.concat([res, pd.DataFrame({
                'name': [names[index].text],
                'type': [types[index].text],
                'address': [addrs[index].text],
                'distance': [dist[index].text[8:]]
            })])
        
        # CSV에 저장
        res.to_csv('naverMap_locations.csv', index=False, encoding='utf-8-sig')
        
        # 다음 페이지 버튼 찾기 및 클릭
        e = driver.findElement(By.XPATH, "id('app-root')")
        b = e.findElements(By.CLASS_NAME, "eUTV2")
        
        if b[1].getAttribute('aria-disabled') == 'false':
            b[1].click()
            time.sleep(5)
        else:
            break

driver.close()
```

### 4.3 페이지네이션 처리

스크립트는 다음을 통해 자동 페이지네이션을 구현합니다:
1. aria-disabled 속성을 사용하여 "다음" 버튼 상태 감지
2. 사용 가능한 경우 다음 버튼 클릭 (aria-disabled = false)
3. 더 이상 페이지가 없을 때 루프 종료 (aria-disabled = true)

## 5. 모범 사례

선택자 우선순위:
1. ID 선택자 (가장 구체적)
2. 클래스 선택자
3. XPath 선택자
4. CSS 선택자
5. 링크 텍스트 선택자

타이밍 전략:
- 일반적인 요소 로드를 위해 implicit_wait() 사용
- 중요한 요소를 위해 명시적 WebDriverWait 사용
- 주요 작업 사이에 time.sleep() 추가
- 레이지 로딩 콘텐츠를 위해 페이지 다운

데이터 유효성 검증:
- 속성에 접근하기 전에 None 값 확인
- 상호작용 전에 요소 존재 확인
- 실패한 요소 찾기에 대한 예외 처리

CSV 출력 표준화:
- 한글 문자를 위해 utf-8-sig 인코딩 사용
- 빈 행을 방지하기 위해 newline='' 설정
- 적절한 헤더 포함
- DataFrame 연결 시 인덱스 재설정

</details>
