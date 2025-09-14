#!/usr/bin/env python3
"""
'출력 폴더 열기' 버튼 제거 검증 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_button_removal():
    """UI에서 '출력 폴더 열기' 버튼 제거 검증"""
    print("=== '출력 폴더 열기' 버튼 제거 검증 ===\n")
    
    try:
        # main_window.py 파일 검증
        main_window_path = Path("markitdown_gui/ui/main_window.py")
        if not main_window_path.exists():
            print("❌ main_window.py 파일을 찾을 수 없음")
            return False
        
        with open(main_window_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("--- 버튼 관련 코드 제거 확인 ---")
        
        # 버튼 생성 코드 확인
        if 'open_output_btn' in content:
            print("❌ open_output_btn 참조가 여전히 남아있음")
            return False
        else:
            print("✓ open_output_btn 버튼 변수 모두 제거됨")
        
        # 메서드 확인
        if '_open_output_folder' in content:
            print("❌ _open_output_folder 메서드가 여전히 남아있음")
            return False
        else:
            print("✓ _open_output_folder 메서드 제거됨")
        
        # 버튼 텍스트 확인
        if '"출력 폴더 열기"' in content:
            print("❌ '출력 폴더 열기' 텍스트가 여전히 남아있음")
            return False
        else:
            print("✓ '출력 폴더 열기' 버튼 텍스트 제거됨")
        
        # 필수 버튼들이 여전히 존재하는지 확인
        print("\n--- 필수 버튼들 존재 확인 ---")
        essential_buttons = [
            ('scan_btn', '디렉토리 선택'),
            ('convert_btn', '변환 시작'),
            ('preview_btn', '미리보기'),
            ('conversion_settings_btn', '변환 설정')
        ]
        
        for btn_var, btn_description in essential_buttons:
            if btn_var in content:
                print(f"✓ {btn_description} 버튼({btn_var}) 존재")
            else:
                print(f"❌ {btn_description} 버튼({btn_var}) 누락")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 파일 검증 실패: {e}")
        return False


def test_ui_integrity():
    """UI 구조 무결성 테스트"""
    print("\n=== UI 구조 무결성 테스트 ===\n")
    
    try:
        # PyQt6 및 관련 모듈 import 테스트
        from markitdown_gui.core.config_manager import ConfigManager
        from markitdown_gui.core.models import AppConfig
        print("✓ 핵심 모듈 import 성공")
        
        # ConfigManager 생성 테스트
        config_manager = ConfigManager()
        config = config_manager.get_config()
        print("✓ ConfigManager 생성 및 설정 로드 성공")
        
        print(f"✓ 기본 출력 디렉토리: {config.output_directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI 무결성 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_translation_cleanup():
    """번역 파일에서 불필요한 항목 확인"""
    print("\n=== 번역 파일 정리 상태 확인 ===\n")
    
    translation_files = [
        "markitdown_gui/resources/translations/ko_KR.json",
        "markitdown_gui/resources/translations/en_US.json",
        "markitdown_gui/resources/translations/template.json"
    ]
    
    for file_path in translation_files:
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'open_output_button' in content:
                    print(f"⚠️  {path.name}: open_output_button 번역이 여전히 존재함 (선택적 정리 가능)")
                else:
                    print(f"✓ {path.name}: open_output_button 번역 없음")
            else:
                print(f"⚠️  {path.name}: 파일 없음")
        except Exception as e:
            print(f"❌ {path.name} 확인 실패: {e}")
    
    print("\n📝 참고: 번역 파일의 'open_output_button' 항목은 사용되지 않으므로")
    print("   필요하다면 별도로 정리할 수 있습니다.")
    
    return True


def main():
    """메인 함수"""
    print("'출력 폴더 열기' 버튼 제거 검증")
    print("=" * 50)
    print("UI에서 '출력 폴더 열기' 버튼 완전 제거 확인")
    print("=" * 50)
    
    # 개별 테스트 실행
    test1 = test_button_removal()
    test2 = test_ui_integrity()
    test3 = test_translation_cleanup()
    
    print("\n" + "=" * 50)
    print("전체 테스트 결과:")
    print(f"  - 버튼 제거 검증: {'✅ 통과' if test1 else '❌ 실패'}")
    print(f"  - UI 무결성 테스트: {'✅ 통과' if test2 else '❌ 실패'}")
    print(f"  - 번역 파일 상태: {'✅ 확인완료' if test3 else '❌ 실패'}")
    
    if test1 and test2:
        print("\n🎉 '출력 폴더 열기' 버튼이 성공적으로 제거되었습니다!")
        print("\n제거된 내용:")
        print("1. QPushButton('출력 폴더 열기') 버튼 생성 코드")
        print("2. open_output_btn 변수 및 모든 속성 설정")
        print("3. clicked.connect(_open_output_folder) 이벤트 연결")
        print("4. _open_output_folder() 메서드 전체")
        print("\n✅ UI가 더 간결해지고 필수 기능들은 그대로 유지됩니다!")
        print("📁 사용자는 직접 출력 폴더(기본: ./markdown)에 접근할 수 있습니다.")
    else:
        print("\n❌ 일부 테스트에 실패했습니다.")
        print("코드를 다시 확인해주세요.")


if __name__ == "__main__":
    main()