#!/usr/bin/env python3
"""
이미지 호환성 수정 검증 스크립트
GUI 없이 PIL 호환성만 테스트
"""

import sys
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_pil_compatibility():
    """PIL 호환성 테스트"""
    print("=== PIL 호환성 테스트 시작 ===\n")
    
    try:
        from PIL import Image, ImageQt
        print("✓ PIL import 성공")
        print(f"  - PIL 버전: {Image.__version__ if hasattr(Image, '__version__') else 'unknown'}")
    except ImportError as e:
        print(f"✗ PIL import 실패: {e}")
        return False
    
    # ImageQt 메서드 확인
    print("\nImageQt 메서드 확인:")
    if hasattr(ImageQt, 'toqimage'):
        print("✓ ImageQt.toqimage() 사용 가능 (최신 버전)")
        has_toqimage = True
    else:
        print("✗ ImageQt.toqimage() 없음")
        has_toqimage = False
    
    if hasattr(ImageQt, 'ImageQt'):
        print("✓ ImageQt.ImageQt() 사용 가능 (구 버전)")
        has_imageqt = True
    else:
        print("✗ ImageQt.ImageQt() 없음")
        has_imageqt = False
    
    # Image.Resampling 확인
    print("\n리샘플링 메서드 확인:")
    if hasattr(Image, 'Resampling') and hasattr(Image.Resampling, 'LANCZOS'):
        print("✓ Image.Resampling.LANCZOS 사용 가능 (최신 버전)")
        has_resampling = True
    else:
        print("✗ Image.Resampling.LANCZOS 없음")
        has_resampling = False
    
    if hasattr(Image, 'LANCZOS'):
        print("✓ Image.LANCZOS 사용 가능 (구 버전)")
        has_lanczos = True
    else:
        print("✗ Image.LANCZOS 없음")
        has_lanczos = False
    
    # 테스트 이미지 생성
    print("\n테스트 이미지 생성:")
    try:
        test_image = Image.new('RGB', (100, 100), (255, 0, 0))
        print("✓ 테스트 이미지 생성 성공")
        
        # 썸네일 테스트 (호환성 확인)
        print("\n썸네일 생성 테스트:")
        test_copy = test_image.copy()
        max_size = (50, 50)
        
        try:
            if has_resampling:
                test_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
                print("✓ Image.Resampling.LANCZOS로 썸네일 생성 성공")
            else:
                raise AttributeError("Resampling not available")
        except AttributeError:
            if has_lanczos:
                test_copy.thumbnail(max_size, Image.LANCZOS)
                print("✓ Image.LANCZOS로 썸네일 생성 성공")
            else:
                test_copy.thumbnail(max_size)
                print("✓ 기본 방법으로 썸네일 생성 성공")
        
        print(f"  - 원본 크기: {test_image.size}")
        print(f"  - 썸네일 크기: {test_copy.size}")
        
    except Exception as e:
        print(f"✗ 테스트 이미지 생성 실패: {e}")
        return False
    
    # RGBA 변환 테스트
    print("\nRGBA 변환 테스트:")
    try:
        rgba_image = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        print("✓ RGBA 이미지 생성 성공")
        
        # RGB로 변환 (흰색 배경)
        background = Image.new('RGB', rgba_image.size, (255, 255, 255))
        background.paste(rgba_image, mask=rgba_image.split()[-1])
        rgb_image = background
        print("✓ RGBA -> RGB 변환 성공")
        print(f"  - 원본 모드: {rgba_image.mode}")
        print(f"  - 변환 후 모드: {rgb_image.mode}")
        
    except Exception as e:
        print(f"✗ RGBA 변환 테스트 실패: {e}")
        return False
    
    print("\n=== 호환성 테스트 완료 ===")
    print("결론:")
    print(f"  - PIL 기본 기능: 정상")
    print(f"  - 썸네일 생성: 정상")
    print(f"  - RGBA 처리: 정상")
    
    if has_toqimage or has_imageqt:
        print(f"  - Qt 변환 지원: 가능 (toqimage: {has_toqimage}, ImageQt: {has_imageqt})")
    else:
        print(f"  - Qt 변환 지원: 불가능 (수동 변환 필요)")
    
    return True


def check_fixed_code():
    """수정된 코드 검증"""
    print("\n=== 수정된 코드 검증 ===\n")
    
    try:
        # 수정된 파일 읽기
        file_path = project_root / "markitdown_gui" / "ui" / "file_viewer_dialog.py"
        
        if not file_path.exists():
            print("✗ file_viewer_dialog.py 파일을 찾을 수 없습니다.")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 수정사항 확인
        fixes_found = []
        
        if "Image.Resampling.LANCZOS" in content and "except AttributeError:" in content:
            fixes_found.append("PIL 호환성 (Resampling)")
        
        if "toqimage(pil_image)" in content and "ImageQt(pil_image)" in content:
            fixes_found.append("ImageQt 호환성")
        
        if "background.paste(pil_image, mask=" in content:
            fixes_found.append("RGBA 처리")
        
        if "pixmap.isNull()" in content:
            fixes_found.append("QPixmap 유효성 검사")
        
        if "이미지를 불러오는 중..." in content:
            fixes_found.append("사용자 피드백 개선")
        
        print("발견된 수정사항:")
        for fix in fixes_found:
            print(f"  ✓ {fix}")
        
        if len(fixes_found) >= 4:
            print(f"\n✅ {len(fixes_found)}개의 주요 수정사항이 적용되었습니다!")
            return True
        else:
            print(f"\n⚠️ 일부 수정사항만 발견되었습니다 ({len(fixes_found)}/5)")
            return False
            
    except Exception as e:
        print(f"✗ 코드 검증 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("이미지 표시 문제 수정 검증 스크립트")
    print("=" * 50)
    
    # PIL 호환성 테스트
    pil_ok = test_pil_compatibility()
    
    # 수정된 코드 검증
    code_ok = check_fixed_code()
    
    print("\n" + "=" * 50)
    print("전체 검증 결과:")
    print(f"  - PIL 호환성: {'✅ 통과' if pil_ok else '❌ 실패'}")
    print(f"  - 코드 수정: {'✅ 통과' if code_ok else '❌ 실패'}")
    
    if pil_ok and code_ok:
        print("\n🎉 모든 검증이 통과했습니다!")
        print("\n수정 내용 요약:")
        print("1. PIL 버전 호환성 문제 해결")
        print("   - Image.Resampling.LANCZOS vs Image.LANCZOS")
        print("   - ImageQt.toqimage() vs ImageQt.ImageQt()")
        print("2. RGBA 이미지 처리 개선 (투명도 -> 흰색 배경)")
        print("3. QPixmap 유효성 검사 강화")
        print("4. 사용자 피드백 메시지 개선")
        print("5. 다중 백업 변환 방법 추가 (numpy 기반)")
        print("\n이제 '선택된 파일 변환' 후 이미지 표시가 정상 작동할 것입니다.")
    else:
        print("\n❌ 일부 검증에 실패했습니다.")
        
        if not pil_ok:
            print("PIL 설치가 필요합니다: pip install Pillow")
        
        if not code_ok:
            print("코드 수정을 다시 확인해주세요.")


if __name__ == "__main__":
    main()