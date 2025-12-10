import json
import os
import subprocess
import threading
import time
import webbrowser
import sqlite3
import glob
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # file:// 등의 origin에서 접근 허용

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPER_DIR = os.path.join(BASE_DIR, "fangraphs_scraper")
SCRAPER_SCRIPT = os.path.join(SCRAPER_DIR, "fangraphs_scraper1.py")
SCRAPER_SCRIPT_2 = os.path.join(SCRAPER_DIR, "fangraphs_scraper2.py")
SCRAPER_SCRIPT_3 = os.path.join(SCRAPER_DIR, "fangraphs_scraper3.py")
SCRAPER_SCRIPT_4 = os.path.join(SCRAPER_DIR, "fangraphs_scraper4.py")
SCRAPER_SCRIPT_5 = os.path.join(SCRAPER_DIR, "fangraphs_scraper5.py")
SCRAPER_SCRIPT_6 = os.path.join(SCRAPER_DIR, "fangraphs_scraper6.py")
SCRAPER_SCRIPT_7 = os.path.join(SCRAPER_DIR, "fangraphs_scraper7.py")
SCRAPER_SCRIPT_8 = os.path.join(SCRAPER_DIR, "fangraphs_scraper8.py")
SCRAPER_SCRIPT_9 = os.path.join(SCRAPER_DIR, "fangraphs_scraper9.py")
SCRAPER_SCRIPT_10 = os.path.join(SCRAPER_DIR, "fangraphs_scraper10.py")
SCRAPER_SCRIPT_11 = os.path.join(SCRAPER_DIR, "fangraphs_scraper11.py")
SCRAPER_SCRIPT_12 = os.path.join(SCRAPER_DIR, "fangraphs_scraper12.py")
SCRAPER_SCRIPT_13 = os.path.join(SCRAPER_DIR, "fangraphs_scraper13.py")
SCRAPER_SCRIPT_14 = os.path.join(SCRAPER_DIR, "fangraphs_scraper14.py")
SCRAPER_SCRIPT_15 = os.path.join(SCRAPER_DIR, "fangraphs_scraper15.py")
FRONT_HTML_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "front", "MLB_Prediction.html"))
DB_PATH = os.path.join(BASE_DIR, "fangraphs_data.db")


def output_path(selected_date: str, suffix: str = "1") -> str:
    """선택된 날짜 기반 결과 JSON 경로 반환 (날짜별 디렉토리 구조)"""
    date_dir = os.path.join(BASE_DIR, f"fangraphs_data_{selected_date}")
    # 디렉토리가 없으면 생성
    os.makedirs(date_dir, exist_ok=True)
    return os.path.join(date_dir, f"fangraphs_data_{selected_date}_{suffix}.json")


def init_database():
    """SQLite 데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fangraphs_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            file_index TEXT NOT NULL,
            rank TEXT,
            season TEXT,
            name TEXT,
            team TEXT,
            games TEXT,
            tbf TEXT,
            era TEXT,
            hits TEXT,
            doubles TEXT,
            triples TEXT,
            runs TEXT,
            earned_runs TEXT,
            home_runs TEXT,
            walks TEXT,
            intentional_walks TEXT,
            hit_by_pitch TEXT,
            strikeouts TEXT,
            avg TEXT,
            obp TEXT,
            slg TEXT,
            woba TEXT,
            ip TEXT,
            bb_per_9 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, file_index, name, season)
        )
    """)
    
    # 기존 테이블에 필드가 없으면 추가 (마이그레이션)
    try:
        cursor.execute("ALTER TABLE fangraphs_data ADD COLUMN ip TEXT")
    except sqlite3.OperationalError:
        pass  # 이미 존재하는 경우
    
    try:
        cursor.execute("ALTER TABLE fangraphs_data ADD COLUMN bb_per_9 TEXT")
    except sqlite3.OperationalError:
        pass  # 이미 존재하는 경우
    
    conn.commit()
    conn.close()
    app.logger.info(f"데이터베이스 초기화 완료: {DB_PATH}")


