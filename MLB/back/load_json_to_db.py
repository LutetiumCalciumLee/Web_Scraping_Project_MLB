#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON 파일들을 SQLite 데이터베이스에 저장하는 독립 실행 스크립트
"""

import json
import os
import sqlite3
import glob
from datetime import datetime


# 스크립트가 있는 디렉토리를 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fangraphs_data.db")


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
    print(f"✓ 데이터베이스 초기화 완료: {DB_PATH}")


def save_json_to_db(json_file_path: str):
    """JSON 파일을 읽어서 데이터베이스에 저장"""
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
            print(f"⚠ 경고: JSON 파일이 배열 형식이 아닙니다: {json_file_path}")
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
                print(f"✗ 선수 데이터 저장 실패: {player.get('Name', 'Unknown')} - {str(e)}")
                skipped_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"  ✓ {os.path.basename(json_file_path)}: 저장 {saved_count}개, 건너뜀 {skipped_count}개")
        return True
        
    except Exception as e:
        print(f"✗ JSON 파일 저장 실패: {json_file_path} - {str(e)}")
        return False


def load_all_json_to_db():
    """모든 JSON 파일을 찾아서 데이터베이스에 저장"""
    print("=" * 60)
    print("JSON 파일을 SQLite 데이터베이스에 저장하는 중...")
    print("=" * 60)
    
    init_database()
    
    # 모든 fangraphs_data_* 디렉토리 찾기
    pattern = os.path.join(BASE_DIR, "fangraphs_data_*", "*.json")
    json_files = glob.glob(pattern)
    
    if not json_files:
        print("⚠ 경고: 저장할 JSON 파일을 찾을 수 없습니다.")
        print(f"   검색 경로: {pattern}")
        return
    
    # 파일 정렬 (날짜순, 인덱스순)
    json_files.sort()
    
    print(f"\n총 {len(json_files)}개의 JSON 파일을 찾았습니다.\n")
    
    processed = 0
    failed = 0
    
    for i, json_file in enumerate(json_files, 1):
        print(f"[{i}/{len(json_files)}] 처리 중: {os.path.basename(json_file)}")
        if save_json_to_db(json_file):
            processed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("처리 완료!")
    print(f"  성공: {processed}개")
    print(f"  실패: {failed}개")
    print(f"  총계: {len(json_files)}개")
    print(f"\n데이터베이스 위치: {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        load_all_json_to_db()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

