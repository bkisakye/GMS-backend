# import os
# import sqlite3
# from django.core.management.base import BaseCommand, CommandError


# class Command(BaseCommand):
#     help = "Transfers data from one SQLite database to another"

#     def handle(self, *args, **options):
#         # Update the paths to the correct locations
#         source_db = os.path.expanduser("~/Videos/Desktop/GMS/BaylorGrants/db.sqlite3")
#         destination_db = os.path.expanduser("~/Desktop/GMS/BaylorGrants/db.sqlite3")

#         # Print the paths to verify
#         self.stdout.write(f"Source DB path: {source_db}")
#         self.stdout.write(f"Destination DB path: {destination_db}")

#         # Check if the source file exists
#         if not os.path.exists(source_db):
#             raise CommandError(f"Source database file does not exist: {source_db}")

#         try:
#             source_conn = sqlite3.connect(source_db)
#             destination_conn = sqlite3.connect(destination_db)

#             source_cursor = source_conn.cursor()
#             destination_cursor = destination_conn.cursor()

#             # Get the list of tables from the source database
#             source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#             tables = source_cursor.fetchall()

#             # Iterate through each table
#             for table in tables:
#                 table_name = table[0]

#                 # Get all data from the source table
#                 source_cursor.execute(f"SELECT * FROM {table_name};")
#                 rows = source_cursor.fetchall()

#                 if not rows:
#                     self.stdout.write(
#                         self.style.WARNING(
#                             f"No data found in table '{table_name}'. Skipping."
#                         )
#                     )
#                     continue

#                 # Get column names
#                 source_cursor.execute(f"PRAGMA table_info({table_name});")
#                 columns = [column[1] for column in source_cursor.fetchall()]
#                 placeholders = ", ".join(["?" for _ in columns])

#                 # Insert data into the destination table
#                 self.stdout.write(f"Inserting data into table '{table_name}'...")
#                 destination_cursor.executemany(
#                     f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});",
#                     rows,
#                 )

#             # Commit changes and close connections
#             destination_conn.commit()
#             self.stdout.write(
#                 self.style.SUCCESS("Data transfer completed successfully")
#             )

#         except sqlite3.Error as e:
#             raise CommandError(f"SQLite error: {e}")

#         finally:
#             if "source_conn" in locals():
#                 source_conn.close()
#             if "destination_conn" in locals():
#                 destination_conn.close()
