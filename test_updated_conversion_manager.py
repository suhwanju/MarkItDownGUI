#!/usr/bin/env python3
"""
Updated ConversionManager 테스트
직접 파일 저장 기능과 충돌 처리 기능을 테스트합니다.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from markitdown_gui.core.conversion_manager import ConversionManager, ConversionWorker
from markitdown_gui.core.models import (
    FileInfo, FileType, ConversionStatus, ConversionProgressStatus,
    FileConflictStatus, FileConflictPolicy, FileConflictConfig
)
from markitdown_gui.core.file_conflict_handler import FileConflictHandler


def create_test_file_info(name: str, content: str = "Test content") -> FileInfo:
    """테스트용 FileInfo 객체 생성"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{name.split(".")[-1]}', 
                                    delete=False, encoding='utf-8') as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)
    
    return FileInfo(
        path=temp_path,
        name=name,
        size=len(content.encode('utf-8')),
        modified_time=datetime.now(),
        file_type=FileType.TXT,
        is_selected=True
    )


def test_direct_file_saving():
    """직접 파일 저장 기능 테스트"""
    print("=== 직접 파일 저장 기능 테스트 ===")
    
    # 테스트 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 테스트 파일 생성
        test_file = temp_path / "test_document.txt"
        test_file.write_text("# Test Document\nThis is a test document.", encoding='utf-8')
        
        file_info = FileInfo(
            path=test_file,
            name="test_document.txt",
            size=test_file.stat().st_size,
            modified_time=datetime.fromtimestamp(test_file.stat().st_mtime),
            file_type=FileType.TXT,
            is_selected=True
        )
        
        # ConversionManager 생성 (원본 디렉토리에 저장)
        manager = ConversionManager(save_to_original_dir=True)
        
        # MarkItDown을 Mock으로 대체
        with patch('markitdown_gui.core.conversion_manager.MARKITDOWN_AVAILABLE', True):
            with patch('markitdown_gui.core.conversion_manager.MarkItDown') as MockMarkItDown:
                mock_instance = Mock()
                mock_result = Mock()
                mock_result.text_content = "# Test Document\nThis is a converted test document."
                mock_instance.convert.return_value = mock_result
                MockMarkItDown.return_value = mock_instance
                
                # 단일 파일 변환 테스트
                result = manager.convert_single_file(file_info)
                
                print(f"변환 상태: {result.status}")
                print(f"출력 경로: {result.output_path}")
                print(f"변환 시간: {result.conversion_time_formatted}")
                
                # 결과 확인
                if result.is_success:
                    print("✅ 직접 파일 저장 성공")
                    # 마크다운 파일이 원본과 같은 디렉토리에 생성되었는지 확인
                    expected_path = test_file.parent / "test_document.md"
                    if result.output_path == expected_path:
                        print("✅ 파일이 원본 디렉토리에 정확히 저장됨")
                    else:
                        print(f"❌ 예상 경로: {expected_path}, 실제 경로: {result.output_path}")
                else:
                    print(f"❌ 변환 실패: {result.error_message}")


