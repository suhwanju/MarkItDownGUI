#!/usr/bin/env python3
"""
i18n 시스템 테스트 스크립트
"""

import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import QApplication
from markitdown_gui.core.i18n_manager import init_i18n, tr, set_language, get_current_language


def test_i18n_system():
    """i18n 시스템 테스트"""
    
    # Qt 애플리케이션 생성 (i18n 매니저 초기화에 필요)
    app = QApplication(sys.argv)
    
    print("=== MarkItDown GUI i18n System Test ===\n")
    
    # i18n 시스템 초기화
    i18n_manager = init_i18n(app)
    
    if not i18n_manager:
        print("❌ Failed to initialize i18n manager")
        return False
    
    print(f"✅ i18n Manager initialized")
    
    # 지원되는 언어 확인
    supported_langs = i18n_manager.get_supported_languages()
    print(f"📝 Supported languages: {list(supported_langs.keys())}")
    
    # 기본 언어 확인
    current_lang = get_current_language()
    print(f"🌍 Current language: {current_lang}")
    
    # 번역 테스트
    print("\n--- Translation Tests ---")
    
    # 현재 언어로 번역 테스트
    window_title = tr("title", "window")
    app_name = tr("name", "app")
    ready_status = tr("ready", "window")
    
    print(f"Window title: '{window_title}'")
    print(f"App name: '{app_name}'")
    print(f"Ready status: '{ready_status}'")
    
    # 언어 변경 테스트
    print("\n--- Language Change Tests ---")
    
    # 영어로 변경
    if current_lang != "en_US":
        print("Changing to English (en_US)...")
        success = set_language("en_US")
        if success:
            print("✅ Changed to English")
            window_title_en = tr("title", "window")
            app_name_en = tr("name", "app")
            print(f"Window title (EN): '{window_title_en}'")
            print(f"App name (EN): '{app_name_en}'")
        else:
            print("❌ Failed to change to English")
    
    # 한국어로 변경
    print("\nChanging to Korean (ko_KR)...")
    success = set_language("ko_KR")
    if success:
        print("✅ Changed to Korean")
        window_title_ko = tr("title", "window")
        app_name_ko = tr("name", "app")
        print(f"Window title (KO): '{window_title_ko}'")
        print(f"App name (KO): '{app_name_ko}'")
    else:
        print("❌ Failed to change to Korean")
    
    # 폰트 테스트
    print("\n--- Font Tests ---")
    
    for lang_code, lang_info in supported_langs.items():
        font = i18n_manager.get_font_for_language(lang_code, 12)
        print(f"{lang_code}: {font.family()}, {font.pointSize()}pt")
    
    # 로케일 형식 테스트
    print("\n--- Locale Format Tests ---")
    
    # 숫자 형식
    number = 1234.567
    formatted_number = i18n_manager.format_number(number, 2)
    print(f"Number format: {number} → '{formatted_number}'")
    
    # 통화 형식
    amount = 1234.56
    formatted_currency = i18n_manager.format_currency(amount, "USD")
    print(f"Currency format: ${amount} → '{formatted_currency}'")
    
    # 날짜/시간 형식 테스트
    from PyQt6.QtCore import QDate, QTime
    today = QDate.currentDate()
    now = QTime.currentTime()
    
    date_short = i18n_manager.format_date(today, "short")
    date_long = i18n_manager.format_date(today, "long")
    time_short = i18n_manager.format_time(now, "short")
    
    print(f"Date (short): '{date_short}'")
    print(f"Date (long): '{date_long}'")
    print(f"Time (short): '{time_short}'")
    
    # 플레이스홀더 테스트
    print("\n--- Placeholder Tests ---")
    
    files_count = tr("count_label", "files", 5)
    selected_count = tr("selected_count_label", "files", 3)
    
    print(f"Files count: '{files_count}'")
    print(f"Selected count: '{selected_count}'")
    
    # 누락된 키 테스트
    print("\n--- Missing Key Tests ---")
    missing_key = tr("nonexistent_key", "nonexistent.context")
    print(f"Missing key result: '{missing_key}'")
    
    print("\n=== Test Completed Successfully ===")
    return True


if __name__ == "__main__":
    try:
        success = test_i18n_system()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)