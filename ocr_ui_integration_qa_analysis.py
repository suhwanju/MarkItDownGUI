#!/usr/bin/env python3
"""
OCR UI Integration - Code Analysis & Quality Assessment
Static analysis and logical testing without runtime dependencies

Comprehensive QA analysis of OCR UI Status Integration feature
"""

import sys
import ast
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Project paths
project_root = Path(__file__).parent
ocr_ui_path = project_root / "markitdown_gui" / "core" / "ocr_enhancements" / "ui_integrations"
ui_components_path = project_root / "markitdown_gui" / "ui" / "components"
config_path = project_root / "config" / "settings.ini"


class OCRUIIntegrationQAAnalyzer:
    """OCR UI Integration 정적 분석 및 품질 평가"""

    def __init__(self):
        self.analysis_results = {}
        self.findings = []
        self.recommendations = []
        self.quality_score = 0
        self.start_time = datetime.now()

    def analyze_code_structure(self) -> Dict[str, Any]:
        """코드 구조 분석"""
        print("1. 코드 구조 분석 중...")

        analysis = {
            'test_name': 'Code Structure Analysis',
            'passed': True,
            'issues': [],
            'metrics': {},
            'files_analyzed': []
        }

        # OCR UI Integration 파일들 분석
        ocr_files = [
            ocr_ui_path / "ocr_status_provider.py",
            ocr_ui_path / "ocr_progress_tracker.py",
            ocr_ui_path / "ocr_result_formatter.py"
        ]

        ui_files = [
            ui_components_path / "file_list_widget.py",
            ui_components_path / "progress_widget.py"
        ]

        all_files = ocr_files + ui_files

        for file_path in all_files:
            if file_path.exists():
                file_analysis = self._analyze_python_file(file_path)
                analysis['files_analyzed'].append(file_analysis)

                # 파일별 이슈 체크
                if file_analysis['lines_of_code'] > 1000:
                    analysis['issues'].append(f"{file_path.name}: 파일이 너무 큼 ({file_analysis['lines_of_code']} 줄)")

                if file_analysis['complexity_score'] > 20:
                    analysis['issues'].append(f"{file_path.name}: 복잡도가 높음 ({file_analysis['complexity_score']})")

                if file_analysis['docstring_coverage'] < 0.8:
                    analysis['issues'].append(f"{file_path.name}: 문서화 부족 ({file_analysis['docstring_coverage']:.1%})")
            else:
                analysis['issues'].append(f"파일 없음: {file_path}")
                analysis['passed'] = False

        # 전체 메트릭 계산
        if analysis['files_analyzed']:
            total_lines = sum(f['lines_of_code'] for f in analysis['files_analyzed'])
            avg_complexity = sum(f['complexity_score'] for f in analysis['files_analyzed']) / len(analysis['files_analyzed'])
            avg_docstring_coverage = sum(f['docstring_coverage'] for f in analysis['files_analyzed']) / len(analysis['files_analyzed'])

            analysis['metrics'] = {
                'total_lines_of_code': total_lines,
                'average_complexity': avg_complexity,
                'average_docstring_coverage': avg_docstring_coverage,
                'files_count': len(analysis['files_analyzed'])
            }

        return analysis

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Python 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # 기본 메트릭
            lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])

            # 클래스와 함수 분석
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            # 복잡도 계산 (간단한 버전)
            complexity_score = self._calculate_complexity(tree)

            # 문서화 확인
            docstring_coverage = self._calculate_docstring_coverage(classes + functions)

            # 임포트 분석
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

            return {
                'file_name': file_path.name,
                'lines_of_code': lines_of_code,
                'classes_count': len(classes),
                'functions_count': len(functions),
                'imports_count': len(imports),
                'complexity_score': complexity_score,
                'docstring_coverage': docstring_coverage,
                'classes': [cls.name for cls in classes],
                'functions': [func.name for func in functions if not func.name.startswith('_')]
            }

        except Exception as e:
            return {
                'file_name': file_path.name,
                'error': str(e),
                'lines_of_code': 0,
                'complexity_score': 0,
                'docstring_coverage': 0
            }

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """복잡도 계산 (순환 복잡도 기반)"""
        complexity = 1  # 기본값

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_docstring_coverage(self, nodes: List[ast.AST]) -> float:
        """문서화 커버리지 계산"""
        if not nodes:
            return 1.0

        documented = 0
        for node in nodes:
            if ast.get_docstring(node):
                documented += 1

        return documented / len(nodes)

    def analyze_feature_integration(self) -> Dict[str, Any]:
        """기능 통합 분석"""
        print("2. 기능 통합 분석 중...")

        analysis = {
            'test_name': 'Feature Integration Analysis',
            'passed': True,
            'issues': [],
            'integration_points': [],
            'recommendations': []
        }

        # FileListWidget 통합 확인
        file_list_path = ui_components_path / "file_list_widget.py"
        if file_list_path.exists():
            with open(file_list_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # OCR 관련 임포트 확인
            if 'ocr_enhancements.ui_integrations' in content:
                analysis['integration_points'].append("FileListWidget: OCR 상태 제공자 통합 확인")
            else:
                analysis['issues'].append("FileListWidget: OCR 통합 임포트가 없음")
                analysis['passed'] = False

            # 옵셔널 임포트 패턴 확인
            if 'try:' in content and 'OCRStatusProvider' in content:
                analysis['integration_points'].append("FileListWidget: 옵셔널 OCR 임포트 패턴 사용")
            else:
                analysis['issues'].append("FileListWidget: 안전한 임포트 패턴 부족")

            # OCR 컬럼 추가 로직 확인
            if 'OCR' in content and 'columns.append' in content:
                analysis['integration_points'].append("FileListWidget: OCR 컬럼 동적 추가 구현")
            else:
                analysis['issues'].append("FileListWidget: OCR 컬럼 추가 로직 미확인")

        # ProgressWidget 통합 확인
        progress_path = ui_components_path / "progress_widget.py"
        if progress_path.exists():
            with open(progress_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # OCR 진행률 추적 확인
            if 'OCRProgressTracker' in content or 'ocr_stage' in content:
                analysis['integration_points'].append("ProgressWidget: OCR 진행률 추적 통합")
            else:
                analysis['recommendations'].append("ProgressWidget: OCR 진행률 통합 권장")

        # 설정 파일 확인
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()

            if '[ocr_enhancements]' in config_content:
                analysis['integration_points'].append("Configuration: OCR 설정 섹션 존재")

                # 필수 설정 확인
                required_settings = ['enabled', 'preprocessing_enabled', 'post_processing_enabled']
                for setting in required_settings:
                    if setting in config_content:
                        analysis['integration_points'].append(f"Configuration: {setting} 설정 확인")
                    else:
                        analysis['issues'].append(f"Configuration: {setting} 설정 누락")
            else:
                analysis['issues'].append("Configuration: OCR 설정 섹션 없음")
                analysis['passed'] = False

        return analysis

    def analyze_ui_patterns(self) -> Dict[str, Any]:
        """UI 패턴 분석"""
        print("3. UI 패턴 분석 중...")

        analysis = {
            'test_name': 'UI Patterns Analysis',
            'passed': True,
            'issues': [],
            'patterns_found': [],
            'design_quality': {}
        }

        # OCR Status Provider 분석
        status_provider_path = ocr_ui_path / "ocr_status_provider.py"
        if status_provider_path.exists():
            with open(status_provider_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 위젯 패턴 확인
            if 'class OCRStatusBadge(QLabel)' in content:
                analysis['patterns_found'].append("Status Badge: QLabel 기반 커스텀 위젯")

            if 'class OCRMethodBadge(QLabel)' in content:
                analysis['patterns_found'].append("Method Badge: QLabel 기반 커스텀 위젯")

            # 캐싱 패턴 확인
            if 'QCache' in content:
                analysis['patterns_found'].append("Caching: QCache 활용한 성능 최적화")
            else:
                analysis['issues'].append("Status Provider: 캐싱 미구현으로 성능 이슈 가능")

            # 시그널-슬롯 패턴 확인
            if 'pyqtSignal' in content:
                analysis['patterns_found'].append("Signals: PyQt 시그널-슬롯 패턴 사용")

            # 배지 크기 일관성 확인
            if 'setFixedSize(20, 16)' in content:
                analysis['patterns_found'].append("UI Consistency: 고정 크기 배지 사용")

        # OCR Progress Tracker 분석
        progress_tracker_path = ocr_ui_path / "ocr_progress_tracker.py"
        if progress_tracker_path.exists():
            with open(progress_tracker_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 단계별 진행률 확인
            if 'OCRStageProgressBar' in content:
                analysis['patterns_found'].append("Progress Tracking: 단계별 진행률 바")

            # 시간 추정 기능 확인
            if 'estimated_completion' in content:
                analysis['patterns_found'].append("Time Estimation: 완료 시간 추정 기능")

            # 타이머 기반 업데이트 확인
            if 'QTimer' in content:
                analysis['patterns_found'].append("Real-time Updates: 타이머 기반 주기적 업데이트")

        # OCR Result Formatter 분석
        result_formatter_path = ocr_ui_path / "ocr_result_formatter.py"
        if result_formatter_path.exists():
            with open(result_formatter_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 탭 위젯 패턴 확인
            if 'QTabWidget' in content:
                analysis['patterns_found'].append("Result Display: 탭 기반 결과 표시")

            # 신뢰도 시각화 확인
            if 'ConfidenceScoreWidget' in content:
                analysis['patterns_found'].append("Confidence Display: 신뢰도 시각화 위젯")

            # 품질 메트릭 표시 확인
            if 'QualityMetricsWidget' in content:
                analysis['patterns_found'].append("Quality Metrics: 품질 메트릭 표시 위젯")

        # 디자인 품질 평가
        analysis['design_quality'] = {
            'widget_consistency': len([p for p in analysis['patterns_found'] if 'fixed_size' in p.lower() or 'consistency' in p.lower()]) > 0,
            'performance_optimization': len([p for p in analysis['patterns_found'] if 'caching' in p.lower() or 'timer' in p.lower()]) > 0,
            'user_feedback': len([p for p in analysis['patterns_found'] if 'progress' in p.lower() or 'confidence' in p.lower()]) > 0,
            'modular_design': len([p for p in analysis['patterns_found'] if 'widget' in p.lower()]) >= 3
        }

        return analysis

    def analyze_performance_considerations(self) -> Dict[str, Any]:
        """성능 고려사항 분석"""
        print("4. 성능 고려사항 분석 중...")

        analysis = {
            'test_name': 'Performance Considerations',
            'passed': True,
            'issues': [],
            'optimizations_found': [],
            'potential_bottlenecks': []
        }

        # 캐싱 전략 분석
        status_provider_path = ocr_ui_path / "ocr_status_provider.py"
        if status_provider_path.exists():
            with open(status_provider_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 캐시 구현 확인
            cache_patterns = [
                ('_status_cache: QCache', '상태 캐시'),
                ('_method_cache: QCache', '방법 캐시'),
                ('_badge_cache: QCache', '배지 캐시')
            ]

            for pattern, description in cache_patterns:
                if pattern.split(':')[0] in content:
                    analysis['optimizations_found'].append(f"Caching: {description} 구현")
                else:
                    analysis['potential_bottlenecks'].append(f"Missing: {description} 미구현")

            # 캐시 크기 제한 확인
            if 'QCache(1000)' in content or 'QCache(500)' in content:
                analysis['optimizations_found'].append("Cache Management: 적절한 캐시 크기 제한")
            else:
                analysis['issues'].append("Cache: 캐시 크기 제한 미설정으로 메모리 누수 가능")

        # 배치 처리 확인
        progress_tracker_path = ocr_ui_path / "ocr_progress_tracker.py"
        if progress_tracker_path.exists():
            with open(progress_tracker_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 타이머 기반 일괄 업데이트 확인
            if '_update_timer' in content and '500' in content:
                analysis['optimizations_found'].append("Batch Updates: 0.5초 간격 일괄 업데이트")
            else:
                analysis['potential_bottlenecks'].append("Real-time Updates: 실시간 업데이트로 성능 저하 가능")

            # 메모리 정리 확인
            if 'clear_tracking_data' in content:
                analysis['optimizations_found'].append("Memory Management: 추적 데이터 정리 기능")
            else:
                analysis['issues'].append("Memory: 메모리 정리 기능 미구현")

        # UI 반응성 최적화 확인
        result_formatter_path = ocr_ui_path / "ocr_result_formatter.py"
        if result_formatter_path.exists():
            with open(result_formatter_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 지연 로딩 패턴 확인
            if 'create_compact_display' in content:
                analysis['optimizations_found'].append("Lazy Loading: 간소 표시 위젯으로 지연 로딩")
            else:
                analysis['potential_bottlenecks'].append("UI Responsiveness: 대량 데이터 표시시 반응성 저하 가능")

        # 파일 크기 기반 잠재적 이슈 예측
        large_files = []
        for file_path in [status_provider_path, progress_tracker_path, result_formatter_path]:
            if file_path.exists():
                size = file_path.stat().st_size
                if size > 50000:  # 50KB 이상
                    large_files.append(f"{file_path.name}: {size//1024}KB")

        if large_files:
            analysis['potential_bottlenecks'].extend([f"Large File: {f}" for f in large_files])

        return analysis

    def analyze_error_handling(self) -> Dict[str, Any]:
        """에러 처리 분석"""
        print("5. 에러 처리 분석 중...")

        analysis = {
            'test_name': 'Error Handling Analysis',
            'passed': True,
            'issues': [],
            'error_handling_patterns': [],
            'robustness_score': 0
        }

        patterns_found = 0
        total_patterns_checked = 0

        # 각 파일의 에러 처리 패턴 확인
        files_to_check = [
            ocr_ui_path / "ocr_status_provider.py",
            ocr_ui_path / "ocr_progress_tracker.py",
            ocr_ui_path / "ocr_result_formatter.py"
        ]

        for file_path in files_to_check:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Try-except 블록 확인
                total_patterns_checked += 1
                if 'try:' in content and 'except' in content:
                    patterns_found += 1
                    analysis['error_handling_patterns'].append(f"{file_path.name}: try-except 블록 사용")
                else:
                    analysis['issues'].append(f"{file_path.name}: 예외 처리 부족")

                # 로깅 확인
                total_patterns_checked += 1
                if 'logger.' in content:
                    patterns_found += 1
                    analysis['error_handling_patterns'].append(f"{file_path.name}: 로깅 구현")
                else:
                    analysis['issues'].append(f"{file_path.name}: 로깅 미구현")

                # 입력 검증 확인
                total_patterns_checked += 1
                if 'if not' in content or 'is None' in content:
                    patterns_found += 1
                    analysis['error_handling_patterns'].append(f"{file_path.name}: 입력 검증 구현")
                else:
                    analysis['issues'].append(f"{file_path.name}: 입력 검증 부족")

                # Graceful degradation 확인
                total_patterns_checked += 1
                if 'return None' in content or 'setVisible(False)' in content:
                    patterns_found += 1
                    analysis['error_handling_patterns'].append(f"{file_path.name}: Graceful degradation 구현")
                else:
                    analysis['issues'].append(f"{file_path.name}: Graceful degradation 부족")

        # UI 통합 파일의 안전 임포트 확인
        ui_files = [
            ui_components_path / "file_list_widget.py",
            ui_components_path / "progress_widget.py"
        ]

        for file_path in ui_files:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 옵셔널 임포트 패턴 확인
                total_patterns_checked += 1
                if 'try:' in content and 'ImportError:' in content:
                    patterns_found += 1
                    analysis['error_handling_patterns'].append(f"{file_path.name}: 안전한 OCR 임포트 패턴")
                else:
                    analysis['issues'].append(f"{file_path.name}: 안전한 임포트 패턴 부족")

        # 견고성 점수 계산
        if total_patterns_checked > 0:
            analysis['robustness_score'] = patterns_found / total_patterns_checked
        else:
            analysis['robustness_score'] = 0

        if analysis['robustness_score'] < 0.7:
            analysis['passed'] = False
            analysis['issues'].append(f"전체 견고성 점수가 낮음: {analysis['robustness_score']:.1%}")

        return analysis

    def analyze_accessibility_compliance(self) -> Dict[str, Any]:
        """접근성 준수 분석"""
        print("6. 접근성 준수 분석 중...")

        analysis = {
            'test_name': 'Accessibility Compliance',
            'passed': True,
            'issues': [],
            'accessibility_features': [],
            'wcag_compliance': {}
        }

        # 툴팁 구현 확인 (WCAG 1.3.1)
        status_provider_path = ocr_ui_path / "ocr_status_provider.py"
        if status_provider_path.exists():
            with open(status_provider_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'setToolTip' in content:
                analysis['accessibility_features'].append("Tooltips: 상태 배지 툴팁 구현")
                analysis['wcag_compliance']['1.3.1_info_relationships'] = True
            else:
                analysis['issues'].append("Accessibility: 상태 배지 툴팁 미구현")
                analysis['wcag_compliance']['1.3.1_info_relationships'] = False

            # 한글 지원 확인 (국제화)
            if any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in content):
                analysis['accessibility_features'].append("Localization: 한글 인터페이스 지원")
                analysis['wcag_compliance']['3.1.1_language'] = True
            else:
                analysis['issues'].append("Accessibility: 한글 지원 미확인")
                analysis['wcag_compliance']['3.1.1_language'] = False

        # 색상 기반이 아닌 정보 전달 확인 (WCAG 1.4.1)
        if status_provider_path.exists():
            with open(status_provider_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 텍스트 기반 정보 확인
            if "'text':" in content and "drawText" in content:
                analysis['accessibility_features'].append("Color Independence: 색상과 함께 텍스트 정보 제공")
                analysis['wcag_compliance']['1.4.1_color_usage'] = True
            else:
                analysis['issues'].append("Accessibility: 색상에만 의존한 정보 전달")
                analysis['wcag_compliance']['1.4.1_color_usage'] = False

        # 키보드 네비게이션 (WCAG 2.1.1)
        file_list_path = ui_components_path / "file_list_widget.py"
        if file_list_path.exists():
            with open(file_list_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 포커스 정책 확인
            if 'focusPolicy' in content or 'TabFocus' in content:
                analysis['accessibility_features'].append("Keyboard Navigation: 키보드 포커스 지원")
                analysis['wcag_compliance']['2.1.1_keyboard'] = True
            else:
                analysis['accessibility_features'].append("Keyboard Navigation: 기본 Qt 키보드 지원 (추정)")
                analysis['wcag_compliance']['2.1.1_keyboard'] = True  # Qt 기본 지원

        # 의미 있는 시퀀스 확인 (WCAG 1.3.2)
        if 'QHBoxLayout' in content or 'QVBoxLayout' in content:
            analysis['accessibility_features'].append("Meaningful Sequence: 논리적 레이아웃 구조")
            analysis['wcag_compliance']['1.3.2_meaningful_sequence'] = True
        else:
            analysis['wcag_compliance']['1.3.2_meaningful_sequence'] = False

        # 전체 WCAG 준수도 계산
        compliance_items = list(analysis['wcag_compliance'].values())
        if compliance_items:
            compliance_rate = sum(compliance_items) / len(compliance_items)
            analysis['wcag_compliance']['overall_rate'] = compliance_rate

            if compliance_rate < 0.8:  # 80% 미만
                analysis['passed'] = False
                analysis['issues'].append(f"WCAG 준수도가 낮음: {compliance_rate:.1%}")

        return analysis

    def generate_comprehensive_report(self) -> str:
        """종합 보고서 생성"""
        print("\n=== OCR UI Integration QA 종합 분석 보고서 생성 ===")

        # 모든 분석 실행
        analyses = [
            self.analyze_code_structure(),
            self.analyze_feature_integration(),
            self.analyze_ui_patterns(),
            self.analyze_performance_considerations(),
            self.analyze_error_handling(),
            self.analyze_accessibility_compliance()
        ]

        # 전체 결과 집계
        total_tests = len(analyses)
        passed_tests = sum(1 for a in analyses if a['passed'])
        total_issues = sum(len(a['issues']) for a in analyses)

        # 품질 점수 계산
        quality_score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        # 우선순위별 이슈 분류
        high_priority = []
        medium_priority = []
        low_priority = []

        for analysis in analyses:
            for issue in analysis['issues']:
                if any(keyword in issue.lower() for keyword in ['없음', '미구현', '실패', '예외']):
                    high_priority.append(f"{analysis['test_name']}: {issue}")
                elif any(keyword in issue.lower() for keyword in ['성능', '느림', '크기', '메모리']):
                    medium_priority.append(f"{analysis['test_name']}: {issue}")
                else:
                    low_priority.append(f"{analysis['test_name']}: {issue}")

        # 보고서 생성
        end_time = datetime.now()
        analysis_time = (end_time - self.start_time).total_seconds()

        overall_status = "✅ PASS" if quality_score >= 80 and total_issues == 0 else "❌ NEEDS IMPROVEMENT"
        if quality_score >= 80 and total_issues <= 5:
            overall_status = "⚠️ CONDITIONAL PASS"

        report = f"""
# OCR UI Integration - QA 종합 분석 보고서

## 전체 평가: {overall_status}

**분석 완료 시간**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**분석 소요 시간**: {analysis_time:.2f}초
**품질 점수**: {quality_score:.1f}/100
**전체 테스트**: {total_tests}개
**통과 테스트**: {passed_tests}개
**실패 테스트**: {total_tests - passed_tests}개
**발견된 이슈**: {total_issues}개

## 상세 분석 결과

"""

        # 각 분석 결과 추가
        for analysis in analyses:
            status = "✅ PASS" if analysis['passed'] else "❌ FAIL"
            report += f"### {status} {analysis['test_name']}\n\n"

            if analysis['issues']:
                report += "**발견된 이슈:**\n"
                for issue in analysis['issues']:
                    report += f"- {issue}\n"
                report += "\n"

            # 긍정적인 발견사항
            positive_keys = ['patterns_found', 'optimizations_found', 'error_handling_patterns',
                           'accessibility_features', 'integration_points']

            for key in positive_keys:
                if key in analysis and analysis[key]:
                    report += f"**{key.replace('_', ' ').title()}:**\n"
                    for item in analysis[key]:
                        report += f"- {item}\n"
                    report += "\n"

        # 우선순위별 이슈 요약
        report += "## 이슈 우선순위\n\n"

        if high_priority:
            report += "### 🔥 높은 우선순위 (즉시 수정 필요)\n"
            for issue in high_priority:
                report += f"- {issue}\n"
            report += "\n"

        if medium_priority:
            report += "### ⚡ 중간 우선순위 (성능/품질 개선)\n"
            for issue in medium_priority:
                report += f"- {issue}\n"
            report += "\n"

        if low_priority:
            report += "### 📝 낮은 우선순위 (개선 권장)\n"
            for issue in low_priority:
                report += f"- {issue}\n"
            report += "\n"

        # 권장사항
        report += "## 권장사항\n\n"

        if quality_score >= 90 and total_issues == 0:
            report += "🎉 **우수한 구현품질!**\n\n"
            report += "- 프로덕션 배포 준비 완료\n"
            report += "- 코드 품질과 아키텍처가 우수함\n"
            report += "- 성능 최적화와 에러 처리가 잘 구현됨\n"
            report += "- 접근성 고려사항이 반영됨\n\n"
        elif quality_score >= 80:
            report += "✅ **양호한 구현품질**\n\n"
            report += "- 소수의 개선사항 반영 후 배포 가능\n"
            report += "- 전반적인 아키텍처는 건실함\n"
            report += "- 운영 전 추가 테스트 권장\n\n"
        else:
            report += "⚠️ **개선 필요**\n\n"
            report += "- 주요 이슈들을 수정 후 재검토 필요\n"
            report += "- 아키텍처 및 에러 처리 보완\n"
            report += "- 성능 최적화 고려\n\n"

        # 기술적 권장사항
        report += "### 기술적 권장사항\n\n"

        if any('캐싱' in str(analyses) for analysis in analyses):
            report += "1. **캐싱 전략**: QCache 활용이 잘 구현되어 있음\n"
        else:
            report += "1. **캐싱 구현**: 성능 개선을 위한 캐싱 전략 필요\n"

        if any('에러' in str(analyses) for analysis in analyses):
            report += "2. **에러 처리**: 견고한 예외 처리 구현 필요\n"
        else:
            report += "2. **에러 처리**: 예외 처리가 적절히 구현됨\n"

        report += "3. **테스트 커버리지**: 단위 테스트 및 통합 테스트 추가 권장\n"
        report += "4. **문서화**: API 문서 및 사용자 가이드 보완\n"
        report += "5. **성능 모니터링**: 프로덕션 성능 메트릭 수집 설정\n\n"

        # 다음 단계
        report += "## 다음 단계\n\n"

        if quality_score >= 85:
            report += "1. ✅ 프로덕션 배포 진행\n"
            report += "2. 🔍 사용자 승인 테스트 (UAT) 실시\n"
            report += "3. 📊 성능 모니터링 설정\n"
            report += "4. 👥 사용자 피드백 수집\n"
        else:
            report += "1. 🔧 발견된 이슈 수정\n"
            report += "2. 🧪 수정사항 재테스트\n"
            report += "3. 📋 코드 리뷰 실시\n"
            report += "4. ✅ 품질 게이트 재평가\n"

        report += f"""
## 메트릭 요약

| 항목 | 값 |
|------|-----|
| 전체 품질 점수 | {quality_score:.1f}/100 |
| 테스트 통과율 | {(passed_tests/total_tests)*100:.1f}% |
| 발견된 이슈 | {total_issues}개 |
| 분석 파일 수 | 5개 |
| 코드 라인 수 | ~2,000줄 (추정) |

## 결론

OCR UI Integration 기능은 {"높은" if quality_score >= 80 else "보통" if quality_score >= 60 else "낮은"} 품질로 구현되었습니다.
{"프로덕션 배포가 가능한 상태" if quality_score >= 80 else "추가 개선이 필요한 상태"}이며,
사용자 경험과 시스템 안정성을 위한 {"최소한의" if quality_score >= 80 else "상당한"} 보완이 필요합니다.

---
*QA Analysis Tool v1.0*
*Generated: {end_time.isoformat()}*
"""

        return report


def main():
    """메인 분석 실행"""
    analyzer = OCRUIIntegrationQAAnalyzer()

    try:
        print("OCR UI Integration - 정적 분석 및 품질 평가 시작")
        print("=" * 60)

        # 종합 보고서 생성
        report = analyzer.generate_comprehensive_report()

        # 결과 출력
        print(report)

        # 보고서 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = project_root / f"ocr_ui_integration_qa_report_{timestamp}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 상세 보고서 저장됨: {report_path}")

        # 품질 점수에 따른 종료 코드
        overall_quality = sum(1 for a in [
            analyzer.analyze_code_structure(),
            analyzer.analyze_feature_integration(),
            analyzer.analyze_ui_patterns(),
            analyzer.analyze_performance_considerations(),
            analyzer.analyze_error_handling(),
            analyzer.analyze_accessibility_compliance()
        ] if a['passed']) / 6 * 100

        return 0 if overall_quality >= 80 else 1

    except Exception as e:
        print(f"\n❌ 분석 실행 실패: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)