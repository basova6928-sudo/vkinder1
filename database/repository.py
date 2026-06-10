from database.db import get_connection


# ========== ПОЛЬЗОВАТЕЛИ ==========

def add_user(vk_id, first_name, last_name):
    """Добавление пользователя в БД"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (vk_id, first_name, last_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (vk_id) DO NOTHING
            """, (vk_id, first_name, last_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Ошибка добавления пользователя: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user(vk_id):
    """Получение пользователя по vk_id"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, vk_id, first_name, last_name "
                "FROM users WHERE vk_id = %s",
                (vk_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "vk_id": row[1],
                    "first_name": row[2],
                    "last_name": row[3]
                }
            return None
    finally:
        conn.close()


def get_user_by_db_id(db_id):
    """Получение пользователя по id в БД"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, vk_id, first_name, last_name "
                "FROM users WHERE id = %s",
                (db_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "vk_id": row[1],
                    "first_name": row[2],
                    "last_name": row[3]
                }
            return None
    finally:
        conn.close()


# ========== ИЗБРАННОЕ ==========

def add_to_favorites(vk_user_id, candidate):
    """Добавление кандидата в избранное"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Получаем внутренний ID пользователя
            cur.execute(
                "SELECT id FROM users WHERE vk_id = %s",
                (vk_user_id,)
            )
            user_row = cur.fetchone()

            if not user_row:
                print(f"❌ Пользователь {vk_user_id} не найден в БД!")
                return False

            db_user_id = user_row[0]
            candidate_vk_id = candidate.get("vk_id")

            if not candidate_vk_id:
                print("❌ Нет vk_id в кандидате!")
                return False

            # Проверяем, есть ли кандидат в matches
            cur.execute(
                "SELECT id FROM matches WHERE vk_id = %s",
                (candidate_vk_id,)
            )
            match_row = cur.fetchone()

            if match_row:
                match_id = match_row[0]
            else:
                # Сохраняем нового кандидата
                photos = candidate.get("photos", [])
                cur.execute("""
                    INSERT INTO matches
                    (vk_id, first_name, last_name, profile_url,
                     photo_1, photo_2, photo_3, search_criteria)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    candidate["vk_id"],
                    candidate.get("first_name", ""),
                    candidate.get("last_name", ""),
                    candidate.get("profile_url", ""),
                    photos[0] if len(photos) > 0 else None,
                    photos[1] if len(photos) > 1 else None,
                    photos[2] if len(photos) > 2 else None,
                    candidate.get("search_criteria", "")
                ))
                match_id = cur.fetchone()[0]

            # Добавляем в избранное
            cur.execute("""
                INSERT INTO favorites (user_id, match_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, match_id) DO NOTHING
            """, (db_user_id, match_id))

            conn.commit()
            return True

    except Exception as e:
        print(f"❌ Ошибка добавления в избранное: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_favorites(vk_user_id):
    """Получение списка избранных кандидатов для пользователя"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT m.id, m.vk_id, m.first_name, m.last_name, m.profile_url
                FROM favorites f
                JOIN matches m ON f.match_id = m.id
                JOIN users u ON f.user_id = u.id
                WHERE u.vk_id = %s
                ORDER BY f.id DESC
            """, (vk_user_id,))

            favorites = []
            for row in cur.fetchall():
                favorites.append({
                    "match_db_id": row[0],
                    "id": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "name": f"{row[2]} {row[3]}".strip(),
                    "profile_url": row[4]
                })
            return favorites
    finally:
        conn.close()


def is_favorite(vk_user_id, candidate_vk_id):
    """Проверка, есть ли кандидат в избранном у пользователя"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM favorites f
                JOIN users u ON f.user_id = u.id
                JOIN matches m ON f.match_id = m.id
                WHERE u.vk_id = %s AND m.vk_id = %s
            """, (vk_user_id, candidate_vk_id))
            return cur.fetchone() is not None
    finally:
        conn.close()


def remove_from_favorites(vk_user_id, candidate_vk_id):
    """Удаление кандидата из избранного"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM favorites
                WHERE user_id = (SELECT id FROM users WHERE vk_id = %s)
                AND match_id = (SELECT id FROM matches WHERE vk_id = %s)
            """, (vk_user_id, candidate_vk_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Ошибка удаления из избранного: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_favorites_count(vk_user_id):
    """Количество избранных кандидатов у пользователя"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM favorites f
                JOIN users u ON f.user_id = u.id
                WHERE u.vk_id = %s
            """, (vk_user_id,))
            return cur.fetchone()[0]
    finally:
        conn.close()
