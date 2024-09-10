from django.core.management.base import BaseCommand
from bot.app import start_bot
import aiohttp


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **kwargs):
        self.stdout.write("Bot started...")
        start_bot()
