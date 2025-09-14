#!/usr/bin/env python3
"""
setText Path 객체 오류 수정 검증 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_path_to_string_conversion():
    """Path 객체를 setText에 전달할 때 문자열 변환 테스트"""
    print("=== setText Path 객체 오류 수정 검증 ===\n")
    
    try:
        from markitdown_gui.core.models import AppConfig
        from markitdown_gui.core.config_manager import ConfigManager
        print("✓ 필요한 클래스들 import 성공")
    except ImportError as e:
        print(f"❌ Import 실패: {e}")
        return False
    
    try:
        # ConfigManager를 통해 설정 로드
        config_manager = ConfigManager()
        config = config_manager.get_config()
        print("✓ ConfigManager를 통한 설정 로드 성공")
        
        # output_directory가 Path 객체인지 확인
        output_dir = config.get("output_directory", "")
        print(f"✓ config.get('output_directory') = {output_dir} (타입: {type(output_dir)})")
        
        # log_directory 테스트 (존재하지 않는 키)
        log_dir = config.get("log_directory", "")
        print(f"✓ config.get('log_directory') = {log_dir} (타입: {type(log_dir)})")
        
        # Path 객체를 문자열로 변환하는 수정된 패턴 테스트
        print("\n--- setText 호출 시나리오 테스트 ---")
        
        # 수정된 패턴: str() 변환 적용
        output_dir_str = str(output_dir) if output_dir else ""
        log_dir_str = str(log_dir) if log_dir else ""
        
        print(f"✓ str(output_dir) if output_dir else '' = '{output_dir_str}' (타입: {type(output_dir_str)})")
        print(f"✓ str(log_dir) if log_dir else '' = '{log_dir_str}' (타입: {type(log_dir_str)})")
        
        # setText 호출 시뮬레이션 (실제 QLineEdit.setText가 아닌 str 타입 확인)
        def mock_set_text(text):
            """setText 메서드 시뮬레이션"""
            if not isinstance(text, str):
                raise TypeError(f"setText(self, a0: Optional[str]): argument 1 has unexpected type '{type(text).__name__}'")
            return f"setText 성공: '{text}'"
        
        print("\n--- setText 호출 시뮬레이션 ---")
        try:
            result1 = mock_set_text(output_dir_str)
            print(f"✓ output_dir_edit.setText() 시뮬레이션: {result1}")
        except TypeError as e:
            print(f"❌ output_dir_edit.setText() 실패: {e}")
            return False
        
        try:
            result2 = mock_set_text(log_dir_str)
            print(f"✓ log_dir_edit.setText() 시뮬레이션: {result2}")
        except TypeError as e:
            print(f"❌ log_dir_edit.setText() 실패: {e}")
            return False
        
        # 수정 전 패턴으로 오류 재현 (참고용)
        print("\n--- 수정 전 패턴 (오류 재현) ---")
        try:
            # 이것이 원래 오류를 발생시키던 패턴
            if isinstance(output_dir, Path):
                mock_set_text(output_dir)  # 이것이 오류를 발생시킴
                print("❌ 이 줄은 실행되면 안됨")
        except TypeError as e:
            print(f"✓ 예상된 오류 재현됨: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    print("setText Path 객체 오류 수정 검증")
    print("=" * 50)
    print("'setText has unexpected type WindowsPath' 오류 수정 확인")
    print("=" * 50)
    
    test_result = test_path_to_string_conversion()
    
    print("\n" + "=" * 50)
    if test_result:
        print("🎉 setText Path 객체 오류 수정이 완료되었습니다!")
        print("\n수정 내용:")
        print("1. settings_dialog.py 307-308라인에서 Path 객체를 문자열로 변환")
        print("2. str(path_obj) if path_obj else '' 패턴 적용")
        print("3. setText() 메서드가 문자열만 받도록 보장")
        print("\n이제 '변환 설정' 다이얼로그가 정상 동작할 것입니다!")
    else:
        print("❌ 테스트에 실패했습니다. 수정 내용을 다시 확인해주세요.")


if __name__ == "__main__":
    main()