"""
データベース機能のテストスクリプト
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.songs_database import SongsDatabase
from utils.songs_class import Song


def test_database():
    # データベースを初期化
    db = SongsDatabase("db/data/test_songs.db")
    
    # テスト前にデータベースをクリア
    db.clear_all_songs()

    # テスト用のSongオブジェクトを作成
    test_song = Song(
        id="test001",
        title="テスト楽曲",
        publishedTimestamp=1694000000,
        publishedType=1,
        durationSeconds=240,
        vocal=["初音ミク"],
        illustrations=["テストイラスト"],
        movie=["テスト動画"],
        bpm=120,
        mainKey=60,
        chordRate6451=0.5,
        chordRate4561=0.3,
        mainChord="C",
        pianoRate=0.8,
        modulationTimes=2,
        comment="これはテスト楽曲です",
    )

    print("=== データベーステスト開始 ===")

    # 1. 楽曲を追加
    print("1. 楽曲追加テスト")
    result = db.add_song(test_song)
    print(f"   追加結果: {result}")

    # 2. 楽曲数を確認
    print("2. 楽曲数確認テスト")
    count = db.get_songs_count()
    print(f"   楽曲数: {count}")

    # 3. IDで楽曲を取得
    print("3. ID検索テスト")
    retrieved_song = db.get_song_by_id("test001")
    if retrieved_song:
        print(f"   取得した楽曲: {retrieved_song.title}")
        print(f"   BPM: {retrieved_song.bpm}")
    else:
        print("   楽曲が見つかりませんでした")

    # 4. 全楽曲を取得
    print("4. 全楽曲取得テスト")
    all_songs = db.get_all_songs()
    print(f"   取得した楽曲数: {len(all_songs)}")

    # 5. 検索テスト
    print("5. 検索テスト")
    search_results = db.search_songs(vocal="初音ミク")
    print(f"   初音ミクの楽曲数: {len(search_results)}")

    # 6. 更新テスト
    print("6. 更新テスト")
    test_song.title = "更新されたテスト楽曲"
    update_result = db.update_song(test_song)
    print(f"   更新結果: {update_result}")

    # 更新結果を確認
    updated_song = db.get_song_by_id("test001")
    if updated_song:
        print(f"   更新後のタイトル: {updated_song.title}")

    # 7. 削除テスト
    print("7. 削除テスト")
    delete_result = db.delete_song("test001")
    print(f"   削除結果: {delete_result}")

    # 削除結果を確認
    final_count = db.get_songs_count()
    print(f"   削除後の楽曲数: {final_count}")

    print("=== データベーステスト完了 ===")


if __name__ == "__main__":
    test_database()
