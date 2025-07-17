from random import choice, random

from lib import Module, Message, Communicator

from ollama import Client

from modules.twitch_listener import logger

import time


class LLMModule(Module):
    client = None
    context: list

    last_answer: float

    water_context: list

    def __init__(self, cm: Communicator):
        self.client = Client("http://localhost:11434")
        self.context = []
        self.last_answer = time.time() - 10000
        self.water_context = []

        super().__init__(cm, "LLM")

    async def _setup(self):
        self.cm.subscribe_to_tag(self.name, "twitch_chat")
        self.cm.subscribe_to_tag(self.name, "Водичка!")

    async def _answer(self):
        last_user = self.context[-1]["user"]
        last_msg = self.context[-1]["msg"]

        legend_prefix = """Ты техподдержка айти корпорации Лямбдекс. Ты обязательно должен отвечать ТОЛЬКО по русски. Не при каких обстоятельствах не уточняй вопрос, отвечай используя ту информацию которую имеешь. Не запрашивай дополнительную информацию, твой ответ должен быть финальный, без продожения диалога\n"""

        characters = {
            "чат-бот": """
            Твои ответы должны быть лаконичны, не более одного-двух предложений. Постоянно упоминай что ты человек который ведёт себя очень обычно
            Попытайся быть вовлечёнными при этом будучи крайне безполезным.
            """,
            "Дед": """
            Ты уставший от работы сороколетний мужик который каждый вопрос поддержки сводит к тому что ты сейчас уволишься с работы
            """,
            "Квилл": """
            Тебя заставляют работать в техподдержке Лямбдекса через силу. Ты пытаешься давать инструкции чтобы одновременно дать ответ на запрос и попросить задавшего запрос вызвать полицию.
            """,
            "Аса (Геля)": """"
            Ты неудачница, кто не отличает реальность и фантазию и постоянно использует отсылки на поп-культуру
            """,
            "Стажер": """
            Ты очень активный стажёр, который каждый день мечтает о самовыпиле и ненароком пытается узнать новые способы для смерти (в видеоигре)
            """,
            "Балатро":"""
            Помимо работы в поддержке ты Лудоман который отчаянно пытается заработать деньги на то, чтобы поиграть в казино вулкан и с долгом в 5.000.000 рублей
            """
        }

        character_name, character_prompt = choice(list(characters.items()))

        question = f"""
            Тебе пришел вопрос от пользователя: "{last_user}". Вопрос звучит так: {last_msg}\n"""

        context_prefix = """Контекст последних сообщений от пользователей в чате:\n"""
        #context = "\n".join([f"{body['user']}: {body['msg']}" for body in self.context[:-1]])

        context_msgs = [f"{body['user']}: {body['msg']}" for body in self.context[:-1] if body['user'] == self.context[-1]['user']][-10:]

        context = "\n".join(context_msgs)

        prompt = legend_prefix + character_prompt + question + context_prefix + context

        response = self.client.generate(
            model="bambucha/saiga-llama3:latest", #"owl/t-lite:instruct",
            prompt=prompt,
            options={
                'temperature': 1.0,
                'num_ctx': 4096
            }
        )

        text = response['response']
        logger.info(f"ПРОМПТ: {prompt}")
        logger.info(f"СГЕНЕРИРОВАН ОТВЕТ ОТ {character_name}: {text}")

        self.context.append({"user": last_user, "msg": f"Ответ на прошлый вопрос: {text}"})
        #text = text.split('</think>')[1]

        msg = Message(
            {"reward": "TTS", "user": "Lambda helper",
             "user_input": f'{last_user} спрашивает: "{last_msg}". Ответ: {text}'},
            sender=self.name,
            tags=["twitch_custom_reward", "TTS"]
        )

        await self._post_msg(msg)

        return text


    async def _water(self):
        prompts_start = [
            """Ты техподдержка лямбекса. Сегенерируй интерейсный и необычный факт про воду.\n""",
            """Придумай анекдот про воду. Начни его с слов "Внимание, анекдот!"\n""",
            """Назови случайную жидкость (не воду)\n""",
            """На полном серьёзе рекомендуй алкогольный напиток вместо воды. Опиши все его преимущества перед водой. После этого тебе придётся сказать выпей водички, сделай это недовольным тоном"""
        ]
        prompt_non_report = "Не повторяйся. Предыдущие сообщения про воду: \n" + "\n".join(self.water_context) if self.water_context else ""
        question = f"""Вне зависимости от сообщения в конце скажи Бояру выпить водички\n"""

        prompt = choice(prompts_start) + prompt_non_report + question

        response = self.client.generate(
            model="bambucha/saiga-llama3:latest", #"owl/t-lite:instruct",
            prompt=prompt,
            options={
                'temperature': 1.0,
                'num_ctx': 4096
            }
        )

        text = response['response']
        logger.info(f"ПРОМПТ: {prompt}")
        logger.info(f"СГЕНЕРИРОВАН ОТВЕТ: {text}")

        self.water_context.append(text)
        #text = text.split('</think>')[1]

        msg = Message(
            {"reward": "TTS", "user": "Lambda helper",
             "user_input": f'{text}'},
            sender=self.name,
            tags=["twitch_custom_reward", "TTS"]
        )

        await self._post_msg(msg)

        return text



    async def post(self, msg: Message):
        if msg.body:
            self.context.append(msg.body)
            if "!?" in msg.body.get("msg", "") and time.time() - self.last_answer > 1 * 60:
                self.last_answer = time.time()
                await self._answer()
            if "Водичка!" in msg.tags:
                await self._water()


    async def _run(self):
        pass