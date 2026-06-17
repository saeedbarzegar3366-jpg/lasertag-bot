import aiosqlite
import random
import string
from datetime import datetime
from datetime import datetime, timedelta
import jdatetime

DB_NAME = "users.db"

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            phone TEXT,
            full_name TEXT,
            points INTEGER DEFAULT 0,
            invited_by INTEGER,
            invites_count INTEGER DEFAULT 0
        )
        """)
        await db.commit()



async def add_user(
    user_id,
    phone,
    full_name,
    invited_by=None
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO users
            (
                user_id,
                phone,
                full_name,
                invited_by
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                phone,
                full_name,
                invited_by
            )
        )

        await db.commit()



async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )
        return await cursor.fetchone()

async def create_reservations_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reserve_date TEXT,
            reserve_time TEXT,
            status TEXT,
            created_at TEXT,
            receipt_sent INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def create_discount_codes_table():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS discount_codes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            code TEXT UNIQUE,
            percent INTEGER,
            used INTEGER DEFAULT 0
        )
        """)

        await db.commit()



async def add_reservation(
    user_id,
    reserve_date,
    reserve_time,
    status="pending",
    discount_code=None,
    discount_percent=0
):
    async with aiosqlite.connect(DB_NAME) as db:

        created_at = datetime.now().isoformat()

        await db.execute("""
        INSERT INTO reservations
        (
            user_id,
            reserve_date,
            reserve_time,
            status,
            discount_code,
            discount_percent,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            reserve_date,
            reserve_time,
            status,
            discount_code,
            discount_percent,
            created_at
        ))

        await db.commit()



async def get_reservation(
    reserve_date,
    reserve_time
):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT *
        FROM reservations
        WHERE reserve_date=?
        AND reserve_time=?
        AND status IN (
            'pending',
            'waiting_admin',
            'approved'
        )
        """,
        (
            reserve_date,
            reserve_time
        ))
        return await cursor.fetchone()

       
async def update_reservation_status(
    reservation_id,
    status
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE reservations
            SET status=?
            WHERE id=?
            """,
            (
                status,
                reservation_id
            )
        )
        await db.commit()


async def get_last_user_reservation(
    user_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        return await cursor.fetchone()

async def get_day_reservations(
    reserve_date
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT reserve_time, status
            FROM reservations
            WHERE reserve_date=?
            """,
            (reserve_date,)
        )

        return await cursor.fetchall()


async def get_reservation_by_id(
    reservation_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE id=?
            """,
            (reservation_id,)
        )

        return await cursor.fetchone()


async def get_user_reservations(
    user_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE user_id=?
            AND status IN ('pending', 'approved')
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cursor.fetchall()


async def cancel_reservation(
    reservation_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE reservations
            SET status='cancelled'
            WHERE id=?
            """,
            (reservation_id,)
        )

        await db.commit()


async def get_reservation_by_id(
    reservation_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE id=?
            """,
            (reservation_id,)
        )

        return await cursor.fetchone()



async def get_all_user_reservations(
    user_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cursor.fetchall()


async def get_users_count():
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT COUNT(*) FROM users"
        )

        result = await cursor.fetchone()

        return result[0]


async def get_all_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT user_id, full_name, phone
            FROM users
            ORDER BY rowid DESC
            """
        )

        return await cursor.fetchall()


async def delete_user(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "DELETE FROM reservations WHERE user_id=?",
            (user_id,)
        )

        await db.execute(
            "DELETE FROM users WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


        
async def get_today_reservations(
    reserve_date
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE reserve_date=?
            AND status IN ('pending','approved')
            ORDER BY reserve_time
            """,
            (reserve_date,)
        )

        return await cursor.fetchall()


async def get_today_reservations_with_users(
    reserve_date
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                reservations.id,
                users.full_name,
                users.phone,
                reservations.reserve_time,
                reservations.status,
                reservations.user_id
            FROM reservations
            JOIN users
            ON reservations.user_id = users.user_id
            WHERE reservations.reserve_date=?
            AND reservations.status IN ('pending','approved')
            ORDER BY reservations.reserve_time
            """,
            (reserve_date,)
        )

        return await cursor.fetchall()



async def get_all_user_ids():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT user_id
            FROM users
            """
        )

        return await cursor.fetchall()


async def add_points(
    user_id,
    points
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET points = points + ?
            WHERE user_id = ?
            """,
            (
                points,
                user_id
            )
        )

        await db.commit()



async def remove_points(
    user_id,
    points
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET points = points - ?
            WHERE user_id = ?
            """,
            (
                points,
                user_id
            )
        )

        await db.commit()



async def get_user_points(
    user_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT points
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        result = await cursor.fetchone()

        if result:
            return result[0]

        return 0



async def increase_invites(
    user_id
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET invites_count = invites_count + 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

        await db.commit()



async def create_discount_code(
    user_id,
    percent
):

    code = ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=8
        )
    )

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO discount_codes
            (
                user_id,
                code,
                percent
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                code,
                percent
            )
        )

        await db.commit()

    return code



async def remove_points(
    user_id,
    points
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET points = points - ?
            WHERE user_id = ?
            """,
            (
                points,
                user_id
            )
        )

        await db.commit()



async def get_user_discount_codes(
    user_id
):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT code, percent, used
            FROM discount_codes
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cursor.fetchall()



