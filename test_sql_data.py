from db_handler import connect_to_db

def sanity_check():
    conn = connect_to_db()
    cursor = conn.cursor()

    for table in ['channels', 'playlists', 'videos', 'comments']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} rows")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    sanity_check()


# from db_handler import connect_to_db

# def force_clear_data():
#     conn = connect_to_db()
#     cursor = conn.cursor()

#     print("⚠️ Disabling foreign key checks...")
#     cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

#     print("💣 Truncating all tables...")
#     cursor.execute("TRUNCATE TABLE comments")
#     cursor.execute("TRUNCATE TABLE videos")
#     cursor.execute("TRUNCATE TABLE playlists")
#     cursor.execute("TRUNCATE TABLE channels")

#     print("✅ Re-enabling foreign key checks...")
#     cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("✅ All data has been forcefully deleted.")

# if __name__ == "__main__":
#     force_clear_data()
