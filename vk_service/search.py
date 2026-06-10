from vk_service.vk_client import user_api


def search_users(city, age_from, age_to, sex, offset=0, count=20):
    try:
        response = user_api.users.search(
            city=city,
            age_from=age_from,
            age_to=age_to,
            sex=sex,
            count=count,
            offset=offset,
            has_photo=1,
            fields="domain"
        )

        users = response.get("items", [])
        result = []

        for user in users:
            if user.get("deactivated"):
                continue

            if user.get("is_closed"):
                continue

            result.append({
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            })

        return result

    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        return []
