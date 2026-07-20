import unittest
from datetime import datetime
from types import SimpleNamespace

from app.alerts import build_error_message, build_recovery_message, build_reminder_message
from app.app_support.response_data_class import ResponseData
from app.nightly_report import MOSCOW_TZ, build_nightly_report_message


class MessageFormattingTests(unittest.TestCase):
    def setUp(self):
        self.incident = SimpleNamespace(
            id=1,
            link_id=1,
            url="https://example.test",
            status_code=903,
            description="Таймаут соединения (более 15 секунд).",
            confirmed_status_code=903,
            confirmed_description="Таймаут соединения (более 15 секунд).",
            started_at=int(datetime(2026, 7, 12, 10, 0, tzinfo=MOSCOW_TZ).timestamp()),
            recovered_at=int(datetime(2026, 7, 12, 10, 45, tzinfo=MOSCOW_TZ).timestamp()),
        )

    def test_alert_threshold_labels(self):
        self.assertIn("недоступен в течение 5 минут", build_error_message([self.incident]))
        self.assertIn("недоступен в течение 60 минут", build_reminder_message([self.incident]))

    def test_recovery_contains_timestamp(self):
        message = build_recovery_message([self.incident], [])
        self.assertIn("12.07.2026 10:45:00", message)

    def test_report_marks_healthy_and_failed_sites(self):
        links = [
            SimpleNamespace(id=1, url="https://example.test"),
            SimpleNamespace(id=2, url="https://healthy.test"),
        ]
        start = datetime(2026, 7, 12, 9, 0, tzinfo=MOSCOW_TZ)
        end = datetime(2026, 7, 13, 9, 0, tzinfo=MOSCOW_TZ)
        message = build_nightly_report_message(links, [self.incident], start, end)
        self.assertIn("❌ [URL=https://example.test]", message)
        self.assertIn("✅ [URL=https://healthy.test]", message)
        self.assertIn("Недоступен 45 мин.", message)
        self.assertIn("с 12.07.2026 10:00:00 по 12.07.2026 10:45:00", message)

    def test_custom_status_explanation_is_short(self):
        response = ResponseData("https://example.test", 903, "very long exception details")
        self.assertEqual(response.explanation, "Таймаут соединения (более 15 секунд).")


if __name__ == "__main__":
    unittest.main()
