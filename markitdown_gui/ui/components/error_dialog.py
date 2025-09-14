"""
Enhanced Error Dialog Component

User-friendly error dialog with technical details, recovery suggestions,
and integration with the comprehensive error handling system.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QTabWidget, QWidget, QScrollArea, QGroupBox, QListWidget, QListWidgetItem,
    QMessageBox, QProgressBar, QCheckBox, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QPixmap

from ...core.error_handling import (
    ErrorReport, ErrorSeverity, ConversionError, FontDescriptorError,
    PDFParsingError, RecoveryAction
)
from ...core.models import FileInfo


class ErrorDialog(QDialog):
    """Enhanced error dialog with comprehensive error information and actions"""
    
    # Signals
    retry_requested = pyqtSignal()
    ignore_error = pyqtSignal()
    apply_suggestion = pyqtSignal(str)  # Recovery suggestion
    export_logs = pyqtSignal()
    
    def __init__(self, error_report: ErrorReport, parent=None):
        super().__init__(parent)
        self.error_report = error_report
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.setMaximumSize(800, 700)
        
        self._init_ui()
        self._populate_content()
        self._setup_connections()
        
        # Auto-resize based on content
        self.adjustSize()
    
    def _init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Conversion Error")
        self.setWindowIcon(self._get_severity_icon())
        
        layout = QVBoxLayout(self)
        
        # Header section
        self._create_header_section(layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # User-friendly tab
        self._create_user_tab()
        
        # Technical details tab
        self._create_technical_tab()
        
        # Recovery suggestions tab
        self._create_recovery_tab()
        
        # Button section
        self._create_button_section(layout)
    
    def _get_severity_icon(self) -> QIcon:
        """Get icon based on error severity"""
        # In a real implementation, you would load appropriate icons
        if self.error_report.severity == ErrorSeverity.CRITICAL:
            return self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxCritical)
        elif self.error_report.severity == ErrorSeverity.ERROR:
            return self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxCritical)
        elif self.error_report.severity == ErrorSeverity.WARNING:
            return self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning)
        else:
            return self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation)
    
    def _create_header_section(self, layout: QVBoxLayout):
        """Create header with error title and severity"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Severity icon
        icon_label = QLabel()
        pixmap = self._get_severity_icon().pixmap(32, 32)
        icon_label.setPixmap(pixmap)
        header_layout.addWidget(icon_label)
        
        # Title and basic info
        info_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(self.error_report.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        info_layout.addWidget(title_label)
        
        # File path (if available)
        if self.error_report.file_path:
            file_label = QLabel(f"File: {self.error_report.file_path.name}")
            file_label.setStyleSheet("color: gray;")
            info_layout.addWidget(file_label)
        
        # Timestamp
        time_label = QLabel(f"Time: {self.error_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        time_label.setStyleSheet("color: gray; font-size: 10pt;")
        info_layout.addWidget(time_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addWidget(header_widget)
    
    def _create_user_tab(self):
        """Create user-friendly tab"""
        user_widget = QWidget()
        layout = QVBoxLayout(user_widget)
        
        # User message
        if self.error_report.user_message:
            message_group = QGroupBox("What happened?")
            message_layout = QVBoxLayout(message_group)
            
            message_label = QLabel(self.error_report.user_message)
            message_label.setWordWrap(True)
            message_label.setStyleSheet("padding: 10px; background: #f0f8ff; border: 1px solid #cce7ff;")
            message_layout.addWidget(message_label)
            
            layout.addWidget(message_group)
        
        # Quick recovery actions (if available)
        if self.error_report.recovery_suggestions:
            actions_group = QGroupBox("Quick Actions")
            actions_layout = QVBoxLayout(actions_group)
            
            # Show first few suggestions as buttons
            for i, suggestion in enumerate(self.error_report.recovery_suggestions[:3]):
                btn = QPushButton(suggestion)
                btn.clicked.connect(lambda checked, s=suggestion: self.apply_suggestion.emit(s))
                actions_layout.addWidget(btn)
            
            if len(self.error_report.recovery_suggestions) > 3:
                more_label = QLabel(f"+ {len(self.error_report.recovery_suggestions) - 3} more suggestions in Recovery tab")
                more_label.setStyleSheet("color: gray; font-style: italic;")
                actions_layout.addWidget(more_label)
            
            layout.addWidget(actions_group)
        
        # Error message (simplified for users)
        error_group = QGroupBox("Error Details")
        error_layout = QVBoxLayout(error_group)
        
        error_text = QTextEdit()
        error_text.setPlainText(self._get_user_friendly_message())
        error_text.setReadOnly(True)
        error_text.setMaximumHeight(150)
        error_layout.addWidget(error_text)
        
        layout.addWidget(error_group)
        
        layout.addStretch()
        self.tab_widget.addTab(user_widget, "Overview")
    
    def _create_technical_tab(self):
        """Create technical details tab"""
        tech_widget = QWidget()
        layout = QVBoxLayout(tech_widget)
        
        # Technical details
        details_group = QGroupBox("Technical Information")
        details_layout = QVBoxLayout(details_group)
        
        details_text = QTextEdit()
        details_text.setPlainText(self._format_technical_details())
        details_text.setReadOnly(True)
        details_text.setFont(QFont("Courier", 9))
        details_layout.addWidget(details_text)
        
        layout.addWidget(details_group)
        
        # Font-specific information (for FontDescriptorError)
        if self._is_font_error():
            font_group = QGroupBox("Font Issues")
            font_layout = QVBoxLayout(font_group)
            
            font_info = self._get_font_error_info()
            font_text = QTextEdit()
            font_text.setPlainText(font_info)
            font_text.setReadOnly(True)
            font_text.setMaximumHeight(200)
            font_layout.addWidget(font_text)
            
            layout.addWidget(font_group)
        
        self.tab_widget.addTab(tech_widget, "Technical")
    
    def _create_recovery_tab(self):
        """Create recovery suggestions tab"""
        recovery_widget = QWidget()
        layout = QVBoxLayout(recovery_widget)
        
        if self.error_report.recovery_suggestions:
            suggestions_group = QGroupBox("Recovery Suggestions")
            suggestions_layout = QVBoxLayout(suggestions_group)
            
            # List of all suggestions
            suggestions_list = QListWidget()
            
            for i, suggestion in enumerate(self.error_report.recovery_suggestions):
                item = QListWidgetItem(f"{i+1}. {suggestion}")
                suggestions_list.addItem(item)
            
            suggestions_layout.addWidget(suggestions_list)
            
            # Action buttons
            action_layout = QHBoxLayout()
            
            apply_btn = QPushButton("Apply Selected")
            apply_btn.clicked.connect(self._apply_selected_suggestion)
            action_layout.addWidget(apply_btn)
            
            action_layout.addStretch()
            suggestions_layout.addLayout(action_layout)
            
            layout.addWidget(suggestions_group)
            
            self.suggestions_list = suggestions_list
        else:
            no_suggestions_label = QLabel("No recovery suggestions available for this error.")
            no_suggestions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_suggestions_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
            layout.addWidget(no_suggestions_label)
        
        # Recovery actions (if this is a recoverable error)
        if self._is_recoverable_error():
            actions_group = QGroupBox("Automatic Recovery")
            actions_layout = QVBoxLayout(actions_group)
            
            recovery_label = QLabel("This error may be recoverable. The system can attempt to:")
            actions_layout.addWidget(recovery_label)
            
            # Checkboxes for recovery options
            self.retry_checkbox = QCheckBox("Retry original conversion")
            self.fallback_checkbox = QCheckBox("Use fallback conversion method")
            self.validate_checkbox = QCheckBox("Validate file before retry")
            
            actions_layout.addWidget(self.retry_checkbox)
            actions_layout.addWidget(self.fallback_checkbox)
            actions_layout.addWidget(self.validate_checkbox)
            
            # Set defaults based on error type
            if isinstance(self.error_report.technical_details.get("error_type"), str):
                error_type = self.error_report.technical_details["error_type"]
                if "FontDescriptor" in error_type:
                    self.fallback_checkbox.setChecked(True)
                elif "PDF" in error_type:
                    self.validate_checkbox.setChecked(True)
                else:
                    self.retry_checkbox.setChecked(True)
            
            layout.addWidget(actions_group)
        
        layout.addStretch()
        self.tab_widget.addTab(recovery_widget, "Recovery")
    
    def _create_button_section(self, layout: QVBoxLayout):
        """Create button section"""
        button_layout = QHBoxLayout()
        
        # Export logs button
        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs.emit)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        # Action buttons
        if self._is_recoverable_error():
            retry_btn = QPushButton("Retry")
            retry_btn.setDefault(True)
            retry_btn.clicked.connect(self.retry_requested.emit)
            button_layout.addWidget(retry_btn)
        
        ignore_btn = QPushButton("Ignore")
        ignore_btn.clicked.connect(self.ignore_error.emit)
        button_layout.addWidget(ignore_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Tab switching to technical details when user wants more info
        pass
    
    def _populate_content(self):
        """Populate dialog content based on error report"""
        # Set window title based on error type
        if self.error_report.error_code:
            self.setWindowTitle(f"Error: {self.error_report.error_code}")
    
    def _get_user_friendly_message(self) -> str:
        """Get user-friendly error message"""
        parts = []
        
        # Basic error message
        parts.append(self.error_report.message)
        
        # Add context if available
        if self.error_report.file_path:
            parts.append(f"\nFile: {self.error_report.file_path}")
        
        # Add specific error information
        if self._is_font_error():
            parts.append("\nThis appears to be a PDF font formatting issue that can usually be resolved using alternative conversion methods.")
        
        return "\n".join(parts)
    
    def _format_technical_details(self) -> str:
        """Format technical details for display"""
        details = []
        
        details.append(f"Error Code: {self.error_report.error_code or 'N/A'}")
        details.append(f"Severity: {self.error_report.severity.value.upper()}")
        details.append(f"Timestamp: {self.error_report.timestamp.isoformat()}")
        
        if self.error_report.file_path:
            details.append(f"File Path: {self.error_report.file_path}")
        
        details.append(f"\nRaw Error Message:\n{self.error_report.message}")
        
        if self.error_report.technical_details:
            details.append("\nTechnical Details:")
            for key, value in self.error_report.technical_details.items():
                if isinstance(value, dict):
                    details.append(f"  {key}:")
                    for k, v in value.items():
                        details.append(f"    {k}: {v}")
                elif isinstance(value, list):
                    details.append(f"  {key}: {len(value)} items")
                    for i, item in enumerate(value[:5]):  # Show first 5 items
                        details.append(f"    [{i}]: {item}")
                    if len(value) > 5:
                        details.append(f"    ... and {len(value) - 5} more")
                else:
                    details.append(f"  {key}: {value}")
        
        return "\n".join(details)
    
    def _is_font_error(self) -> bool:
        """Check if this is a font-related error"""
        if not self.error_report.technical_details:
            return False
        
        error_type = self.error_report.technical_details.get("error_type", "")
        return "FontDescriptor" in error_type or "font" in self.error_report.message.lower()
    
    def _get_font_error_info(self) -> str:
        """Get font-specific error information"""
        if not self.error_report.technical_details:
            return "No font-specific information available."
        
        details = self.error_report.technical_details
        info_parts = []
        
        if "font_name" in details:
            info_parts.append(f"Font Name: {details['font_name']}")
        
        if "bbox_value" in details:
            info_parts.append(f"FontBBox Value: {details['bbox_value']}")
        
        if "font_issues" in details and isinstance(details["font_issues"], list):
            info_parts.append(f"\nFont Issues ({len(details['font_issues'])}):")
            for i, issue in enumerate(details["font_issues"][:10]):  # Show first 10
                if isinstance(issue, dict):
                    issue_type = issue.get("issue_type", "unknown")
                    font_name = issue.get("font_name", "unknown")
                    info_parts.append(f"  {i+1}. {issue_type} in {font_name}")
                else:
                    info_parts.append(f"  {i+1}. {issue}")
        
        info_parts.append("\nRecommended Actions:")
        info_parts.append("• Try using basic text extraction mode")
        info_parts.append("• Use OCR-based conversion if the PDF contains scanned text")
        info_parts.append("• Consider repairing the PDF using specialized tools")
        
        return "\n".join(info_parts) if info_parts else "No detailed font information available."
    
    def _is_recoverable_error(self) -> bool:
        """Check if this is a recoverable error"""
        if not self.error_report.technical_details:
            return True  # Assume recoverable if no details
        
        error_type = self.error_report.technical_details.get("error_type", "")
        return "Unrecoverable" not in error_type
    
    def _apply_selected_suggestion(self):
        """Apply the selected recovery suggestion"""
        if hasattr(self, 'suggestions_list'):
            current_item = self.suggestions_list.currentItem()
            if current_item:
                # Extract suggestion text (remove numbering)
                suggestion_text = current_item.text()
                if ". " in suggestion_text:
                    suggestion = suggestion_text.split(". ", 1)[1]
                    self.apply_suggestion.emit(suggestion)


class ErrorReportViewer(QDialog):
    """Dialog for viewing multiple error reports"""
    
    def __init__(self, error_reports: List[ErrorReport], parent=None):
        super().__init__(parent)
        self.error_reports = error_reports
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setWindowTitle("Error Reports")
        
        self._init_ui()
        self._populate_reports()
    
    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Summary section
        summary_layout = QHBoxLayout()
        
        total_label = QLabel(f"Total Errors: {len(self.error_reports)}")
        summary_layout.addWidget(total_label)
        
        # Count by severity
        severity_counts = {}
        for report in self.error_reports:
            severity_counts[report.severity] = severity_counts.get(report.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            severity_label = QLabel(f"{severity.value.title()}: {count}")
            if severity == ErrorSeverity.CRITICAL:
                severity_label.setStyleSheet("color: red; font-weight: bold;")
            elif severity == ErrorSeverity.ERROR:
                severity_label.setStyleSheet("color: red;")
            elif severity == ErrorSeverity.WARNING:
                severity_label.setStyleSheet("color: orange;")
            
            summary_layout.addWidget(severity_label)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Reports list
        self.reports_list = QListWidget()
        layout.addWidget(self.reports_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Selected")
        view_btn.clicked.connect(self._view_selected_report)
        button_layout.addWidget(view_btn)
        
        export_btn = QPushButton("Export All")
        export_btn.clicked.connect(self._export_reports)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_reports(self):
        """Populate the reports list"""
        for i, report in enumerate(self.error_reports):
            # Create summary text
            file_name = report.file_path.name if report.file_path else "Unknown file"
            summary_text = f"[{report.severity.value.upper()}] {report.title} - {file_name}"
            
            item = QListWidgetItem(summary_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # Store report index
            
            # Set item color based on severity
            if report.severity == ErrorSeverity.CRITICAL:
                item.setForeground(Qt.GlobalColor.red)
            elif report.severity == ErrorSeverity.ERROR:
                item.setForeground(Qt.GlobalColor.darkRed)
            elif report.severity == ErrorSeverity.WARNING:
                item.setForeground(Qt.GlobalColor.darkYellow)
            
            self.reports_list.addItem(item)
    
    def _view_selected_report(self):
        """View the selected error report in detail"""
        current_item = self.reports_list.currentItem()
        if current_item:
            report_index = current_item.data(Qt.ItemDataRole.UserRole)
            report = self.error_reports[report_index]
            
            # Show detailed error dialog
            error_dialog = ErrorDialog(report, self)
            error_dialog.exec()
    
    def _export_reports(self):
        """Export all error reports"""
        # This would integrate with the error reporter's export functionality
        QMessageBox.information(self, "Export", 
                              f"Exported {len(self.error_reports)} error reports to logs/error_reports.json")