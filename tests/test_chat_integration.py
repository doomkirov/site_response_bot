import os
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from app.alerts import build_error_message
from app.checker import send_text_to_chat
from app.nightly_report import build_nightly_report_message


RUN_CHAT_INTEGRATION = os.getenv("RUN_CHAT_INTEGRATION") == "1"
MOSCOW_TZ = ZoneInfo("Europe/Moscow")


@unittest.skipUnless(
    RUN_CHAT_INTEGRATION,
    "Для реальной отправки установите RUN_CHAT_INTEGRATION=1",
)
class ChatIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_send_monitoring_messages(self):
        chat_id = os.getenv("TEST_CHAT_ID", "chat73069")
        now = datetime.now(MOSCOW_TZ)
        period_end = now.replace(hour=9, minute=0, second=0, microsecond=0)
        period_start = period_end - timedelta(days=1)
        failed_at = period_start + timedelta(hours=2)
        recovered_at = failed_at + timedelta(minutes=45)

        failed_incident = SimpleNamespace(
            id=1,
            link_id=1,
            url="https://httpbin.org/delay/20",
            status_code=903,
            description="Таймаут соединения (более 15 секунд).",
            confirmed_status_code=903,
            confirmed_description="Таймаут соединения (более 15 секунд).",
            started_at=int(failed_at.timestamp()),
            recovered_at=int(recovered_at.timestamp()),
        )
        links = [
            SimpleNamespace(id=1, url="https://httpbin.org/delay/20"),
            SimpleNamespace(id=2, url="https://httpbin.org/status/200"),
        ]

        messages = (
            (
                "успешный статус 200",
                "[B]ТЕСТ: успешная проверка[/B][BR]"
                "• [URL=https://httpbin.org/status/200]https://httpbin.org/status/200[/URL][BR]"
                "Код: 200. Сайт доступен.",
            ),
            (
                "неуспешный статус 903",
                "[B]ТЕСТ: недоступность[/B][BR]" + build_error_message([failed_incident]),
            ),
            (
                "суточный отчёт",
                "[B]ТЕСТОВЫЙ ОТЧЁТ[/B][BR]"
                + build_nightly_report_message(links, [failed_incident], period_start, period_end),
            ),
        )

        for case_name, message in messages:
            with self.subTest(case=case_name):
                sent = await send_text_to_chat(message, chat_id=chat_id)
                self.assertTrue(
                    sent,
                    f"Webhook не подтвердил отправку сообщения «{case_name}» HTTP-статусом 200",
                )
