from db.database_migration import export_songs

if __name__ == "__main__":
    database_path = input("Enter the path to the songs database (default: db/data/songs.db): ") or "db/data/songs.db"
    output_path = input("Enter the output JSON file path (default: exported_songs.json): ") or "exported_songs.json"
    export_songs(database_path, output_path)
