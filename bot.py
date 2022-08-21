import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import requests
import shutil

from PIL import Image

token = ""
session = vk_api.VkApi(token=token)
api = session.get_api()


def send_image(user_id):
    """Отправляет картинку в чат"""
    uploader = vk_api.upload.VkUpload(api)
    img = uploader.photo_messages("merged_img.jpg")
    media_id = str(img[0]['id'])
    owner_id = str(img[0]['owner_id'])
    api.messages.send(user_id=user_id, attachment=f"photo{owner_id}_{media_id}", random_id=0)


def send_message(user_id, message, keyboard=None):
    """Отправляет сообщение от бота в чат"""
    if keyboard != None:
        api.messages.send(
            user_id=user_id,
            message=message,
            random_id=0,
            keyboard=keyboard.get_keyboard()
        )
    else:
        api.messages.send(
            user_id=user_id,
            message=message,
            random_id=0
        )
    send_image(user_id)


def save_profile_image(url_image):
    """Скачивает фото с профайла и сохраняет"""
    image_url = str(url_image)
    print(image_url)
    filename = "picture_of_profile.jpg"

    print(filename)
    print(url_image)
    r = requests.get(url_image, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
        merge_images()


def merge_images():
    """Соединяет картинку с фоном"""
    image1 = Image.open('picture_of_profile.jpg')
    image1 = image1.resize((200, 200))
    image1_size = image1.size
    new_image = Image.new('RGB', (750, 250), (250, 250, 0))
    new_image.paste(image1, (275, 25))
    new_image.save("merged_img.jpg", "JPEG")


for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text
        user_id = event.user_id
        if text in ["Начать", "Привет бот"]:
            keyboard = VkKeyboard(inline=True)
            keyboard.add_button("пришли картинку", VkKeyboardColor.PRIMARY)

            url_image = api.users.get(user_id=user_id, fields="photo_max")[0]["photo_max"]
            save_profile_image(url_image)

            user_name = api.users.get(user_id=user_id)[0]['first_name']
            send_message(user_id, f"Привет, {user_name}!", keyboard)
