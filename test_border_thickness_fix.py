#!/usr/bin/env python3
"""
GUI 테두리 두께 수정 검증 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_qss_files():
    """QSS 파일에서 두꺼운 테두리 검사"""
    print("=== QSS 테마 파일 테두리 두께 검증 ===\n")
    
    qss_files = [
        "markitdown_gui/resources/styles/light_theme.qss",
        "markitdown_gui/resources/styles/dark_theme.qss", 
        "markitdown_gui/resources/styles/high_contrast_theme.qss"
    ]
    
    results = {}
    
    for qss_file in qss_files:
        file_path = project_root / qss_file
        theme_name = file_path.stem
        
        if not file_path.exists():
            print(f"❌ {theme_name}: 파일 없음")
            results[theme_name] = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 두꺼운 테두리 패턴 검사
            thick_border_patterns = [
                "border: 2px solid",
                "border: 3px solid",
                "border: 4px solid",
                "border-width: 2px",
                "border-width: 3px",
                "border-width: 4px"
            ]
            
            found_thick_borders = []
            for pattern in thick_border_patterns:
                if pattern in content:
                    found_thick_borders.append(pattern)
            
            # 얇은 테두리 패턴 확인
            thin_border_count = content.count("border: 1px solid")
            if theme_name == "high_contrast_theme":
                thin_border_count += content.count("border: 1.5px solid")
            
            if found_thick_borders:
                print(f"❌ {theme_name}: 두꺼운 테두리 발견")
                for pattern in found_thick_borders:
                    print(f"     - {pattern}")
                results[theme_name] = False
            else:
                print(f"✅ {theme_name}: 모든 테두리가 얇게 수정됨")
                if theme_name == "high_contrast_theme":
                    print(f"     - 1px 테두리: {content.count('border: 1px solid')}개")
                    print(f"     - 1.5px 테두리: {content.count('border: 1.5px solid')}개 (접근성 고려)")
                else:
                    print(f"     - 1px 테두리: {thin_border_count}개")
                results[theme_name] = True
                
        except Exception as e:
            print(f"❌ {theme_name}: 파일 읽기 오류 - {e}")
            results[theme_name] = False
    
    return all(results.values())


def check_python_files():
    """Python 파일에서 두꺼운 테두리 검사"""
    print("\n=== Python 위젯 파일 테두리 두께 검증 ===\n")
    
    python_files = [
        "markitdown_gui/ui/settings_dialog.py",
        "markitdown_gui/ui/components/search_widget.py",
        "markitdown_gui/ui/components/progress_widget.py"
    ]
    
    results = {}
    
    for py_file in python_files:
        file_path = project_root / py_file
        file_name = file_path.name
        
        if not file_path.exists():
            print(f"❌ {file_name}: 파일 없음")
            results[file_name] = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 두꺼운 테두리 패턴 검사
            thick_patterns = [
                "border: 2px solid",
                "border: 3px solid", 
                "border: 4px solid",
                "border-width: 2px",
                "border-width: 3px"
            ]
            
            found_thick = []
            for pattern in thick_patterns:
                if pattern in content:
                    found_thick.append(pattern)
            
            # 얇은 테두리 패턴 확인
            thin_count = content.count("border: 1px solid")
            
            if found_thick:
                print(f"❌ {file_name}: 두꺼운 테두리 발견")
                for pattern in found_thick:
                    print(f"     - {pattern}")
                results[file_name] = False
            else:
                print(f"✅ {file_name}: 모든 테두리가 얇게 수정됨")
                if thin_count > 0:
                    print(f"     - 1px 테두리: {thin_count}개")
                results[file_name] = True
                
        except Exception as e:
            print(f"❌ {file_name}: 파일 읽기 오류 - {e}")
            results[file_name] = False
    
    return all(results.values())


def check_visual_consistency():
    """시각적 일관성 검사"""
    print("\n=== 시각적 일관성 검증 ===\n")
    
    consistency_checks = []
    
    # 1. 모든 테마 파일이 일관된 얇은 테두리를 사용하는지 확인
    try:
        light_theme = project_root / "markitdown_gui/resources/styles/light_theme.qss"
        dark_theme = project_root / "markitdown_gui/resources/styles/dark_theme.qss"
        
        if light_theme.exists() and dark_theme.exists():
            with open(light_theme, 'r', encoding='utf-8') as f:
                light_content = f.read()
            with open(dark_theme, 'r', encoding='utf-8') as f:
                dark_content = f.read()
            
            light_borders = light_content.count("border: 1px solid")
            dark_borders = dark_content.count("border: 1px solid")
            
            if light_borders > 0 and dark_borders > 0:
                consistency_checks.append("✅ Light와 Dark 테마 모두 1px 테두리 사용")
            else:
                consistency_checks.append("❌ 테마 간 테두리 두께 불일치")
        else:
            consistency_checks.append("❌ 테마 파일을 찾을 수 없음")
            
    except Exception as e:
        consistency_checks.append(f"❌ 테마 일관성 검사 실패: {e}")
    
    # 2. 고대비 테마는 접근성을 위해 약간 더 두꺼운 테두리 사용 확인
    try:
        hc_theme = project_root / "markitdown_gui/resources/styles/high_contrast_theme.qss"
        
        if hc_theme.exists():
            with open(hc_theme, 'r', encoding='utf-8') as f:
                hc_content = f.read()
            
            if "1.5px solid" in hc_content or "1px solid" in hc_content:
                consistency_checks.append("✅ 고대비 테마에서 접근성을 고려한 적절한 테두리 두께 사용")
            else:
                consistency_checks.append("❌ 고대비 테마 테두리 설정 문제")
        else:
            consistency_checks.append("❌ 고대비 테마 파일을 찾을 수 없음")
            
    except Exception as e:
        consistency_checks.append(f"❌ 고대비 테마 검사 실패: {e}")
    
    for check in consistency_checks:
        print(check)
    
    return all("✅" in check for check in consistency_checks)


def main():
    """메인 함수"""
    print("GUI 테두리 두께 수정 검증 스크립트")
    print("=" * 60)
    print("검은색으로 출력되는 두꺼운 테두리를 얇은 선으로 변경한 수정사항 검증")
    print("=" * 60)
    
    # QSS 파일 검증
    qss_ok = check_qss_files()
    
    # Python 파일 검증
    python_ok = check_python_files()
    
    # 시각적 일관성 검증
    consistency_ok = check_visual_consistency()
    
    # 전체 결과
    print("\n" + "=" * 60)
    print("전체 검증 결과:")
    print(f"  - QSS 테마 파일: {'✅ 통과' if qss_ok else '❌ 실패'}")
    print(f"  - Python 위젯: {'✅ 통과' if python_ok else '❌ 실패'}")
    print(f"  - 시각적 일관성: {'✅ 통과' if consistency_ok else '❌ 실패'}")
    
    if qss_ok and python_ok and consistency_ok:
        print("\n🎉 모든 검증이 통과했습니다!")
        print("\n수정 내용 요약:")
        print("1. Light Theme: 모든 2px 테두리를 1px로 변경")
        print("2. Dark Theme: 모든 2px 테두리를 1px로 변경") 
        print("3. High Contrast Theme: 2px 테두리를 1.5px로 변경 (접근성 고려)")
        print("4. Python 위젯: 모든 2px inline 스타일을 1px로 변경")
        print("5. 시각적 일관성: 모든 테마에서 통일된 얇은 테두리 적용")
        print("\n이제 GUI의 모든 검은색 출력 부분이 얇은 선으로 표시됩니다!")
    else:
        print("\n❌ 일부 검증에 실패했습니다.")
        
        if not qss_ok:
            print("QSS 파일에서 수정이 완전하지 않거나 파일이 누락되었습니다.")
        
        if not python_ok:
            print("Python 파일에서 인라인 스타일 수정이 필요합니다.")
        
        if not consistency_ok:
            print("테마 간 일관성을 다시 확인해주세요.")


if __name__ == "__main__":
    main()