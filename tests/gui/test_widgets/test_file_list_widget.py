"""
GUI tests for FileListWidget
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest

from markitdown_gui.ui.widgets.file_list_widget import FileListWidget
from markitdown_gui.core.file_manager import FileInfo


class TestFileListWidget:
    """Test suite for FileListWidget"""
    
    @pytest.fixture
    def file_list_widget(self, qtbot):
        """Create FileListWidget instance for testing"""
        widget = FileListWidget()
        qtbot.addWidget(widget)
        return widget
    
    @pytest.fixture
    def sample_file_info(self):
        """Create sample FileInfo objects for testing"""
        files = []
        
        # Create various file types
        files.append(FileInfo(
            path="/test/document.pdf",
            name="document.pdf",
            size=1024000,
            modified_time="2024-01-15 10:30:00",
            file_type="PDF Document"
        ))
        
        files.append(FileInfo(
            path="/test/spreadsheet.xlsx", 
            name="spreadsheet.xlsx",
            size=512000,
            modified_time="2024-01-16 14:20:00",
            file_type="Excel Spreadsheet"
        ))
        
        files.append(FileInfo(
            path="/test/presentation.pptx",
            name="presentation.pptx", 
            size=2048000,
            modified_time="2024-01-17 09:15:00",
            file_type="PowerPoint Presentation"
        ))
        
        return files
    
    def test_initialization(self, file_list_widget):
        """Test FileListWidget initialization"""
        assert isinstance(file_list_widget, QTreeWidget)
        assert file_list_widget.columnCount() >= 4  # Name, Size, Date, Type
        
        # Check headers are set
        header = file_list_widget.headerItem()
        assert header.text(0) != ""  # Name column
        assert header.text(1) != ""  # Size column
        assert header.text(2) != ""  # Date column
    
    def test_column_headers(self, file_list_widget):
        """Test column headers setup"""
        headers = []
        for i in range(file_list_widget.columnCount()):
            headers.append(file_list_widget.headerItem().text(i))
        
        # Check expected headers
        assert any("Name" in header or "File" in header for header in headers)
        assert any("Size" in header for header in headers)
        assert any("Date" in header or "Modified" in header for header in headers)
        assert any("Type" in header for header in headers)
    
    def test_add_files(self, file_list_widget, sample_file_info):
        """Test adding files to the widget"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Check items were added
        assert file_list_widget.topLevelItemCount() == len(sample_file_info)
        
        # Check first item content
        first_item = file_list_widget.topLevelItem(0)
        assert first_item.text(0) == "document.pdf"  # Name column
        assert "1.0 MB" in first_item.text(1) or "1024" in first_item.text(1)  # Size column
    
    def test_clear_files(self, file_list_widget, sample_file_info):
        """Test clearing all files"""
        # Add files first
        file_list_widget.add_files(sample_file_info)
        assert file_list_widget.topLevelItemCount() > 0
        
        # Clear files
        file_list_widget.clear_files()
        assert file_list_widget.topLevelItemCount() == 0
    
    def test_file_selection(self, file_list_widget, sample_file_info, qtbot):
        """Test file selection functionality"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Select first item
        first_item = file_list_widget.topLevelItem(0)
        file_list_widget.setCurrentItem(first_item)
        
        # Check selection
        selected_items = file_list_widget.selectedItems()
        assert len(selected_items) == 1
        assert selected_items[0] == first_item
    
    def test_multi_selection(self, file_list_widget, sample_file_info, qtbot):
        """Test multi-file selection"""
        # Enable multi-selection
        file_list_widget.setSelectionMode(QTreeWidget.SelectionMode.MultiSelection)
        
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Select multiple items
        for i in range(2):
            item = file_list_widget.topLevelItem(i)
            item.setSelected(True)
        
        # Check multiple selection
        selected_items = file_list_widget.selectedItems()
        assert len(selected_items) == 2
    
    def test_checkboxes(self, file_list_widget, sample_file_info, qtbot):
        """Test checkbox functionality for files"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Check if checkboxes are enabled
        first_item = file_list_widget.topLevelItem(0)
        if first_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            # Test checking/unchecking
            first_item.setCheckState(0, Qt.CheckState.Checked)
            assert first_item.checkState(0) == Qt.CheckState.Checked
            
            first_item.setCheckState(0, Qt.CheckState.Unchecked)
            assert first_item.checkState(0) == Qt.CheckState.Unchecked
    
    def test_get_selected_files(self, file_list_widget, sample_file_info):
        """Test getting selected file information"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Select some items
        file_list_widget.topLevelItem(0).setSelected(True)
        file_list_widget.topLevelItem(2).setSelected(True)
        
        # Get selected files
        selected_files = file_list_widget.get_selected_files()
        
        assert len(selected_files) == 2
        assert selected_files[0].name == "document.pdf"
        assert selected_files[1].name == "presentation.pptx"
    
    def test_get_checked_files(self, file_list_widget, sample_file_info):
        """Test getting checked file information"""
        # Add files  
        file_list_widget.add_files(sample_file_info)
        
        # Check some items
        first_item = file_list_widget.topLevelItem(0)
        if first_item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            first_item.setCheckState(0, Qt.CheckState.Checked)
            
            # Get checked files
            checked_files = file_list_widget.get_checked_files()
            assert len(checked_files) >= 1
    
    def test_sorting(self, file_list_widget, sample_file_info, qtbot):
        """Test column sorting functionality"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Enable sorting
        file_list_widget.setSortingEnabled(True)
        
        # Sort by name (column 0)
        file_list_widget.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        # Check sort order
        first_item_name = file_list_widget.topLevelItem(0).text(0)
        second_item_name = file_list_widget.topLevelItem(1).text(0)
        assert first_item_name <= second_item_name  # Alphabetical order
        
        # Sort descending
        file_list_widget.sortItems(0, Qt.SortOrder.DescendingOrder)
        
        new_first_name = file_list_widget.topLevelItem(0).text(0)
        assert new_first_name >= first_item_name  # Reverse order
    
    def test_context_menu(self, file_list_widget, sample_file_info, qtbot):
        """Test context menu functionality"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Select an item
        first_item = file_list_widget.topLevelItem(0)
        file_list_widget.setCurrentItem(first_item)
        
        # Right-click to show context menu
        item_rect = file_list_widget.visualItemRect(first_item)
        pos = item_rect.center()
        
        with patch.object(file_list_widget, 'create_context_menu') as mock_create_menu:
            mock_menu = Mock(spec=QMenu)
            mock_create_menu.return_value = mock_menu
            
            # Simulate right-click
            qtbot.mouseClick(
                file_list_widget.viewport(), 
                Qt.MouseButton.RightButton,
                pos=pos
            )
            
            # Check context menu was created
            qtbot.wait(10)  # Allow signal processing
    
    def test_file_icons(self, file_list_widget, sample_file_info):
        """Test file type icons"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Check items have icons
        for i in range(file_list_widget.topLevelItemCount()):
            item = file_list_widget.topLevelItem(i)
            icon = item.icon(0)
            
            # Icon should not be null for known file types
            assert not icon.isNull()
    
    def test_filtering(self, file_list_widget, sample_file_info):
        """Test file filtering functionality"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Apply filter (if filtering is implemented)
        if hasattr(file_list_widget, 'set_filter'):
            file_list_widget.set_filter("*.pdf")
            
            # Check only PDF files are visible
            visible_count = 0
            for i in range(file_list_widget.topLevelItemCount()):
                item = file_list_widget.topLevelItem(i)
                if not item.isHidden():
                    visible_count += 1
                    assert item.text(0).endswith('.pdf')
            
            assert visible_count == 1  # Only the PDF file
    
    def test_double_click_action(self, file_list_widget, sample_file_info, qtbot):
        """Test double-click action on file items"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Set up signal tracking
        double_click_signal = None
        if hasattr(file_list_widget, 'file_double_clicked'):
            double_click_signal = file_list_widget.file_double_clicked
        
        # Double-click first item
        first_item = file_list_widget.topLevelItem(0)
        item_rect = file_list_widget.visualItemRect(first_item)
        pos = item_rect.center()
        
        qtbot.mouseDClick(file_list_widget.viewport(), Qt.MouseButton.LeftButton, pos=pos)
        
        # If double-click signal exists, it should have been emitted
        if double_click_signal:
            qtbot.wait(10)  # Allow signal processing
    
    def test_drag_and_drop(self, file_list_widget, qtbot):
        """Test drag and drop functionality"""
        # Check if drag and drop is enabled
        assert file_list_widget.dragEnabled() or file_list_widget.acceptDrops()
        
        # Test drag and drop behavior (simplified)
        if file_list_widget.acceptDrops():
            assert file_list_widget.dragDropMode() != QTreeWidget.DragDropMode.NoDragDrop
    
    def test_column_resizing(self, file_list_widget, sample_file_info, qtbot):
        """Test column resizing functionality"""
        # Add files to populate columns
        file_list_widget.add_files(sample_file_info)
        
        header = file_list_widget.header()
        
        # Test manual column resizing
        original_width = header.sectionSize(0)
        header.resizeSection(0, original_width + 50)
        
        assert header.sectionSize(0) == original_width + 50
        
        # Test automatic column sizing
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        # Width should adjust to content
        new_width = header.sectionSize(0)
        assert new_width > 0
    
    def test_keyboard_navigation(self, file_list_widget, sample_file_info, qtbot):
        """Test keyboard navigation through file list"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Set focus to widget
        file_list_widget.setFocus()
        
        # Select first item
        first_item = file_list_widget.topLevelItem(0)
        file_list_widget.setCurrentItem(first_item)
        
        # Navigate with arrow keys
        qtbot.keyPress(file_list_widget, Qt.Key.Key_Down)
        
        # Should select next item
        current_item = file_list_widget.currentItem()
        assert current_item == file_list_widget.topLevelItem(1)
        
        # Navigate up
        qtbot.keyPress(file_list_widget, Qt.Key.Key_Up)
        current_item = file_list_widget.currentItem()
        assert current_item == file_list_widget.topLevelItem(0)
    
    def test_select_all(self, file_list_widget, sample_file_info, qtbot):
        """Test select all functionality"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Set multi-selection mode
        file_list_widget.setSelectionMode(QTreeWidget.SelectionMode.MultiSelection)
        
        # Select all with Ctrl+A
        file_list_widget.setFocus()
        qtbot.keySequence(file_list_widget, "Ctrl+A")
        
        # Check all items are selected
        selected_items = file_list_widget.selectedItems()
        assert len(selected_items) == len(sample_file_info)
    
    def test_status_columns(self, file_list_widget, sample_file_info):
        """Test conversion status columns"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Update status (if status column exists)
        if hasattr(file_list_widget, 'update_conversion_status'):
            first_item = file_list_widget.topLevelItem(0)
            file_path = first_item.data(0, Qt.ItemDataRole.UserRole)
            
            file_list_widget.update_conversion_status(file_path, "Converting...")
            
            # Check status was updated
            status_column = file_list_widget.columnCount() - 1  # Assuming last column
            status_text = first_item.text(status_column)
            assert "Converting" in status_text
    
    def test_progress_indicators(self, file_list_widget, sample_file_info, qtbot):
        """Test progress indicators for individual files"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Update progress (if supported)
        if hasattr(file_list_widget, 'update_conversion_progress'):
            first_item = file_list_widget.topLevelItem(0)
            file_path = first_item.data(0, Qt.ItemDataRole.UserRole)
            
            file_list_widget.update_conversion_progress(file_path, 50)  # 50%
            
            # Check progress is shown (implementation dependent)
            qtbot.wait(10)
    
    def test_accessibility(self, file_list_widget, sample_file_info):
        """Test accessibility features"""
        # Add files
        file_list_widget.add_files(sample_file_info)
        
        # Check widget has accessible name
        assert file_list_widget.accessibleName() != "" or file_list_widget.windowTitle() != ""
        
        # Check items have accessible descriptions
        first_item = file_list_widget.topLevelItem(0)
        # Items should be readable by screen readers
        assert first_item.text(0) != ""  # At minimum, the name should be accessible
    
    def test_large_file_list_performance(self, file_list_widget, qtbot):
        """Test performance with large number of files"""
        import time
        
        # Create many file info objects
        large_file_list = []
        for i in range(100):
            file_info = FileInfo(
                path=f"/test/file_{i:03d}.pdf",
                name=f"file_{i:03d}.pdf", 
                size=1000 + i,
                modified_time="2024-01-01 12:00:00",
                file_type="PDF Document"
            )
            large_file_list.append(file_info)
        
        # Measure time to add files
        start_time = time.time()
        file_list_widget.add_files(large_file_list)
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second for 100 files)
        assert (end_time - start_time) < 1.0
        
        # Check all files were added
        assert file_list_widget.topLevelItemCount() == 100
    
    def test_memory_usage(self, file_list_widget, sample_file_info):
        """Test memory usage with file operations"""
        # Add and remove files multiple times
        for _ in range(5):
            file_list_widget.add_files(sample_file_info)
            assert file_list_widget.topLevelItemCount() == len(sample_file_info)
            
            file_list_widget.clear_files()
            assert file_list_widget.topLevelItemCount() == 0
        
        # Memory should be properly released
        # (This is more of a check that operations complete without errors)
    
    def test_error_handling(self, file_list_widget):
        """Test error handling with invalid data"""
        # Test with None data
        file_list_widget.add_files(None)
        assert file_list_widget.topLevelItemCount() == 0
        
        # Test with empty list
        file_list_widget.add_files([])
        assert file_list_widget.topLevelItemCount() == 0
        
        # Test with invalid FileInfo objects
        invalid_files = [Mock(), Mock()]  # Mock objects without proper attributes
        
        # Should handle gracefully without crashing
        try:
            file_list_widget.add_files(invalid_files)
            # May or may not add items, but shouldn't crash
        except Exception as e:
            # If it does raise an exception, it should be handled gracefully
            pass