def save_json_to_db(json_file_path: str):
    """JSON 파일을 읽어서 데이터베이스에 저장"""
    # 데이터베이스가 초기화되지 않았을 수 있으므로 먼저 초기화
    init_database()
    
    try:
        # 파일 경로에서 날짜와 인덱스 추출
        # 예: fangraphs_data_2025-06-26/fangraphs_data_2025-06-26_1.json
        filename = os.path.basename(json_file_path)
        dirname = os.path.basename(os.path.dirname(json_file_path))
        
        # 날짜 추출 (fangraphs_data_2025-06-26 -> 2025-06-26)
        if dirname.startswith("fangraphs_data_"):
            date = dirname.replace("fangraphs_data_", "")
        else:
            date = "unknown"
        
        # 파일 인덱스 추출 (fangraphs_data_2025-06-26_1.json -> 1)
        if "_" in filename:
            parts = filename.replace(".json", "").split("_")
            file_index = parts[-1] if parts else "1"
        else:
            file_index = "1"
        
        # JSON 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            app.logger.warning(f"JSON 파일이 배열 형식이 아닙니다: {json_file_path}")
            return False
        
        # 데이터베이스 연결
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        saved_count = 0
        skipped_count = 0
        
        for player in data:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO fangraphs_data 
                    (date, file_index, rank, season, name, team, games, tbf, era, hits, 
                     doubles, triples, runs, earned_runs, home_runs, walks, intentional_walks,
                     hit_by_pitch, strikeouts, avg, obp, slg, woba, ip, bb_per_9)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    file_index,
                    player.get("#", ""),
                    player.get("Season", ""),
                    player.get("Name", ""),
                    player.get("Tm", ""),
                    player.get("G", ""),
                    player.get("TBF", ""),
                    player.get("ERA", ""),
                    player.get("H", ""),
                    player.get("2B", ""),
                    player.get("3B", ""),
                    player.get("R", ""),
                    player.get("ER", ""),
                    player.get("HR", ""),
                    player.get("BB", ""),
                    player.get("IBB", ""),
                    player.get("HBP", ""),
                    player.get("SO", ""),
                    player.get("AVG", ""),
                    player.get("OBP", ""),
                    player.get("SLG", ""),
                    player.get("wOBA", ""),
                    player.get("IP", ""),
                    player.get("BB/9", "")
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                app.logger.error(f"선수 데이터 저장 실패: {player.get('Name', 'Unknown')} - {str(e)}")
                skipped_count += 1
        
        conn.commit()
        conn.close()
        
        app.logger.info(f"파일 저장 완료: {json_file_path} (저장: {saved_count}, 건너뜀: {skipped_count})")
        return True
        
    except Exception as e:
        app.logger.error(f"JSON 파일 저장 실패: {json_file_path} - {str(e)}")
        return False


def load_all_json_to_db():
    """모든 JSON 파일을 찾아서 데이터베이스에 저장"""
    init_database()
    
    # 모든 fangraphs_data_* 디렉토리 찾기
    pattern = os.path.join(BASE_DIR, "fangraphs_data_*", "*.json")
    json_files = glob.glob(pattern)
    
    if not json_files:
        app.logger.warning("저장할 JSON 파일을 찾을 수 없습니다.")
        return {"success": False, "message": "JSON 파일을 찾을 수 없습니다.", "processed": 0}
    
    app.logger.info(f"총 {len(json_files)}개의 JSON 파일을 찾았습니다.")
    
    processed = 0
    failed = 0
    
    for json_file in json_files:
        if save_json_to_db(json_file):
            processed += 1
        else:
            failed += 1
    
    return {
        "success": True,
        "message": f"처리 완료: 성공 {processed}개, 실패 {failed}개",
        "processed": processed,
        "failed": failed,
        "total": len(json_files)
    }


