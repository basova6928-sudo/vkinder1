from vk_service.photos import get_photo_list


def build_candidate(vk_user):
    photos = get_photo_list(vk_user["id"])

    text = (
        f'{vk_user["first_name"]} {vk_user["last_name"]}\n'
        f'https://vk.com/id{vk_user["id"]}'
    )

    return text, photos


def search_candidates(user_id):
    from vk_service.search import search_users

    return search_users(
        city=1,
        age_from=18,
        age_to=30,
        sex=1
    )
