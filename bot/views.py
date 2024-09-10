import json
from aiogram import types, Bot
from django.http import JsonResponse, HttpResponseNotFound
from django.views import View
from django.conf import settings

from bot.app import dp
from bot.models import TgUser


class BotView(View):
    async def post(self, request, *args, **kwargs):
        update = json.loads(request.body.decode('utf-8'))
        await dp.process_update(types.Update(**update))
        return JsonResponse({"status": "ok"})

    async def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("Not found")


class SendMessagesView(View):

    async def send(self, message, chat_id, bot: Bot):
        try:
            await bot.send_message(chat_id, message)
        except Exception as e:
            print(e)

    async def post(self, request, *args, **kwargs):
        update = json.loads(request.body.decode('utf-8'))
        bot = Bot(token=settings.API_TOKEN)
        message = update.get('message')
        if not message:
            return JsonResponse({"status": "fail", "message": "Message not found"})
        users = [user async for user in TgUser.objects.all()]
        for user in users:
            await self.send(message, user.user_id, bot)
        return JsonResponse({"status": "ok"})


class AcceptNotificationView(View):

    async def send(self, message, chat_id, bot: Bot):
        try:
            await bot.send_message(chat_id, message)
        except Exception as e:
            print(e)
            return False

        return True

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))

            bot = Bot(token=settings.API_TOKEN)
            transaction_id = data.get('transaction_id')
            params = data.get('params', [])


            message = '———————————-\n'
            for param in params:
                key = param.get('key')
                value = param.get('value')
                message += f'{key}: {value}\n'
            message += '———————————-'

            chat_id = settings.TELEGRAM_CHAT_ID
            res = await self.send(message, chat_id, bot)
            if res:
                return JsonResponse({'transaction_id': transaction_id, 'status': 'accept'})
            else:
                return JsonResponse({'transaction_id': transaction_id, 'status': 'reject'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
