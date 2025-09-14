"""
System Theme Detection
Cross-platform system theme detection for Windows, macOS, and Linux
"""

import os
import sys
import platform
import subprocess
from typing import Optional
from pathlib import Path

from .logger import get_logger


logger = get_logger(__name__)


class SystemThemeDetector:
    """시스템 테마 감지 클래스"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self._last_detected_theme = None
        
        # 시스템별 초기화
        if self.system == "windows":
            self._init_windows()
        elif self.system == "darwin":
            self._init_macos()
        elif self.system == "linux":
            self._init_linux()
        else:
            logger.warning(f"Unsupported system for theme detection: {self.system}")
    
    def _init_windows(self):
        """Windows 시스템 초기화"""
        try:
            # Windows Registry 접근을 위한 winreg 모듈 확인
            import winreg
            self._winreg = winreg
            logger.debug("Windows theme detection initialized")
        except ImportError:
            logger.warning("winreg module not available, Windows theme detection disabled")
            self._winreg = None
    
    def _init_macos(self):
        """macOS 시스템 초기화"""
        logger.debug("macOS theme detection initialized")
    
    def _init_linux(self):
        """Linux 시스템 초기화"""
        # 일반적인 Linux 데스크톱 환경들 확인
        self.desktop_env = self._detect_linux_desktop_environment()
        logger.debug(f"Linux theme detection initialized for: {self.desktop_env}")
    
    def _detect_linux_desktop_environment(self) -> str:
        """Linux 데스크톱 환경 감지"""
        # 환경 변수들로 데스크톱 환경 판단
        desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
        xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        # GNOME
        if 'gnome' in desktop_session or 'gnome' in xdg_current_desktop:
            return 'gnome'
        
        # KDE
        if 'kde' in desktop_session or 'kde' in xdg_current_desktop:
            return 'kde'
        
        # XFCE
        if 'xfce' in desktop_session or 'xfce' in xdg_current_desktop:
            return 'xfce'
        
        # Ubuntu (Unity/GNOME)
        if 'ubuntu' in desktop_session:
            return 'ubuntu'
        
        # Cinnamon
        if 'cinnamon' in desktop_session:
            return 'cinnamon'
        
        # MATE
        if 'mate' in desktop_session:
            return 'mate'
        
        return 'unknown'
    
    def get_system_theme(self):
        """
        현재 시스템 테마 감지
        
        Returns:
            'dark' 또는 'light'
        """
        try:
            if self.system == "windows":
                return self._get_windows_theme()
            elif self.system == "darwin":
                return self._get_macos_theme()
            elif self.system == "linux":
                return self._get_linux_theme()
            else:
                logger.warning(f"Theme detection not implemented for: {self.system}")
                return "light"  # Default fallback
                
        except Exception as e:
            logger.error(f"Error detecting system theme: {e}")
            return "light"  # Default fallback
    
    def _get_windows_theme(self) -> str:
        """Windows 시스템 테마 감지"""
        if not self._winreg:
            return "light"
        
        try:
            # Windows 10/11 테마 설정 확인
            # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            
            with self._winreg.OpenKey(self._winreg.HKEY_CURRENT_USER, key_path) as key:
                # AppsUseLightTheme 값 확인 (0 = dark, 1 = light)
                try:
                    apps_use_light_theme, _ = self._winreg.QueryValueEx(key, "AppsUseLightTheme")
                    theme = "light" if apps_use_light_theme else "dark"
                    logger.debug(f"Windows theme detected: {theme}")
                    return theme
                except FileNotFoundError:
                    # Windows 8.1 이하에서는 해당 키가 없을 수 있음
                    pass
                
                # SystemUsesLightTheme도 확인
                try:
                    system_use_light_theme, _ = self._winreg.QueryValueEx(key, "SystemUsesLightTheme")
                    theme = "light" if system_use_light_theme else "dark"
                    logger.debug(f"Windows system theme detected: {theme}")
                    return theme
                except FileNotFoundError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error reading Windows registry for theme: {e}")
        
        return "light"  # Default fallback
    
    def _get_macos_theme(self) -> str:
        """macOS 시스템 테마 감지"""
        try:
            # macOS의 defaults 명령어를 사용하여 테마 확인
            result = subprocess.run([
                "defaults", "read", "-g", "AppleInterfaceStyle"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # AppleInterfaceStyle이 "Dark"면 다크 모드
                interface_style = result.stdout.strip()
                theme = "dark" if interface_style.lower() == "dark" else "light"
                logger.debug(f"macOS theme detected: {theme}")
                return theme
            else:
                # AppleInterfaceStyle 키가 없으면 라이트 모드 (기본값)
                logger.debug("macOS light theme detected (default)")
                return "light"
                
        except subprocess.TimeoutExpired:
            logger.warning("macOS theme detection timed out")
        except FileNotFoundError:
            logger.warning("defaults command not found on macOS")
        except Exception as e:
            logger.error(f"Error detecting macOS theme: {e}")
        
        return "light"  # Default fallback
    
    def _get_linux_theme(self) -> str:
        """Linux 시스템 테마 감지"""
        if self.desktop_env == 'gnome' or self.desktop_env == 'ubuntu':
            return self._get_gnome_theme()
        elif self.desktop_env == 'kde':
            return self._get_kde_theme()
        elif self.desktop_env == 'xfce':
            return self._get_xfce_theme()
        else:
            # 일반적인 방법들 시도
            return self._get_generic_linux_theme()
    
    def _get_gnome_theme(self) -> str:
        """GNOME/Ubuntu 테마 감지"""
        try:
            # GNOME의 gsettings를 사용하여 테마 확인
            result = subprocess.run([
                "gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                theme_name = result.stdout.strip().strip("'\"").lower()
                
                # 일반적인 다크 테마 이름들 확인
                dark_themes = ['adwaita-dark', 'yaru-dark', 'pop-dark', 'arc-dark', 'breeze-dark']
                
                if any(dark in theme_name for dark in dark_themes):
                    logger.debug(f"GNOME dark theme detected: {theme_name}")
                    return "dark"
                else:
                    logger.debug(f"GNOME light theme detected: {theme_name}")
                    return "light"
            
            # Ubuntu 20.04+에서 색상 스키마 확인
            result = subprocess.run([
                "gsettings", "get", "org.gnome.desktop.interface", "color-scheme"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                color_scheme = result.stdout.strip().strip("'\"").lower()
                if 'dark' in color_scheme:
                    logger.debug(f"GNOME dark color scheme detected: {color_scheme}")
                    return "dark"
                    
        except subprocess.TimeoutExpired:
            logger.warning("GNOME theme detection timed out")
        except FileNotFoundError:
            logger.warning("gsettings command not found")
        except Exception as e:
            logger.error(f"Error detecting GNOME theme: {e}")
        
        return "light"  # Default fallback
    
    def _get_kde_theme(self) -> str:
        """KDE 테마 감지"""
        try:
            # KDE의 설정 파일들 확인
            home = Path.home()
            
            # KDE 5/Plasma 5 설정
            kde_config_paths = [
                home / ".config" / "kdeglobals",
                home / ".kde4" / "share" / "config" / "kdeglobals",
                home / ".kde" / "share" / "config" / "kdeglobals"
            ]
            
            for config_path in kde_config_paths:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        content = f.read().lower()
                        
                        # 다크 테마 키워드들 확인
                        if any(keyword in content for keyword in ['breeze dark', 'oxygen dark', 'adwaita-dark']):
                            logger.debug(f"KDE dark theme detected in {config_path}")
                            return "dark"
                        
                        # 색상 스키마 확인
                        if 'colorscheme=breezedark' in content.replace(' ', ''):
                            logger.debug(f"KDE dark color scheme detected in {config_path}")
                            return "dark"
            
            # kreadconfig5 명령어 사용 시도
            result = subprocess.run([
                "kreadconfig5", "--group", "General", "--key", "ColorScheme"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                color_scheme = result.stdout.strip().lower()
                if 'dark' in color_scheme:
                    logger.debug(f"KDE dark color scheme detected: {color_scheme}")
                    return "dark"
                    
        except subprocess.TimeoutExpired:
            logger.warning("KDE theme detection timed out")
        except FileNotFoundError:
            logger.debug("kreadconfig5 command not found")
        except Exception as e:
            logger.error(f"Error detecting KDE theme: {e}")
        
        return "light"  # Default fallback
    
    def _get_xfce_theme(self) -> str:
        """XFCE 테마 감지"""
        try:
            # XFCE 설정 파일 확인
            home = Path.home()
            xfce_config = home / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml" / "xsettings.xml"
            
            if xfce_config.exists():
                with open(xfce_config, 'r') as f:
                    content = f.read().lower()
                    
                    # 다크 테마 확인
                    if any(keyword in content for keyword in ['adwaita-dark', 'arc-dark', 'greybird-dark']):
                        logger.debug("XFCE dark theme detected")
                        return "dark"
            
            # xfconf-query 명령어 사용 시도
            result = subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                theme_name = result.stdout.strip().lower()
                if 'dark' in theme_name:
                    logger.debug(f"XFCE dark theme detected: {theme_name}")
                    return "dark"
                    
        except subprocess.TimeoutExpired:
            logger.warning("XFCE theme detection timed out")
        except FileNotFoundError:
            logger.debug("xfconf-query command not found")
        except Exception as e:
            logger.error(f"Error detecting XFCE theme: {e}")
        
        return "light"  # Default fallback
    
    def _get_generic_linux_theme(self) -> str:
        """일반적인 Linux 테마 감지 방법들"""
        try:
            # GTK 설정 파일들 확인
            home = Path.home()
            
            # GTK-3 설정
            gtk3_config = home / ".config" / "gtk-3.0" / "settings.ini"
            if gtk3_config.exists():
                with open(gtk3_config, 'r') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in ['adwaita-dark', 'arc-dark', 'breeze-dark']):
                        logger.debug("Linux dark theme detected in GTK-3 config")
                        return "dark"
            
            # GTK-2 설정
            gtk2_config = home / ".gtkrc-2.0"
            if gtk2_config.exists():
                with open(gtk2_config, 'r') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in ['adwaita-dark', 'arc-dark', 'breeze-dark']):
                        logger.debug("Linux dark theme detected in GTK-2 config")
                        return "dark"
            
            # 환경 변수 확인
            gtk_theme = os.environ.get('GTK_THEME', '').lower()
            if 'dark' in gtk_theme:
                logger.debug(f"Linux dark theme detected in GTK_THEME env var: {gtk_theme}")
                return "dark"
                
        except Exception as e:
            logger.error(f"Error in generic Linux theme detection: {e}")
        
        return "light"  # Default fallback
    
    def is_theme_changed(self) -> bool:
        """
        테마가 변경되었는지 확인
        
        Returns:
            테마 변경 여부
        """
        current_theme = self.get_system_theme()
        if current_theme != self._last_detected_theme:
            self._last_detected_theme = current_theme
            return True
        return False
    
    def supports_theme_detection(self) -> bool:
        """
        현재 시스템에서 테마 감지를 지원하는지 확인
        
        Returns:
            지원 여부
        """
        if self.system == "windows":
            return self._winreg is not None
        elif self.system == "darwin":
            return True  # macOS는 기본 지원
        elif self.system == "linux":
            return True  # Linux는 기본 지원 (다양한 방법 시도)
        else:
            return False