import unittest
import os
import csv
import tempfile
import shutil
from unittest.mock import patch, mock_open
from datetime import datetime
import sys

# Add the current directory to the path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with the correct module name
try:
    from main import (
        ensure_data_directory_exists,
        initialize_data_file,
        save_daily_log,
        load_all_logs,
        get_user_input,
        record_daily_entry,
        DATA_DIR,
        DATA_FILE,
        HEADERS
    )
except ImportError:
    # Try importing as 'Python main' if direct import fails
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", "Python main.py")
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    
    ensure_data_directory_exists = main_module.ensure_data_directory_exists
    initialize_data_file = main_module.initialize_data_file
    save_daily_log = main_module.save_daily_log
    load_all_logs = main_module.load_all_logs
    get_user_input = main_module.get_user_input
    record_daily_entry = main_module.record_daily_entry
    DATA_DIR = main_module.DATA_DIR
    DATA_FILE = main_module.DATA_FILE
    HEADERS = main_module.HEADERS

class TestHabitTrackerAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_data_dir = DATA_DIR
        self.original_data_file = DATA_FILE
        
        # Create test paths
        self.test_data_dir = os.path.join(self.test_dir, 'data')
        self.test_data_file = os.path.join(self.test_data_dir, 'daily_log.csv')
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_ensure_data_directory_exists_creates_directory(self):
        """Test that ensure_data_directory_exists creates the data directory."""
        with patch('main.DATA_DIR', self.test_data_dir):
            ensure_data_directory_exists()
            self.assertTrue(os.path.exists(self.test_data_dir))
    
    def test_ensure_data_directory_exists_directory_already_exists(self):
        """Test that ensure_data_directory_exists handles existing directory."""
        os.makedirs(self.test_data_dir)
        
        with patch('main.DATA_DIR', self.test_data_dir):
            # Should not raise an exception
            ensure_data_directory_exists()
            self.assertTrue(os.path.exists(self.test_data_dir))
    
    def test_initialize_data_file_creates_file_with_headers(self):
        """Test that initialize_data_file creates CSV file with proper headers."""
        with patch('main.DATA_DIR', self.test_data_dir), \
             patch('main.DATA_FILE', self.test_data_file):
            
            initialize_data_file()
            
            # Check file exists
            self.assertTrue(os.path.exists(self.test_data_file))
            
            # Check headers are correct
            with open(self.test_data_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                self.assertEqual(headers, HEADERS)
    
    def test_initialize_data_file_existing_file(self):
        """Test that initialize_data_file doesn't overwrite existing file."""
        os.makedirs(self.test_data_dir)
        
        # Create existing file with some content
        with open(self.test_data_file, 'w', encoding='utf-8') as f:
            f.write('existing,content\n')
        
        with patch('main.DATA_DIR', self.test_data_dir), \
             patch('main.DATA_FILE', self.test_data_file):
            
            initialize_data_file()
            
            # Check file still contains original content
            with open(self.test_data_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('existing,content', content)
    
    def test_save_daily_log_valid_entry(self):
        """Test saving a valid daily log entry."""
        log_entry = {
            'LogDate': '2024-01-15',
            'MoodRating': '8',
            'HadExercise': 'Yes',
            'GotEnoughSleep': 'Yes',
            'HadSocialInteraction': 'No',
            'AteHealthy': 'Yes',
            'Notes': 'Great day!'
        }
        
        with patch('main.DATA_DIR', self.test_data_dir), \
             patch('main.DATA_FILE', self.test_data_file):
            
            save_daily_log(log_entry)
            
            # Verify file exists and contains the entry
            self.assertTrue(os.path.exists(self.test_data_file))
            
            with open(self.test_data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['LogDate'], '2024-01-15')
                self.assertEqual(rows[0]['MoodRating'], '8')
    
    def test_load_all_logs_empty_file(self):
        """Test loading logs when file doesn't exist."""
        nonexistent_file = os.path.join(self.test_dir, 'nonexistent.csv')
        
        with patch('main.DATA_FILE', nonexistent_file):
            logs = load_all_logs()
            self.assertEqual(logs, [])
    
    def test_load_all_logs_with_data(self):
        """Test loading logs from file with data."""
        os.makedirs(self.test_data_dir)
        
        # Create test data
        test_data = [
            ['LogDate', 'MoodRating', 'HadExercise', 'GotEnoughSleep', 'HadSocialInteraction', 'AteHealthy', 'Notes'],
            ['2024-01-15', '8', 'Yes', 'Yes', 'No', 'Yes', 'Great day!'],
            ['2024-01-16', '6', 'No', 'Yes', 'Yes', 'No', 'Okay day']
        ]
        
        with open(self.test_data_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(test_data)
        
        with patch('main.DATA_FILE', self.test_data_file):
            logs = load_all_logs()
            self.assertEqual(len(logs), 2)
            self.assertEqual(logs[0]['LogDate'], '2024-01-15')
            self.assertEqual(logs[1]['MoodRating'], '6')
    
    @patch('builtins.input', return_value='5')
    def test_get_user_input_valid_integer(self, mock_input):
        """Test get_user_input with valid integer input."""
        result = get_user_input("Enter number: ", int)
        self.assertEqual(result, 5)
    
    @patch('builtins.input', side_effect=['invalid', '7'])
    def test_get_user_input_invalid_then_valid(self, mock_input):
        """Test get_user_input with invalid input followed by valid input."""
        result = get_user_input("Enter number: ", int)
        self.assertEqual(result, 7)
    
    @patch('builtins.input', return_value='yes')
    def test_get_user_input_valid_options(self, mock_input):
        """Test get_user_input with valid options constraint."""
        result = get_user_input("Choose: ", str, ['yes', 'no'])
        self.assertEqual(result, 'yes')
    
    @patch('builtins.input', side_effect=['maybe', 'no'])
    def test_get_user_input_invalid_option_then_valid(self, mock_input):
        """Test get_user_input with invalid option followed by valid option."""
        result = get_user_input("Choose: ", str, ['yes', 'no'])
        self.assertEqual(result, 'no')
    
    @patch('main.get_user_input')
    @patch('main.save_daily_log')
    def test_record_daily_entry_integration(self, mock_save, mock_input):
        """Test the record_daily_entry function integration."""
        # Mock user inputs
        mock_input.side_effect = [8, 'yes', 'yes', 'no', 'yes', 'Had a productive day']
        
        with patch('main.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '2024-01-15'
            
            record_daily_entry()
            
            # Verify save_daily_log was called with correct data
            mock_save.assert_called_once()
            call_args = mock_save.call_args[0][0]
            self.assertEqual(call_args['LogDate'], '2024-01-15')
            self.assertEqual(call_args['MoodRating'], 8)
            self.assertEqual(call_args['HadExercise'], 'yes')
    
    def test_headers_constant(self):
        """Test that HEADERS constant contains expected fields."""
        expected_headers = ['LogDate', 'MoodRating', 'HadExercise', 'GotEnoughSleep', 
                          'HadSocialInteraction', 'AteHealthy', 'Notes']
        self.assertEqual(HEADERS, expected_headers)
    
    def test_data_persistence_multiple_entries(self):
        """Test that multiple entries can be saved and loaded correctly."""
        entries = [
            {
                'LogDate': '2024-01-15',
                'MoodRating': '8',
                'HadExercise': 'Yes',
                'GotEnoughSleep': 'Yes',
                'HadSocialInteraction': 'No',
                'AteHealthy': 'Yes',
                'Notes': 'Great day!'
            },
            {
                'LogDate': '2024-01-16',
                'MoodRating': '6',
                'HadExercise': 'No',
                'GotEnoughSleep': 'Yes',
                'HadSocialInteraction': 'Yes',
                'AteHealthy': 'No',
                'Notes': 'Okay day'
            }
        ]
        
        with patch('main.DATA_DIR', self.test_data_dir), \
             patch('main.DATA_FILE', self.test_data_file):
            
            # Save multiple entries
            for entry in entries:
                save_daily_log(entry)
            
            # Load and verify
            loaded_logs = load_all_logs()
            self.assertEqual(len(loaded_logs), 2)
            self.assertEqual(loaded_logs[0]['LogDate'], '2024-01-15')
            self.assertEqual(loaded_logs[1]['LogDate'], '2024-01-16')

if __name__ == '__main__':
    unittest.main()