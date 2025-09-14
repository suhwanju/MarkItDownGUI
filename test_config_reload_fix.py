#!/usr/bin/env python3
"""
ConfigManager reload_config 메서드 오류 수정 검증 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_manager_methods():
    """ConfigManager 메서드 존재 여부 및 정상 동작 테스트"""
    print("=== ConfigManager reload_config 메서드 오류 수정 검증 ===\n")
    
    try:
        from markitdown_gui.core.config_manager import ConfigManager
        print("✓ ConfigManager import 성공")
    except ImportError as e:
        print(f"❌ ConfigManager import 실패: {e}")
        return False
    
    try:
        # ConfigManager 인스턴스 생성
        config_manager = ConfigManager()
        print("✓ ConfigManager 인스턴스 생성 성공")
        
        # 사용 가능한 메서드 확인
        print("\n--- ConfigManager 메서드 목록 확인 ---")
        available_methods = [method for method in dir(config_manager) if not method.startswith('_')]
        important_methods = ['load_config', 'save_config', 'get_config', 'update_config']
        
        for method in important_methods:
            if hasattr(config_manager, method):
                print(f"✓ {method} 메서드 존재")
            else:
                print(f"❌ {method} 메서드 없음")
                return False
        
        # reload_config 메서드 존재 여부 확인
        if hasattr(config_manager, 'reload_config'):
            print("⚠️  reload_config 메서드가 여전히 존재함 (사용하면 안됨)")
        else:
            print("✓ reload_config 메서드 없음 (예상대로)")
        
        # load_config 메서드 정상 동작 테스트
        print("\n--- load_config 메서드 동작 테스트 ---")
        try:
            original_config = config_manager.get_config()
            print(f"✓ 현재 설정 로드됨: 언어={original_config.language}, 테마={original_config.theme}")
            
            # load_config 호출 (reload_config 대신 사용할 메서드)
            reloaded_config = config_manager.load_config()
            print("✓ load_config() 호출 성공")
            
            # 반환값이 AppConfig 인스턴스인지 확인
            from markitdown_gui.core.models import AppConfig
            if isinstance(reloaded_config, AppConfig):
                print("✓ load_config()가 AppConfig 인스턴스 반환")
            else:
                print(f"❌ load_config()가 잘못된 타입 반환: {type(reloaded_config)}")
                return False
            
            print(f"✓ 재로드된 설정: 언어={reloaded_config.language}, 테마={reloaded_config.theme}")
            
        except Exception as e:
            print(f"❌ load_config() 호출 실패: {e}")
            return False
        
        # 실제 사용 시나리오 시뮬레이션
        print("\n--- 실제 사용 시나리오 시뮬레이션 ---")
        try:
            # 설정 변경 시뮬레이션
            config_manager.update_config(theme="dark")
            print("✓ update_config() 호출 성공")
            
            # 설정 저장 시뮬레이션
            save_result = config_manager.save_config()
            print(f"✓ save_config() 호출 성공: {save_result}")
            
            # 설정 재로드 시뮬레이션 (원래 reload_config() 대신 load_config() 사용)
            reloaded_config = config_manager.load_config()
            print("✓ load_config()로 설정 재로드 성공")
            
            print(f"✓ 시나리오 완료: 최종 테마={reloaded_config.theme}")
            
        except Exception as e:
            print(f"❌ 사용 시나리오 실패: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window_integration():
    """main_window.py의 수정된 코드 검증"""
    print("\n=== main_window.py 수정 내용 검증 ===\n")
    
    try:
        # main_window.py 파일에서 reload_config 호출이 없는지 확인
        main_window_path = Path("markitdown_gui/ui/main_window.py")
        if not main_window_path.exists():
            print("❌ main_window.py 파일을 찾을 수 없음")
            return False
        
        with open(main_window_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'reload_config()' in content:
            print("❌ main_window.py에 reload_config() 호출이 여전히 남아있음")
            return False
        else:
            print("✓ main_window.py에서 reload_config() 호출 제거됨")
        
        if 'load_config()' in content:
            print("✓ main_window.py에서 load_config() 호출로 변경됨")
        else:
            print("⚠️  main_window.py에서 load_config() 호출을 찾을 수 없음")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ main_window.py 검증 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("ConfigManager reload_config 메서드 오류 수정 검증")
    print("=" * 60)
    print("ERROR: 'ConfigManager' object has no attribute 'reload_config'")
    print("=" * 60)
    
    # 개별 테스트 실행
    test1 = test_config_manager_methods()
    test2 = test_main_window_integration()
    
    print("\n" + "=" * 60)
    print("전체 테스트 결과:")
    print(f"  - ConfigManager 메서드 테스트: {'✅ 통과' if test1 else '❌ 실패'}")
    print(f"  - main_window.py 수정 검증: {'✅ 통과' if test2 else '❌ 실패'}")
    
    if test1 and test2:
        print("\n🎉 ConfigManager reload_config 오류가 수정되었습니다!")
        print("\n수정 내용 요약:")
        print("1. main_window.py에서 reload_config() 호출을 load_config()로 변경")
        print("2. ConfigManager.load_config()는 정상적으로 동작하는 기존 메서드")
        print("3. 설정 다이얼로그 저장 후 설정 재로드가 정상 작동")
        print("\n이제 '변환 설정' 저장이 오류 없이 동작할 것입니다!")
    else:
        print("\n❌ 일부 테스트에 실패했습니다.")
        print("수정 내용을 다시 확인해주세요.")


if __name__ == "__main__":
    main()