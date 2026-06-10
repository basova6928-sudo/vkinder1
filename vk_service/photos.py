import vk_api
from vk_service.vk_client import user_api


def get_photo_list(user_id: int):
    try:
        return get_top_photos(user_id)

    except vk_api.exceptions.ApiError as e:
        print(f"[VK API ERROR] get_photo_list({user_id}): {e}")
        return []

    except Exception as e:
        print(f"[UNEXPECTED ERROR] get_photo_list({user_id}): {e}")
        return []


def get_top_photos(user_id: int):
    try:
        response = user_api.photos.get(
            owner_id=user_id,
            album_id="profile",
            extended=1
        )

        items = response.get("items", [])

        if not items:
            return []

        sorted_photos = sorted(
            items,
            key=lambda x: x.get("likes", {}).get("count", 0),
            reverse=True
        )

        result = []

        for photo in sorted_photos[:3]:
            owner_id = photo.get("owner_id")
            photo_id = photo.get("id")

            if owner_id and photo_id:
                result.append(f"photo{owner_id}_{photo_id}")

        return result

    except vk_api.exceptions.ApiError as e:
        print(f"[VK PHOTO API ERROR] get_top_photos({user_id}): {e}")
        return []

    except Exception as e:
        print(f"[PHOTO PROCESS ERROR] get_top_photos({user_id}): {e}")
        return []