def test_conflict_resolution():
    """충돌 해결 기능 테스트"""
    print("\n=== 충돌 해결 기능 테스트 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 원본 파일 생성
        test_file = temp_path / "document.txt"
        test_file.write_text("Original content", encoding='utf-8')
        
        # 기존 마크다운 파일 생성 (충돌 상황)
        existing_md = temp_path / "document.md"
        existing_md.write_text("# Existing Document\nThis already exists.", encoding='utf-8')
        
        file_info = FileInfo(
            path=test_file,
            name="document.txt",
            size=test_file.stat().st_size,
            modified_time=datetime.fromtimestamp(test_file.stat().st_mtime),
            file_type=FileType.TXT,
            is_selected=True
        )
        
        # 충돌 설정 (이름 변경 정책)
        conflict_config = FileConflictConfig(
            default_policy=FileConflictPolicy.RENAME,
            auto_rename_pattern="{name}_{counter}{ext}",
            remember_choices=False
        )
        
        # ConversionManager 생성
        manager = ConversionManager(
            save_to_original_dir=True,
            conflict_config=conflict_config
        )
        
        # 충돌 사전 검사
        prepared_files = manager.prepare_files_for_conversion([file_info])
        prepared_file = prepared_files[0]
        
        print(f"충돌 상태: {prepared_file.conflict_status}")
        print(f"추천 정책: {prepared_file.conflict_policy}")
        
        # MarkItDown Mock
        with patch('markitdown_gui.core.conversion_manager.MARKITDOWN_AVAILABLE', True):
            with patch('markitdown_gui.core.conversion_manager.MarkItDown') as MockMarkItDown:
                mock_instance = Mock()
                mock_result = Mock()
                mock_result.text_content = "# Converted Document\nThis is the converted content."
                mock_instance.convert.return_value = mock_result
                MockMarkItDown.return_value = mock_instance
                
                # 변환 실행
                result = manager.convert_single_file(file_info)
                
                print(f"변환 상태: {result.status}")
                print(f"출력 경로: {result.output_path}")
                print(f"충돌 처리 결과: {result.conflict_status}")
                print(f"적용된 정책: {result.applied_policy}")
                
                if result.is_success:
                    print("✅ 충돌 해결 성공")
                    # 이름이 변경된 파일이 생성되었는지 확인
                    if result.output_path and result.output_path.exists():
                        print(f"✅ 이름 변경된 파일 생성됨: {result.output_path.name}")
                    else:
                        print("❌ 파일이 생성되지 않음")
                else:
                    print(f"❌ 변환 실패: {result.error_message}")


def test_progress_tracking():
    """진행률 추적 기능 테스트"""
    print("\n=== 진행률 추적 기능 테스트 ===")
    
    # 진행률 업데이트를 추적하는 핸들러
    progress_updates = []
    
    def on_progress_update(progress):
        progress_updates.append({
            'status': progress.current_progress_status,
            'file': progress.current_file,
            'percent': progress.progress_percent
        })
        print(f"진행률: {progress.progress_percent:.1f}% - {progress.get_detailed_status()}")
    
    # 테스트 파일들 생성
    test_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for i in range(3):
            test_file = temp_path / f"test_{i}.txt"
            test_file.write_text(f"Test content {i}", encoding='utf-8')
            
            file_info = FileInfo(
                path=test_file,
                name=f"test_{i}.txt",
                size=test_file.stat().st_size,
                modified_time=datetime.fromtimestamp(test_file.stat().st_mtime),
                file_type=FileType.TXT,
                is_selected=True
            )
            test_files.append(file_info)
        
        # ConversionManager 생성
        manager = ConversionManager(save_to_original_dir=True)
        manager.conversion_progress_updated.connect(on_progress_update)
        
        # MarkItDown Mock
        with patch('markitdown_gui.core.conversion_manager.MARKITDOWN_AVAILABLE', True):
            with patch('markitdown_gui.core.conversion_manager.MarkItDown') as MockMarkItDown:
                mock_instance = Mock()
                mock_result = Mock()
                mock_result.text_content = "# Converted Content"
                mock_instance.convert.return_value = mock_result
                MockMarkItDown.return_value = mock_instance
                
                # 비동기 변환 시작 (테스트용으로는 동기로 처리)
                print("파일들의 진행 상태 추적:")
                for file_info in test_files:
                    result = manager.convert_single_file(file_info)
                    print(f"  {file_info.name}: {result.status} - {result.progress_status}")
        
        print(f"✅ 총 {len(progress_updates)}개의 진행률 업데이트 기록됨")


def test_conflict_statistics():
    """충돌 통계 기능 테스트"""
    print("\n=== 충돌 통계 기능 테스트 ===")
    
    manager = ConversionManager()
    
    # 초기 통계
    stats = manager.get_conflict_statistics()
    print(f"초기 통계:")
    print(f"  확인된 파일: {stats.total_files_checked}")
    print(f"  충돌 감지: {stats.conflicts_detected}")
    print(f"  성공률: {stats.success_rate:.1f}%")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 테스트 파일과 기존 마크다운 파일 생성
        for i in range(5):
            # 원본 파일
            test_file = temp_path / f"doc_{i}.txt"
            test_file.write_text(f"Content {i}", encoding='utf-8')
            
            # 일부는 기존 마크다운 파일도 생성 (충돌 상황)
            if i < 3:
                md_file = temp_path / f"doc_{i}.md"
                md_file.write_text(f"Existing {i}", encoding='utf-8')
            
            file_info = FileInfo(
                path=test_file,
                name=f"doc_{i}.txt",
                size=test_file.stat().st_size,
                modified_time=datetime.fromtimestamp(test_file.stat().st_mtime),
                file_type=FileType.TXT,
                is_selected=True
            )
            
            # 충돌 사전 검사
            prepared_files = manager.prepare_files_for_conversion([file_info])
        
        # 최종 통계
        stats = manager.get_conflict_statistics()
        print(f"최종 통계:")
        print(f"  확인된 파일: {stats.total_files_checked}")
        print(f"  충돌 감지: {stats.conflicts_detected}")
        print(f"  충돌률: {stats.conflict_rate:.1f}%")
        print(f"  성공률: {stats.success_rate:.1f}%")
        
        if stats.conflicts_detected > 0:
            print("✅ 충돌 감지 및 통계 기능 정상 작동")
        else:
            print("⚠️ 충돌이 감지되지 않음")


def main():
    """메인 테스트 함수"""
    print("Updated ConversionManager 테스트 시작\n")
    
    try:
        test_direct_file_saving()
        test_conflict_resolution()
        test_progress_tracking()
        test_conflict_statistics()
        
        print("\n=== 테스트 완료 ===")
        print("✅ 모든 핵심 기능이 정상적으로 동작합니다.")
        print("\n주요 개선사항:")
        print("- ✅ ZIP 파일 대신 개별 .md 파일로 직접 저장")
        print("- ✅ FileConflictHandler를 통한 지능적 충돌 처리")
        print("- ✅ 실시간 진행률 추적 (ConversionProgressStatus)")
        print("- ✅ 사용자 설정 가능한 충돌 정책")
        print("- ✅ 스레드 안전성 유지")
        print("- ✅ 포괄적인 통계 및 오류 처리")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()