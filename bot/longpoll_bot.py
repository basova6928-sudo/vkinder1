from dotenv import load_dotenv
import os
from random import randrange
import time

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from bot.service import build_candidate, search_candidates
from bot.state_manager import get_state
from database.repository import (
    add_to_favorites,
    get_favorites,
    add_user,
    get_user
)

load_dotenv()

TOKEN = os.getenv("GROUP_TOKEN")

print("GROUP_TOKEN:", TOKEN)

vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)


last_message_time = {}
is_processing = {}


def write_msg(user_id, message, attachment=None):
    """Отправка сообщения пользователю"""
    params = {
        "user_id": user_id,
        "message": message,
        "random_id": randrange(10 ** 7),
    }

    if attachment:
        params["attachment"] = attachment

    vk.method("messages.send", params)


def ensure_user_exists(user_id):
    """Проверяет, есть ли пользователь в БД, если нет - добавляет"""
    user = get_user(user_id)
    if not user:
        try:
            user_info = vk.method("users.get", {"user_ids": user_id})
            if user_info:
                first_name = user_info[0].get("first_name", "")
                last_name = user_info[0].get("last_name", "")
                add_user(user_id, first_name, last_name)
                print(f"✅ Добавлен пользователь: {user_id}")
                return True
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            return False
    return True


def run_bot():
    """Запуск бота"""
    print("🚀 БОТ ЗАПУЩЕН")

    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

            user_id = event.user_id
            request = event.text.lower().strip()
            current_time = time.time()

           
            ensure_user_exists(user_id)

        
            if is_processing.get(user_id, False):
                print(f"⚠️ Пропуск: {user_id} уже в обработке")
                continue

            if user_id in last_message_time:
                if current_time - last_message_time[user_id] < 2.0:
                    print(f"⚠️ Пропуск: слишком часто от {user_id}")
                    continue

            is_processing[user_id] = True
            last_message_time[user_id] = current_time

            try:
                state = get_state(user_id)

              
                if request == "поиск":
                    print(f"🔍 Поиск для {user_id}")

                    candidates = search_candidates(user_id)

                    print(f"Найдено: {len(candidates) if candidates else 0}")

                    if not candidates:
                        write_msg(user_id, "Никого не нашёл 😢")
                        continue

                   
                    favorites = get_favorites(user_id)
                    favorite_ids = [f["id"] for f in favorites]
                    candidates = [
                        c for c in candidates
                        if c.get("id") not in favorite_ids
                    ]

                    if not candidates:
                        write_msg(
                            user_id,
                            "Новых кандидатов нет 😢\nВсе в избранном"
                        )
                        continue

                    state.set_candidates(candidates)
                    candidate = state.current()

                    profile_text, photos = build_candidate(candidate)
                    attachment = ",".join(photos) if photos else None

                    write_msg(user_id, profile_text, attachment=attachment)

               
                elif request == "следующий":
                    print(f"➡️ Следующий для {user_id}")

                    candidate = state.next()

                    if not candidate:
                        write_msg(
                            user_id,
                            "Кандидаты закончились 😢\nНапишите 'поиск'"
                        )
                        continue

                    profile_text, photos = build_candidate(candidate)
                    attachment = ",".join(photos) if photos else None

                    write_msg(user_id, profile_text, attachment=attachment)

               
                elif request == "в избранное":
                    print(f"❤️ Избранное для {user_id}")

                    candidate = state.current()

                    if not candidate:
                        write_msg(user_id, "Нет активного кандидата 😢")
                        continue

                    vk_id = candidate.get("id") or candidate.get("vk_id")

                    if not vk_id:
                        write_msg(user_id, "Ошибка: нет ID кандидата 😢")
                        continue

                    candidate_for_db = {
                        "vk_id": vk_id,
                        "first_name": candidate.get("first_name", ""),
                        "last_name": candidate.get("last_name", ""),
                        "profile_url": candidate.get(
                            "profile_url",
                            f"https://vk.com/id{vk_id}"
                        ),
                        "photos": candidate.get("photos", []),
                        "search_criteria": candidate.get("search_criteria", "")
                    }

                    success = add_to_favorites(user_id, candidate_for_db)

                    if success:
                        name = f"{candidate_for_db['first_name']} "
                        name += f"{candidate_for_db['last_name']}".strip()
                        write_msg(
                            user_id,
                            f"❤️ {name or 'Кандидат'} добавлен(а)!"
                        )
                    else:
                        write_msg(user_id, "Ошибка при добавлении 😢")

             
                elif request == "избранное":
                    print(f"📋 Избранное для {user_id}")

                    favorites = get_favorites(user_id)

                    if not favorites:
                        write_msg(user_id, "Избранных пока нет 😢")
                    else:
                        msg = "❤️ ВАШЕ ИЗБРАННОЕ ❤️\n\n"
                        for i, fav in enumerate(favorites, 1):
                            msg += f"{i}. {fav['name']}\n"
                            msg += f"   {fav['profile_url']}\n\n"
                        write_msg(user_id, msg)

               
                else:
                    write_msg(
                        user_id,
                        "📌 Команды:\nпоиск\nследующий\nв избранное\nизбранное"
                    )

            except Exception as e:
                print(f"❌ Ошибка: {e}")
                write_msg(user_id, "Произошла ошибка 😢")

            finally:
                is_processing[user_id] = False
                time.sleep(0.3)


if __name__ == "__main__":
    run_bot()
