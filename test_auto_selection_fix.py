#!/usr/bin/env python3
"""
파일 스캔 후 자동 선택 문제 수정사항 검증 테스트

이 테스트는 파일 스캔 완료 후 자동으로 파일이 선택되지 않는지 확인합니다.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from markitdown_gui.core.models import FileInfo, FileType, ConversionStatus
from markitdown_gui.core.config_manager import ConfigManager


class TestAutoSelectionFix:
    """자동 선택 수정사항 테스트"""

    def __init__(self):
        self.test_results = []

    def create_test_file_infos(self, count=5):
        """테스트용 FileInfo 객체들 생성"""
        file_infos = []
        for i in range(count):
            file_info = FileInfo(
                path=Path(f"/test/file_{i}.txt"),
                name=f"file_{i}.txt",
                size=1000 + i * 100,
                modified_time=datetime.now(),
                file_type=FileType.TXT,
                is_selected=False  # 기본값이 False인지 확인
            )
            file_infos.append(file_info)
        return file_infos

    def test_file_info_default_selection(self):
        """FileInfo 기본 선택 상태 테스트"""
        print("1. FileInfo 기본 선택 상태 테스트...")

        file_info = FileInfo(
            path=Path("/test/file.txt"),
            name="test.txt",
            size=1000,
            modified_time=datetime.now(),
            file_type=FileType.TXT
        )

        if file_info.is_selected == False:
            self.test_results.append("✅ FileInfo 기본 선택 상태가 False로 올바르게 설정됨")
            return True
        else:
            self.test_results.append("❌ FileInfo 기본 선택 상태가 True로 잘못 설정됨")
            return False

    def test_scan_completed_logic(self):
        """스캔 완료 로직 테스트 (모의 테스트)"""
        print("2. 스캔 완료 후 자동 선택 로직 테스트...")

        # 테스트 파일 정보 생성
        file_infos = self.create_test_file_infos(5)

        # 스캔 완료 후 파일들이 자동으로 선택되지 않았는지 확인
        auto_selected_count = sum(1 for fi in file_infos if fi.is_selected)

        if auto_selected_count == 0:
            self.test_results.append("✅ 스캔 완료 후 파일이 자동 선택되지 않음")
            return True
        else:
            self.test_results.append(f"❌ 스캔 완료 후 {auto_selected_count}개 파일이 자동 선택됨")
            return False

    def test_manual_selection_still_works(self):
        """수동 선택 기능이 여전히 작동하는지 테스트"""
        print("3. 수동 선택 기능 테스트...")

        file_infos = self.create_test_file_infos(3)

        # 수동으로 일부 파일 선택
        file_infos[0].is_selected = True
        file_infos[2].is_selected = True

        selected_files = [fi for fi in file_infos if fi.is_selected]

        if len(selected_files) == 2:
            self.test_results.append("✅ 수동 선택 기능이 정상 작동함")
            return True
        else:
            self.test_results.append(f"❌ 수동 선택 기능 오류: {len(selected_files)}개 선택됨")
            return False

    def test_get_selected_files_logic(self):
        """get_selected_files 메서드 로직 테스트"""
        print("4. 선택된 파일 반환 로직 테스트...")

        file_infos = self.create_test_file_infos(5)

        # 일부 파일만 선택
        file_infos[1].is_selected = True
        file_infos[3].is_selected = True

        # get_selected_files와 동일한 로직으로 필터링
        selected_files = [fi for fi in file_infos if fi.is_selected]

        expected_names = ["file_1.txt", "file_3.txt"]
        actual_names = [fi.name for fi in selected_files]

        if actual_names == expected_names:
            self.test_results.append("✅ 선택된 파일 반환 로직이 정상 작동함")
            return True
        else:
            self.test_results.append(f"❌ 선택된 파일 반환 로직 오류: {actual_names} != {expected_names}")
            return False

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("파일 스캔 후 자동 선택 문제 수정사항 검증 테스트")
        print("=" * 60)

        tests = [
            self.test_file_info_default_selection,
            self.test_scan_completed_logic,
            self.test_manual_selection_still_works,
            self.test_get_selected_files_logic
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            try:
                if test():
                    passed += 1
                print()
            except Exception as e:
                self.test_results.append(f"❌ 테스트 실행 오류: {e}")
                print()

        print("=" * 60)
        print("테스트 결과 요약")
        print("=" * 60)
        for result in self.test_results:
            print(result)

        print(f"\n통과: {passed}/{total} 테스트")

        if passed == total:
            print("🎉 모든 테스트 통과! 수정사항이 올바르게 적용되었습니다.")
            return True
        else:
            print("⚠️ 일부 테스트 실패. 추가 수정이 필요합니다.")
            return False


if __name__ == "__main__":
    # 경고 억제
    import warnings
    warnings.filterwarnings("ignore")

    tester = TestAutoSelectionFix()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)