async def update_reservations_table():

    async with aiosqlite.connect(DB_NAME) as db:

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN receipt_file_id TEXT
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN discount_code TEXT
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN discount_percent INTEGER DEFAULT 0
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN created_at TEXT
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN receipt_sent INTEGER DEFAULT 0
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN reminder_24 INTEGER DEFAULT 0
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN reminder_12 INTEGER DEFAULT 0
            """)
        except:
            pass

        try:
            await db.execute("""
            ALTER TABLE reservations
            ADD COLUMN reminder_6 INTEGER DEFAULT 0
            """)
        except:
            pass
        await db.commit()



from datetime import datetime

async def get_discount_code(
    code
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM discount_codes
            WHERE code = ?
            """,
            (code,)
        )

        discount = await cursor.fetchone()

        if not discount:
            return None

        expire_date = discount[5]

        if expire_date:

            if datetime.fromisoformat(
                expire_date
            ) < datetime.now():

                return None

        return discount


async def use_discount_code(
    code
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE discount_codes
            SET used = 1
            WHERE code = ?
            """,
            (code,)
        )

        await db.commit()



async def delete_expired_reservations():

    limit_time = (
        datetime.now() - timedelta(minutes=10)
    ).isoformat()

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM reservations
            WHERE status='pending'
            AND created_at < ?
            """,
            (limit_time,)
        )

        await db.commit()


async def delete_old_reservations():

    today = jdatetime.date.today().strftime(
        "%Y/%m/%d"
    )

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM reservations
            WHERE reserve_date < ?
            """,
            (today,)
        )

        await db.commit()

        

from datetime import datetime, timedelta

async def get_unpaid_reservation(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        limit_time = (
            datetime.now() - timedelta(minutes=10)
        ).isoformat()

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            WHERE user_id=?
            AND receipt_sent=0
            AND created_at > ?
            LIMIT 1
            """,
            (
                user_id,
                limit_time
            )
        )

        return await cursor.fetchone()


async def mark_receipt_sent(
    reservation_id
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE reservations
            SET receipt_sent=1,
                status='waiting_admin'
            WHERE id=?
            """,
            (reservation_id,)
        )

        await db.commit()


async def get_user_reservations_count(
    user_id,
    reserve_date
):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM reservations
            WHERE user_id=?
            AND reserve_date=?
            """,
            (
                user_id,
                reserve_date
            )
        )

        result = await cursor.fetchone()

        return result[0]



async def create_discount_usage_table():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS discount_usage(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            code TEXT
        )
        """)

        await db.commit()



async def has_used_discount(
    user_id,
    code
):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM discount_usage
            WHERE user_id=?
            AND code=?
            """,
            (
                user_id,
                code
            )
        )

        return await cursor.fetchone()



async def save_discount_usage(
    user_id,
    code
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO discount_usage
            (
                user_id,
                code
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                code
            )
        )

        await db.commit()



async def create_global_discount(
    code,
    percent,
    days
):

    expire_date = (
        datetime.now() +
        timedelta(days=days)
    ).isoformat()

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO discount_codes
            (
                user_id,
                code,
                percent,
                expire_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                0,
                code,
                percent,
                expire_date
            )
        )

        await db.commit()



async def update_discount_codes_table():

    async with aiosqlite.connect(DB_NAME) as db:

        try:
            await db.execute("""
            ALTER TABLE discount_codes
            ADD COLUMN expire_date TEXT
            """)
        except:
            pass

        await db.commit()



async def get_all_reservations():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM reservations
            ORDER BY id DESC
            """
        )

        return await cursor.fetchall()




async def get_all_reservations_with_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                reservations.id,
                users.full_name,
                users.phone,
                reservations.user_id,
                reservations.reserve_date,
                reservations.reserve_time,
                reservations.status
            FROM reservations
            LEFT JOIN users
            ON reservations.user_id = users.user_id
            ORDER BY reservations.id DESC
            """
        )

        return await cursor.fetchall()




async def delete_reservation_by_id(
    reservation_id
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM reservations
            WHERE id = ?
            """,
            (reservation_id,)
        )

        await db.commit()



from datetime import datetime

async def expire_old_reservations():

    now = datetime.now()

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT id, reserve_date, reserve_time
        FROM reservations
        WHERE status='approved'
        """)

        reservations = await cursor.fetchall()

        for reservation in reservations:

            reservation_id = reservation[0]
            reserve_date = reservation[1]
            reserve_time = reservation[2]

            try:

                jalali_dt = jdatetime.datetime.strptime(
                    f"{reserve_date} {reserve_time}",
                    "%Y/%m/%d %H:%M"
                )

                reserve_datetime = jalali_dt.togregorian()

                if reserve_datetime < now:

                    await db.execute(
                        """
                        UPDATE reservations
                        SET status='expired'
                        WHERE id=?
                        """,
                        (reservation_id,)
                    )

            except:
                pass

        await db.commit()


async def create_club_photos_table():

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS club_photos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT
        )
        """)

        await db.commit()



async def add_club_photo(
    file_id
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO club_photos
            (
                file_id
            )
            VALUES
            (?)
            """,
            (file_id,)
        )

        await db.commit()



async def get_club_photos():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM club_photos
            """
        )

        return await cursor.fetchall()



async def delete_club_photo(
    photo_id
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM club_photos
            WHERE id=?
            """,
            (photo_id,)
        )

        await db.commit()




async def get_all_approved_reservations():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT *
        FROM reservations
        WHERE status='approved'
        """)

        return await cursor.fetchall()


async def mark_reminder_sent(
    reservation_id,
    reminder_type
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            f"""
            UPDATE reservations
            SET reminder_{reminder_type}=1
            WHERE id=?
            """,
            (reservation_id,)
        )

        await db.commit()



async def get_pending_approvals():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT *
            FROM reservations
            WHERE status='waiting_admin'
        """)

        return await cursor.fetchall()




async def save_receipt_file(
    reservation_id,
    file_id
):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE reservations
            SET receipt_file_id=?,
                receipt_sent=1,
                status='waiting_admin'
            WHERE id=?
            """,
            (
                file_id,
                reservation_id
            )
        )

        await db.commit()