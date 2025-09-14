#!/usr/bin/env python3
"""
AppConfig get 메서드 수정 검증 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_appconfig_get_method():
    """AppConfig get 메서드 테스트"""
    print("=== AppConfig get 메서드 테스트 시작 ===\n")
    
    try:
        from markitdown_gui.core.models import AppConfig, FileConflictConfig
        print("✓ AppConfig 클래스 import 성공")
    except ImportError as e:
        print(f"❌ AppConfig import 실패: {e}")
        return False
    
    try:
        # AppConfig 인스턴스 생성
        config = AppConfig()
        print("✓ AppConfig 인스턴스 생성 성공")
        
        # get 메서드 테스트
        print("\n--- get 메서드 테스트 ---")
        
        # 존재하는 속성 테스트
        language = config.get("language", "en")
        print(f"✓ config.get('language', 'en') = {language}")
        
        theme = config.get("theme", "dark")
        print(f"✓ config.get('theme', 'dark') = {theme}")
        
        output_dir = config.get("output_directory", Path("default"))
        print(f"✓ config.get('output_directory', Path('default')) = {output_dir}")
        
        # 존재하지 않는 속성 테스트 (기본값 반환)
        nonexistent = config.get("nonexistent_key", "default_value")
        print(f"✓ config.get('nonexistent_key', 'default_value') = {nonexistent}")
        
        # None 기본값 테스트
        none_test = config.get("another_nonexistent")
        print(f"✓ config.get('another_nonexistent') = {none_test}")
        
        print("\n--- 딕셔너리 스타일 접근 테스트 ---")
        
        # __getitem__ 테스트
        try:
            language_bracket = config["language"]
            print(f"✓ config['language'] = {language_bracket}")
        except KeyError as e:
            print(f"❌ config['language'] 실패: {e}")
            return False
        
        # __setitem__ 테스트
        try:
            config["language"] = "en"
            print(f"✓ config['language'] = 'en' 설정 성공")
            print(f"  확인: config.language = {config.language}")
        except KeyError as e:
            print(f"❌ config['language'] = 'en' 실패: {e}")
            return False
        
        # __contains__ 테스트
        if "language" in config:
            print("✓ 'language' in config = True")
        else:
            print("❌ 'language' in config = False")
            return False
        
        if "nonexistent" not in config:
            print("✓ 'nonexistent' not in config = True")
        else:
            print("❌ 'nonexistent' not in config = False")
            return False
        
        print("\n--- 딕셔너리 스타일 메서드 테스트 ---")
        
        # keys() 테스트
        keys_list = list(config.keys())
        print(f"✓ config.keys() 개수: {len(keys_list)}")
        print(f"  주요 키들: {list(keys_list)[:5]}...")
        
        # items() 테스트
        items_count = 0
        for key, value in config.items():
            items_count += 1
            if items_count <= 3:  # 처음 3개만 출력
                print(f"  {key}: {value}")
        print(f"✓ config.items() 총 {items_count}개 항목")
        
        # values() 테스트
        values_count = sum(1 for _ in config.values())
        print(f"✓ config.values() 총 {values_count}개 값")
        
        print("\n--- 실제 설정 값 테스트 ---")
        
        # 실제 설정 다이얼로그에서 사용되는 값들 테스트
        test_keys = [
            "output_directory",
            "log_directory", 
            "theme",
            "font_size",
            "auto_save",
            "remember_window",
            "restore_session",
            "check_updates"
        ]
        
        for key in test_keys:
            try:
                value = config.get(key, f"default_for_{key}")
                print(f"✓ config.get('{key}') = {value}")
            except Exception as e:
                print(f"❌ config.get('{key}') 실패: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ AppConfig 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_manager_integration():
    """ConfigManager와의 통합 테스트"""
    print("\n=== ConfigManager 통합 테스트 ===\n")
    
    try:
        from markitdown_gui.core.config_manager import ConfigManager
        print("✓ ConfigManager import 성공")
        
        # ConfigManager 인스턴스 생성
        config_manager = ConfigManager()
        print("✓ ConfigManager 인스턴스 생성 성공")
        
        # 설정 로드
        config = config_manager.get_config()
        print("✓ config_manager.get_config() 성공")
        
        # get 메서드 테스트
        language = config.get("language", "default_lang")
        print(f"✓ 로드된 설정에서 config.get('language') = {language}")
        
        theme = config.get("theme", "default_theme")
        print(f"✓ 로드된 설정에서 config.get('theme') = {theme}")
        
        # 존재하지 않는 키 테스트
        unknown = config.get("unknown_key", "fallback_value")
        print(f"✓ config.get('unknown_key', 'fallback_value') = {unknown}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings_dialog_compatibility():
    """설정 다이얼로그 호환성 시뮬레이션 테스트"""
    print("\n=== 설정 다이얼로그 호환성 테스트 ===\n")
    
    try:
        from markitdown_gui.core.models import AppConfig
        
        config = AppConfig()
        print("✓ AppConfig 인스턴스 생성")
        
        # 설정 다이얼로그에서 사용하는 패턴 시뮬레이션
        settings_patterns = [
            ('output_directory', ''),
            ('log_directory', ''),
            ('theme', 'follow_system'),
            ('font_size', 10),
            ('auto_save', True),
            ('remember_window', True),
            ('restore_session', False),
            ('check_updates', True)
        ]
        
        print("설정 다이얼로그 호환성 테스트:")
        for key, default_value in settings_patterns:
            try:
                result = config.get(key, default_value)
                print(f"✓ config.get('{key}', {default_value}) = {result}")
            except Exception as e:
                print(f"❌ config.get('{key}', {default_value}) 실패: {e}")
                return False
        
        # 변환 설정 호환성 테스트
        print("\n변환 설정 섹션 테스트:")
        conversion_patterns = [
            ('max_concurrent_conversions', 4),
            ('include_subdirectories', True),
            ('save_to_original_directory', True),
            ('max_file_size_mb', 100)
        ]
        
        for key, default_value in conversion_patterns:
            try:
                result = config.get(key, default_value)
                print(f"✓ config.get('{key}', {default_value}) = {result}")
            except Exception as e:
                print(f"❌ config.get('{key}', {default_value}) 실패: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 다이얼로그 호환성 테스트 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("AppConfig get 메서드 수정 검증")
    print("=" * 50)
    print("변환 설정 버튼 오류 수정을 위한 AppConfig.get() 메서드 구현 검증")
    print("=" * 50)
    
    # 개별 테스트 실행
    test1 = test_appconfig_get_method()
    test2 = test_config_manager_integration()
    test3 = test_settings_dialog_compatibility()
    
    print("\n" + "=" * 50)
    print("전체 테스트 결과:")
    print(f"  - AppConfig get 메서드: {'✅ 통과' if test1 else '❌ 실패'}")
    print(f"  - ConfigManager 통합: {'✅ 통과' if test2 else '❌ 실패'}")
    print(f"  - 설정 다이얼로그 호환성: {'✅ 통과' if test3 else '❌ 실패'}")
    
    if test1 and test2 and test3:
        print("\n🎉 모든 테스트가 통과했습니다!")
        print("\n수정 내용 요약:")
        print("1. AppConfig 클래스에 get(key, default=None) 메서드 추가")
        print("2. 딕셔너리 스타일 접근을 위한 매직 메서드들 구현:")
        print("   - __getitem__, __setitem__, __contains__")
        print("   - keys(), items(), values() 메서드")
        print("3. 설정 다이얼로그에서 config.get() 호출이 정상 작동")
        print("4. 기존 dataclass 속성 접근 방식도 그대로 유지")
        print("\n이제 '변환 설정' 버튼이 정상 작동할 것입니다!")
    else:
        print("\n❌ 일부 테스트에 실패했습니다.")
        print("AppConfig 클래스의 get 메서드 구현을 다시 확인해주세요.")


if __name__ == "__main__":
    main()