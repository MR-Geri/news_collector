from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.longpoll import VkLongPoll


class MyVkLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as err:
                print('Ошибка > ', err)


class MyVkBotLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as err:
                print('Ошибка > ', err)
