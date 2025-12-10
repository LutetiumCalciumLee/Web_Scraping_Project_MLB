import json
import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta

# 명령줄 인자로 선택된 날짜 받기 (YYYY-MM-DD 형식)
# 인자가 없으면 오늘 날짜 사용
if len(sys.argv) > 1:
    selected_date_str = sys.argv[1]
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
    except ValueError:
        print(f"날짜 형식 오류: {selected_date_str}. YYYY-MM-DD 형식으로 입력해주세요.")
        sys.exit(1)
else:
    # 인자가 없으면 오늘 날짜 사용
    selected_date = datetime.now()
    selected_date_str = selected_date.strftime("%Y-%m-%d")

# startDate: 선택일 - 7일, endDate: 선택일 - 1일
start_date = (selected_date - timedelta(days=7)).strftime("%Y-%m-%d")
end_date = (selected_date - timedelta(days=1)).strftime("%Y-%m-%d")

print(f"선택된 날짜: {selected_date.strftime('%Y-%m-%d')}")
print(f"startDate (선택일 -7): {start_date}")
print(f"endDate (선택일 -1): {end_date}")

# undetected_chromedriver 설정 (Cloudflare 우회)
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# headless 모드는 Cloudflare 탐지에 걸릴 수 있으므로 주석 처리
# options.add_argument("--headless=new")

# undetected_chromedriver로 드라이버 생성
driver = uc.Chrome(options=options, version_main=None)

# Fangraphs URL with dynamic dates (splitArr=59, statgroup=1, position=B, filter=PA|gt|7)
url = (
    "https://www.fangraphs.com/leaders/splits-leaderboards"
    f"?splitArr=59&splitArrPitch=&autoPt=false&splitTeams=true"
    f"&statType=player&statgroup=1"
    f"&startDate={start_date}&endDate={end_date}"
    "&players=&filter=PA%7Cgt%7C7&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=22,1&pageitems=2000000000&pg=0"
)

print("페이지 로딩 중...")
driver.get(url)

# 테이블 로드 대기 (클래스 'table-scroll' 안에 테이블)
try:
    # 더 긴 대기시간으로 변경
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table-scroll"))
    )
    
    # 랜덤한 대기시간 추가 (3-8초 사이)
    wait_time = random.uniform(3, 8)
    print(f"데이터 로드 대기 중... {wait_time:.1f}초")
    time.sleep(wait_time)
    
    # 추가적으로 스크롤이나 마우스 움직임 흉내 내기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
    time.sleep(random.uniform(1, 2))
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random.uniform(1, 2))

    # 페이지 소스 가져와 BeautifulSoup으로 파싱 (쉬운 추출 위해)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table_div = soup.find('div', class_='table-scroll')
    if not table_div:
        raise Exception("Table div not found.")

    table = table_div.find('table')
    if not table:
        raise Exception("Table not found.")

    # 헤더 추출
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]

    # 데이터 행 추출
    data = []
    for tr in table.find('tbody').find_all('tr'):
        row = {}
        cells = tr.find_all('td')
        for i, cell in enumerate(cells):
            col_id = cell.get('data-col-id')
            stat = cell.get('data-stat')
            key = stat or col_id or headers[i]  # 키 우선순위: data-stat > data-col-id > header
            row[key] = cell.text.strip()
        data.append(row)

    # JSON으로 저장 (파일명: fangraphs_data_{선택일}_16.json)
    # 날짜별 디렉토리 생성
    date_dir = f"fangraphs_data_{selected_date_str}"
    os.makedirs(date_dir, exist_ok=True)
    
    # JSON으로 저장 (파일명: fangraphs_data_{선택일}/fangraphs_data_{선택일}_16.json)
    output_filename = os.path.join(date_dir, f"fangraphs_data_{selected_date_str}_16.json")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"데이터가 {output_filename} 파일로 저장되었습니다. 총 {len(data)} 행.")
    print(f"헤더: {headers}")
    print(f"샘플 데이터: {data[:2]}")  # 첫 두 행 출력

except Exception as e:
    print(f"에러: {str(e)} - URL이나 테이블 구조 확인하세요. Fangraphs가 로드 안 될 수 있음.")
finally:
    driver.quit()

