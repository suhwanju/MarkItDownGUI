#!/usr/bin/env python3
"""
QFontDatabase 초기화 오류 수정 검증 스크립트
PyQt6에서 QFontDatabase는 더 이상 인스턴스를 생성할 수 없고, static 메서드만 사용해야 함
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_qfontdatabase_api():
    """QFontDatabase API 사용 방법 테스트"""
    print("=== QFontDatabase API 테스트 ===\n")
    
    try:
        from PyQt6.QtGui import QFontDatabase
        from PyQt6.QtWidgets import QApplication
        
        # QApplication이 필요함
        app = QApplication(sys.argv)
        
        print("1. PyQt6에서 QFontDatabase 인스턴스 생성 시도:")
        try:
            # 이것은 PyQt6에서 오류 발생
            font_db = QFontDatabase()
            print("   ❌ QFontDatabase() 인스턴스 생성 성공 (예상치 못한 결과)")
        except TypeError as e:
            print(f"   ✓ QFontDatabase() 인스턴스 생성 실패 (예상된 결과)")
            print(f"   오류 메시지: {e}")
        
        print("\n2. QFontDatabase static 메서드 사용:")
        
        # Static 메서드는 직접 호출 가능
        try:
            families = QFontDatabase.families()
            print(f"   ✓ QFontDatabase.families() 호출 성공")
            print(f"   사용 가능한 폰트 수: {len(families)}")
            if len(families) > 0:
                print(f"   첫 번째 폰트: {families[0]}")
        except Exception as e:
            print(f"   ❌ QFontDatabase.families() 호출 실패: {e}")
            return False
        
        try:
            system_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
            print(f"   ✓ QFontDatabase.systemFont() 호출 성공")
            print(f"   시스템 기본 폰트: {system_font.family()}")
        except Exception as e:
            print(f"   ❌ QFontDatabase.systemFont() 호출 실패: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ PyQt6 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        return False


def test_i18n_manager_fonts():
    """수정된 i18n_manager의 폰트 초기화 테스트"""
    print("\n=== I18nManager 폰트 초기화 테스트 ===\n")
    
    try:
        from PyQt6.QtWidgets import QApplication
        import sys
        
        # QApplication 생성 (필수)
        app = QApplication(sys.argv)
        
        from markitdown_gui.core.i18n_manager import I18nManager
        
        # I18nManager 인스턴스 생성
        i18n_manager = I18nManager()
        print("✓ I18nManager 인스턴스 생성 성공")
        
        # 지원 언어 확인
        for lang_code, lang_info in i18n_manager.supported_languages.items():
            print(f"✓ {lang_code}: 폰트 = {lang_info.default_font_family}")
        
        return True
        
    except Exception as e:
        print(f"❌ I18nManager 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    print("QFontDatabase 초기화 오류 수정 검증")
    print("=" * 50)
    print("ERROR: QFontDatabase(a0: QFontDatabase): not enough arguments")
    print("=" * 50)
    
    # 개별 테스트 실행
    test1 = test_qfontdatabase_api()
    test2 = test_i18n_manager_fonts()
    
    print("\n" + "=" * 50)
    print("전체 테스트 결과:")
    print(f"  - QFontDatabase API 테스트: {'✅ 통과' if test1 else '❌ 실패'}")
    print(f"  - I18nManager 폰트 초기화: {'✅ 통과' if test2 else '❌ 실패'}")
    
    if test1 and test2:
        print("\n🎉 QFontDatabase 오류가 수정되었습니다!")
        print("\n수정 내용:")
        print("1. PyQt6에서 QFontDatabase는 인스턴스를 생성할 수 없음")
        print("2. 모든 메서드가 static 메서드로 변경됨")
        print("3. font_db = QFontDatabase() → 제거")
        print("4. font_db.families() → QFontDatabase.families()")
        print("5. font_db.systemFont() → QFontDatabase.systemFont()")
        print("\n이제 프로그램 시작시 QFontDatabase 오류가 발생하지 않습니다!")
    else:
        print("\n❌ 일부 테스트에 실패했습니다.")
        print("수정 내용을 다시 확인해주세요.")


if __name__ == "__main__":
    main()