import vk_api
from config import USER_TOKEN, GROUP_TOKEN

user_session = vk_api.VkApi(token=USER_TOKEN)
group_session = vk_api.VkApi(token=GROUP_TOKEN)

user_api = user_session.get_api()
group_api = group_session.get_api()
