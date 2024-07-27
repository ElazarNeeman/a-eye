import datetime
import unittest
from unittest.mock import patch, MagicMock
from image_collector import ImageCollector


class TestImageCollector(unittest.TestCase):
    def setUp(self):
        self.collector = ImageCollector()

    @patch('image_collector.queue.Queue.put')
    def test_collect(self, mock_put):
        detector = MagicMock()
        person_image = MagicMock()
        detector.detected_identities = {
            'key1': {
                'identity': 'identity1',
                'person': person_image
            }
        }
        self.collector.collect(detector)
        mock_put.assert_called_once()

    @patch('image_collector.cv2.imwrite')
    @patch('image_collector.queue.Queue.get')
    def test_write_data(self, mock_get, mock_imwrite):
        # Create a datetime object
        dt = datetime.datetime(year=2022, month=12, day=1, hour=8, minute=30, second=23)
        mock_get.return_value = {
            'timestamp': dt.timestamp(),
            'identity': 'identity1',
            'image': 'image1'
        }
        self.collector.write_data()
        mock_get.assert_called_once()
        mock_imwrite.assert_called_once()
        # expected_file_name = f'images/{dt.year}-{dt.month}-{dt.day}/{dt.hour}-{dt.minute}-identity1.jpg'
        # mock_imwrite.assert_called_with(expected_file_name, 'image1')