def get_data_from_db(selected_date: str, file_index: str):
    """데이터베이스에서 특정 날짜와 파일 인덱스의 데이터 조회"""
    if not os.path.exists(DB_PATH):
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rank, season, name, team, games, tbf, era, hits, doubles, triples,
                   runs, earned_runs, home_runs, walks, intentional_walks, hit_by_pitch,
                   strikeouts, avg, obp, slg, woba, ip, bb_per_9
            FROM fangraphs_data
            WHERE date = ? AND file_index = ?
            ORDER BY CAST(rank AS INTEGER)
        """, (selected_date, file_index))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
        
        # 데이터베이스 결과를 JSON 형식으로 변환
        result = []
        for row in rows:
            result.append({
                "#": row[0] or "",
                "Season": row[1] or "",
                "Name": row[2] or "",
                "Tm": row[3] or "",
                "G": row[4] or "",
                "TBF": row[5] or "",
                "ERA": row[6] or "",
                "H": row[7] or "",
                "2B": row[8] or "",
                "3B": row[9] or "",
                "R": row[10] or "",
                "ER": row[11] or "",
                "HR": row[12] or "",
                "BB": row[13] or "",
                "IBB": row[14] or "",
                "HBP": row[15] or "",
                "SO": row[16] or "",
                "AVG": row[17] or "",
                "OBP": row[18] or "",
                "SLG": row[19] or "",
                "wOBA": row[20] or "",
                "IP": row[21] or "",
                "BB/9": row[22] or ""
            })
        
        app.logger.info(f"데이터베이스에서 데이터 조회: 날짜={selected_date}, 인덱스={file_index}, 레코드 수={len(result)}")
        return result
        
    except Exception as e:
        app.logger.error(f"데이터베이스 조회 실패: {str(e)}")
        return None


def get_fangraphs_data(selected_date: str, file_index: str, scraper_script: str):
    """데이터 조회 공통 함수: DB -> 파일 -> 스크래핑 순서로 시도"""
    # 1. 먼저 데이터베이스에서 조회
    db_data = get_data_from_db(selected_date, file_index)
    if db_data is not None:
        app.logger.info(f"데이터베이스에서 데이터 반환: 날짜={selected_date}, 인덱스={file_index}")
        return db_data, None
    
    output_file = output_path(selected_date, file_index)
    
    # 2. 데이터베이스에 없으면 파일 확인
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            app.logger.info(f"기존 파일 사용: {output_file}")
            # 파일은 있지만 DB에 없는 경우 자동으로 DB에 저장
            try:
                if save_json_to_db(output_file):
                    app.logger.info(f"기존 파일 자동 DB 저장 완료: {output_file}")
            except Exception as e:
                app.logger.warning(f"기존 파일 자동 DB 저장 중 오류: {str(e)}")
            return data, None
        except Exception as e:
            app.logger.warning(f"기존 파일 로드 실패, 스크래핑 실행: {str(e)}")
    
    # 3. 파일도 없으면 스크래퍼 실행
    try:
        result = subprocess.run(
            ["python", scraper_script, selected_date],
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        app.logger.info("scraper stdout: %s", result.stdout)
        app.logger.info("scraper stderr: %s", result.stderr)
    except subprocess.CalledProcessError as e:
        return None, {"error": "스크래퍼 실행 실패", "detail": e.stderr}

    if not os.path.exists(output_file):
        return None, {"error": f"결과 파일이 없습니다: {output_file}"}

    # 4. 스크래퍼 실행 후 JSON 파일이 생성되면 자동으로 데이터베이스에 저장
    try:
        if save_json_to_db(output_file):
            app.logger.info(f"자동 DB 저장 완료: {output_file}")
        else:
            app.logger.warning(f"자동 DB 저장 실패: {output_file}")
    except Exception as e:
        app.logger.error(f"자동 DB 저장 중 오류 발생: {str(e)}")
        # DB 저장 실패해도 데이터는 반환 (파일은 존재하므로)

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return None, {"error": "JSON 로드 실패", "detail": str(e)}

    return data, None


@app.route("/scrape-fangraphs", methods=["POST"])
def scrape_fangraphs():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "1", SCRAPER_SCRIPT)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-2", methods=["POST"])
def scrape_fangraphs_2():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "2", SCRAPER_SCRIPT_2)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-3", methods=["POST"])
def scrape_fangraphs_3():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "3", SCRAPER_SCRIPT_3)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-4", methods=["POST"])
def scrape_fangraphs_4():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "4", SCRAPER_SCRIPT_4)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-5", methods=["POST"])
def scrape_fangraphs_5():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "5", SCRAPER_SCRIPT_5)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-6", methods=["POST"])
def scrape_fangraphs_6():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "6", SCRAPER_SCRIPT_6)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-7", methods=["POST"])
def scrape_fangraphs_7():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "7", SCRAPER_SCRIPT_7)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-8", methods=["POST"])
def scrape_fangraphs_8():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "8", SCRAPER_SCRIPT_8)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-9", methods=["POST"])
def scrape_fangraphs_9():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "9", SCRAPER_SCRIPT_9)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-10", methods=["POST"])
def scrape_fangraphs_10():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "10", SCRAPER_SCRIPT_10)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-11", methods=["POST"])
def scrape_fangraphs_11():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "11", SCRAPER_SCRIPT_11)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-12", methods=["POST"])
def scrape_fangraphs_12():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "12", SCRAPER_SCRIPT_12)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-13", methods=["POST"])
def scrape_fangraphs_13():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "13", SCRAPER_SCRIPT_13)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-14", methods=["POST"])
def scrape_fangraphs_14():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "14", SCRAPER_SCRIPT_14)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/scrape-fangraphs-15", methods=["POST"])
def scrape_fangraphs_15():
    payload = request.get_json(force=True, silent=True) or {}
    selected_date = payload.get("selectedDate")

    if not selected_date:
        return jsonify({"error": "selectedDate가 필요합니다. 형식: YYYY-MM-DD"}), 400

    data, error = get_fangraphs_data(selected_date, "15", SCRAPER_SCRIPT_15)
    if error:
        return jsonify(error), 500
    return jsonify(data), 200


@app.route("/load-json-to-db", methods=["POST"])
def load_json_to_db():
    """모든 JSON 파일을 데이터베이스에 저장하는 엔드포인트"""
    try:
        result = load_all_json_to_db()
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"데이터베이스 저장 중 오류 발생: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # 프론트 HTML 자동 오픈 (비차단)
    def _open_frontend():
        time.sleep(1)  # 서버가 뜰 시간을 확보
        if os.path.exists(FRONT_HTML_PATH):
            # Windows에서도 동작하도록 파일 URL 구성
            file_url = "file:///" + FRONT_HTML_PATH.replace("\\", "/")
            webbrowser.open(file_url)
        else:
            app.logger.warning("프론트 파일을 찾지 못했습니다: %s", FRONT_HTML_PATH)

    threading.Thread(target=_open_frontend, daemon=True).start()

    app.run(host="0.0.0.0", port=5001, debug=False)

