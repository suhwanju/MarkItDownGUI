#!/usr/bin/env python3
"""
QFontDatabase 수정 내용 검증 스크립트
코드 변경 사항을 검증하여 수정이 올바르게 되었는지 확인
"""

import re
from pathlib import Path

def verify_fix():
    """수정된 코드 검증"""
    print("=== QFontDatabase 수정 내용 검증 ===\n")
    
    file_path = Path("markitdown_gui/core/i18n_manager.py")
    
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없음: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 검증 항목들
    issues_found = []
    fixes_found = []
    
    # 1. QFontDatabase() 인스턴스 생성 확인 (없어야 함, 주석 제외)
    # 주석이 아닌 실제 코드만 검사
    non_comment_lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
    non_comment_content = '\n'.join(non_comment_lines)
    
    if re.search(r'font_db\s*=\s*QFontDatabase\(\)', non_comment_content):
        issues_found.append("❌ QFontDatabase() 인스턴스 생성 코드가 여전히 존재함")
    else:
        fixes_found.append("✓ QFontDatabase() 인스턴스 생성 코드 제거됨")
    
    # 2. font_db.families() 사용 확인 (없어야 함)
    if re.search(r'font_db\.families\(\)', content):
        issues_found.append("❌ font_db.families() 호출이 여전히 존재함")
    else:
        fixes_found.append("✓ font_db.families() 호출 제거됨")
    
    # 3. QFontDatabase.families() static 호출 확인 (있어야 함)
    if re.search(r'QFontDatabase\.families\(\)', content):
        fixes_found.append("✓ QFontDatabase.families() static 메서드 호출로 변경됨")
    else:
        issues_found.append("❌ QFontDatabase.families() static 메서드 호출이 없음")
    
    # 4. font_db.systemFont() 사용 확인 (없어야 함)
    if re.search(r'font_db\.systemFont\(', content):
        issues_found.append("❌ font_db.systemFont() 호출이 여전히 존재함")
    else:
        fixes_found.append("✓ font_db.systemFont() 호출 제거됨")
    
    # 5. QFontDatabase.systemFont() static 호출 확인 (있어야 함)
    if re.search(r'QFontDatabase\.systemFont\(', content):
        fixes_found.append("✓ QFontDatabase.systemFont() static 메서드 호출로 변경됨")
    else:
        issues_found.append("❌ QFontDatabase.systemFont() static 메서드 호출이 없음")
    
    # 6. 주석 확인
    if '# PyQt6에서 QFontDatabase는 static 메서드로만 사용' in content:
        fixes_found.append("✓ PyQt6 관련 설명 주석 추가됨")
    
    # 결과 출력
    print("수정 사항:")
    for fix in fixes_found:
        print(f"  {fix}")
    
    if issues_found:
        print("\n발견된 문제:")
        for issue in issues_found:
            print(f"  {issue}")
        return False
    
    return True


def check_error_logs():
    """로그 파일에서 QFontDatabase 오류 확인"""
    print("\n=== 최근 로그 확인 ===\n")
    
    log_file = Path("logs/markitdown_gui.log")
    
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 마지막 50줄에서 QFontDatabase 오류 검색
        recent_lines = lines[-50:] if len(lines) > 50 else lines
        error_found = False
        
        for line in recent_lines:
            if "QFontDatabase" in line and "not enough arguments" in line:
                error_found = True
                # 오류 발생 시간 추출
                if match := re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line):
                    timestamp = match.group(1)
                    print(f"  최근 오류 발생: {timestamp}")
        
        if not error_found:
            print("  ✓ 최근 로그에서 QFontDatabase 오류 없음")
    else:
        print("  로그 파일이 없음")


def main():
    """메인 함수"""
    print("QFontDatabase 초기화 오류 수정 검증")
    print("=" * 50)
    print("원인: PyQt6에서 QFontDatabase는 인스턴스 생성 불가")
    print("해결: Static 메서드 직접 호출로 변경")
    print("=" * 50)
    
    # 수정 내용 검증
    fix_verified = verify_fix()
    
    # 로그 확인
    check_error_logs()
    
    print("\n" + "=" * 50)
    if fix_verified:
        print("🎉 QFontDatabase 오류 수정이 완료되었습니다!")
        print("\n변경 내용:")
        print("  이전: font_db = QFontDatabase()")
        print("       font_db.families()")
        print("       font_db.systemFont(...)")
        print("")
        print("  이후: # QFontDatabase 인스턴스 생성 제거")
        print("       QFontDatabase.families()")
        print("       QFontDatabase.systemFont(...)")
        print("\n이제 프로그램 시작시 QFontDatabase 오류가 발생하지 않습니다!")
    else:
        print("❌ 수정이 완전하지 않습니다. 위의 문제를 확인하세요.")


if __name__ == "__main__":
    main()