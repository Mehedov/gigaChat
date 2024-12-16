from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage

from config_data.config import Config, load_config

config: Config = load_config()

prompts = {
    'Обычная': 'Ты — бот-storyteller, напиши сказку. Отвечай сразу историей без вводных фраз и system messages по типу "Вот ваша сказка:".',
    'Приключение': 'Создай историю о группе друзей, которые отправились в путешествие',
    'Романтика': 'Напиши трогательную сказку о двух влюбленных, которые преодолевают все преграды, чтобы быть вместе, несмотря на разногласия между их семьями.',
    'Сказка с моралью': 'Напиши историю о двух персонажах, которые учат друг друга важному уроку о [ценности дружбы или честности или о чем-то прочем] через свои приключения.',
    'Веселая сказка': 'Создай веселую сказку о каком-либо персонаже, который пытается сделать что-то важное, но постоянно попадает в смешные ситуации из-за своих неуклюжих действий.',
    'Хоррор': 'Создай историю о каком-либо персонаже, который оказывается в заброшенном месте и сталкивается с сущностью или призраком, пытаясь разгадать его тайну.'
}

gigachat = GigaChat(
    credentials=config.gigachat_token,
    scope="GIGACHAT_API_PERS",
    model="GigaChat-Max",
    verify_ssl_certs=False,  # Отключает проверку наличия сертификатов НУЦ Минцифры
    streaming=False,
)


def create_story(story_type: str = 'Обычная', names: str = None) -> str:
    prompt = prompts['Обычная'] if story_type == 'Обычная' else prompts['Обычная'] + prompts[story_type]
    if names:
        prompt += f'Должны участвовать пресонаж(-и) со следующими именами: {names}'
    messages = [SystemMessage(content=prompt)]
    print(names)
    print(messages)
    response = gigachat.invoke(messages)
    return response.content



