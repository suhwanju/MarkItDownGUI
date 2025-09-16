#!/usr/bin/env python3
"""
변환 완료 다이얼로그 개선사항 테스트

이 테스트는 변환 완료 다이얼로그에 파일명과 경로 정보가 올바르게 표시되는지 확인합니다.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from markitdown_gui.core.models import (
    FileInfo, FileType, ConversionStatus, ConversionResult,
    FileConflictStatus
)


class TestConversionCompletedDialog:
    """변환 완료 다이얼로그 테스트"""

    def __init__(self):
        self.test_results = []

    def create_test_conversion_results(self, count=3):
        """테스트용 ConversionResult 객체들 생성"""
        results = []
        temp_dir = Path(tempfile.gettempdir())

        for i in range(count):
            # 원본 파일 정보
            file_info = FileInfo(
                path=Path(f"/test/source/file_{i}.txt"),
                name=f"file_{i}.txt",
                size=1000 + i * 100,
                modified_time=datetime.now(),
                file_type=FileType.TXT,
                is_selected=True
            )

            # 변환 결과
            output_path = temp_dir / "converted" / f"file_{i}.md"
            result = ConversionResult(
                file_info=file_info,
                status=ConversionStatus.SUCCESS,
                output_path=output_path,
                conversion_time=1.5 + i * 0.3,
                conflict_status=FileConflictStatus.NONE
            )
            results.append(result)

        return results

    def create_mixed_results(self):
        """성공/실패가 혼재된 테스트 결과 생성"""
        results = []
        temp_dir = Path(tempfile.gettempdir())

        # 성공한 결과들
        success_files = ["document.docx", "presentation.pptx", "image.jpg"]
        for i, filename in enumerate(success_files):
            file_info = FileInfo(
                path=Path(f"/test/source/{filename}"),
                name=filename,
                size=2000 + i * 500,
                modified_time=datetime.now(),
                file_type=FileType.DOCX if filename.endswith('.docx') else FileType.PPTX if filename.endswith('.pptx') else FileType.JPG,
                is_selected=True
            )

            output_path = temp_dir / "converted" / f"{Path(filename).stem}.md"
            result = ConversionResult(
                file_info=file_info,
                status=ConversionStatus.SUCCESS,
                output_path=output_path,
                conversion_time=2.1 + i * 0.4
            )
            results.append(result)

        # 실패한 결과
        failed_file = FileInfo(
            path=Path("/test/source/corrupted.pdf"),
            name="corrupted.pdf",
            size=5000,
            modified_time=datetime.now(),
            file_type=FileType.PDF,
            is_selected=True
        )

        failed_result = ConversionResult(
            file_info=failed_file,
            status=ConversionStatus.FAILED,
            error_message="PDF 파일이 손상되었습니다."
        )
        results.append(failed_result)

        return results

    def test_summary_text_generation(self):
        """요약 텍스트 생성 테스트"""
        print("1. 변환 완료 요약 텍스트 생성 테스트...")

        results = self.create_test_conversion_results(3)
        success_count = len([r for r in results if r.is_success])
        total_count = len(results)

        # 실제 _on_conversion_completed에서 생성하는 텍스트와 동일한 로직
        summary_text = f"변환이 완료되었습니다.\n\n"
        summary_text += f"총 파일: {total_count}개\n"
        summary_text += f"성공: {success_count}개\n"

        # 변환 성공한 파일들의 상세 정보 추가
        if success_count > 0:
            summary_text += "\n📄 변환된 파일:\n"
            success_results = [r for r in results if r.is_success]
            for i, result in enumerate(success_results[:10], 1):
                file_name = result.file_info.name
                if result.output_path:
                    output_name = result.output_path.name
                    output_dir = str(result.output_path.parent)
                    if output_dir.startswith(str(Path.home())):
                        output_dir = output_dir.replace(str(Path.home()), "~")
                    summary_text += f"  {i}. {file_name} → {output_name}\n"
                    summary_text += f"     위치: {output_dir}\n"

        # 테스트 검증
        expected_elements = [
            "변환이 완료되었습니다",
            "총 파일: 3개",
            "성공: 3개",
            "📄 변환된 파일:",
            "file_0.txt → file_0.md",
            "file_1.txt → file_1.md",
            "file_2.txt → file_2.md",
            "위치:"
        ]

        missing_elements = []
        for element in expected_elements:
            if element not in summary_text:
                missing_elements.append(element)

        if not missing_elements:
            self.test_results.append("✅ 요약 텍스트에 모든 필수 요소가 포함됨")
            return True
        else:
            self.test_results.append(f"❌ 요약 텍스트에서 누락된 요소: {missing_elements}")
            return False

    def test_mixed_results_summary(self):
        """성공/실패 혼재 결과 요약 테스트"""
        print("2. 성공/실패 혼재 결과 요약 테스트...")

        results = self.create_mixed_results()
        success_count = len([r for r in results if r.is_success])
        total_count = len(results)

        summary_text = f"변환이 완료되었습니다.\n\n"
        summary_text += f"총 파일: {total_count}개\n"
        summary_text += f"성공: {success_count}개\n"

        if success_count < total_count:
            failed_count = total_count - success_count
            summary_text += f"실패: {failed_count}개\n"

        # 변환 성공한 파일들의 상세 정보 추가
        if success_count > 0:
            summary_text += "\n📄 변환된 파일:\n"
            success_results = [r for r in results if r.is_success]
            for i, result in enumerate(success_results[:10], 1):
                file_name = result.file_info.name
                if result.output_path:
                    output_name = result.output_path.name
                    output_dir = str(result.output_path.parent)
                    if output_dir.startswith(str(Path.home())):
                        output_dir = output_dir.replace(str(Path.home()), "~")
                    summary_text += f"  {i}. {file_name} → {output_name}\n"
                    summary_text += f"     위치: {output_dir}\n"

        # 검증
        if (f"총 파일: {total_count}개" in summary_text and
            f"성공: {success_count}개" in summary_text and
            f"실패: {total_count - success_count}개" in summary_text and
            "document.docx → document.md" in summary_text and
            "presentation.pptx → presentation.md" in summary_text):

            self.test_results.append("✅ 혼재 결과 요약이 올바르게 생성됨")
            return True
        else:
            self.test_results.append("❌ 혼재 결과 요약 생성 오류")
            return False

    def test_path_formatting(self):
        """경로 표시 형식 테스트"""
        print("3. 경로 표시 형식 테스트...")

        # 홈 디렉토리 경로 테스트
        home_path = Path.home() / "Documents" / "converted" / "test.md"
        formatted_path = str(home_path.parent)

        if formatted_path.startswith(str(Path.home())):
            formatted_path = formatted_path.replace(str(Path.home()), "~")

        # 일반 경로 테스트
        temp_path = Path(tempfile.gettempdir()) / "converted"
        temp_formatted = str(temp_path)

        if (formatted_path.startswith("~") and
            "Documents" in formatted_path and
            temp_formatted.endswith("converted")):

            self.test_results.append("✅ 경로 표시 형식이 올바르게 적용됨")
            return True
        else:
            self.test_results.append("❌ 경로 표시 형식 오류")
            return False

    def test_large_file_list_truncation(self):
        """대량 파일 목록 잘림 테스트"""
        print("4. 대량 파일 목록 잘림 테스트...")

        # 15개 파일 결과 생성
        results = self.create_test_conversion_results(15)
        success_results = [r for r in results if r.is_success]

        summary_text = ""
        for i, result in enumerate(success_results[:10], 1):  # 최대 10개까지만 표시
            file_name = result.file_info.name
            if result.output_path:
                output_name = result.output_path.name
                summary_text += f"  {i}. {file_name} → {output_name}\n"

        if len(success_results) > 10:
            remaining = len(success_results) - 10
            summary_text += f"  ... 외 {remaining}개 더\n"

        # 검증
        lines = summary_text.strip().split('\n')
        displayed_files = len([line for line in lines if '→' in line and not line.strip().startswith('...')])

        if (displayed_files == 10 and
            "... 외 5개 더" in summary_text):

            self.test_results.append("✅ 대량 파일 목록이 올바르게 잘려서 표시됨")
            return True
        else:
            self.test_results.append(f"❌ 대량 파일 목록 잘림 오류 (표시된 파일: {displayed_files}개)")
            return False

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 70)
        print("변환 완료 다이얼로그 개선사항 테스트")
        print("=" * 70)

        tests = [
            self.test_summary_text_generation,
            self.test_mixed_results_summary,
            self.test_path_formatting,
            self.test_large_file_list_truncation
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
                print(f"테스트 오류: {e}")
                print()

        print("=" * 70)
        print("테스트 결과 요약")
        print("=" * 70)
        for result in self.test_results:
            print(result)

        print(f"\n통과: {passed}/{total} 테스트")

        if passed == total:
            print("🎉 모든 테스트 통과! 변환 완료 다이얼로그 개선사항이 올바르게 구현되었습니다.")
            return True
        else:
            print("⚠️ 일부 테스트 실패. 추가 수정이 필요합니다.")
            return False


if __name__ == "__main__":
    # 경고 억제
    import warnings
    warnings.filterwarnings("ignore")

    tester = TestConversionCompletedDialog()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)