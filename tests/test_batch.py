"""
バッチ追加機能のテストスクリプト

このテストは GitHub Copilot エージェントによって作成されました。
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.songs_database import SongsDatabase
from utils.songs_class import Song


def test_batch_add():
    # データベースを初期化
    db = SongsDatabase("db/data/test_batch_songs.db")
    
    # 既存のデータをクリア
    db.clear_all_songs()

    # テスト用の複数のSongオブジェクトを作成
    test_songs = [
        Song(
            id="batch001",
            title="バッチテスト楽曲1",
            publishedTimestamp=1694000000,
            publishedType=0,
            durationSeconds=240,
            thumbnailURL="https://example.com/thumb1.jpg",
            vocal=["初音ミク"],
            illustrations=["テストイラスト1"],
            movie=["テスト動画1"],
            bpm=120,
            mainKey=60,
            chordRate6451=0.5,
            chordRate4561=0.3,
            mainChord="C",
            pianoRate=0.8,
            modulationTimes=2,
            comment="バッチテスト楽曲1です",
        ),
        Song(
            id="batch002",
            title="バッチテスト楽曲2",
            publishedTimestamp=1694001000,
            publishedType=1,
            durationSeconds=180,
            thumbnailURL="https://example.com/thumb2.jpg",
            vocal=["鏡音リン"],
            illustrations=["テストイラスト2"],
            movie=["テスト動画2"],
            bpm=140,
            mainKey=62,
            chordRate6451=0.6,
            chordRate4561=0.4,
            mainChord="D",
            pianoRate=0.7,
            modulationTimes=1,
            comment="バッチテスト楽曲2です",
        ),
        Song(
            id="batch003",
            title="バッチテスト楽曲3",
            publishedTimestamp=1694002000,
            publishedType=0,
            durationSeconds=300,
            thumbnailURL="https://example.com/thumb3.jpg",
            vocal=["巡音ルカ"],
            illustrations=["テストイラスト3"],
            movie=["テスト動画3"],
            bpm=100,
            mainKey=64,
            chordRate6451=0.4,
            chordRate4561=0.5,
            mainChord="E",
            pianoRate=0.9,
            modulationTimes=3,
            comment="バッチテスト楽曲3です",
        ),
    ]

    print("=== バッチ追加テスト開始 ===")

    # バッチ追加テスト
    print("1. バッチ追加テスト")
    success_count = db.add_songs_batch(test_songs)
    print(f"   追加成功数: {success_count}")
    assert success_count == 3, f"バッチ追加の結果が正しくありません（期待: 3, 実際: {success_count}）"

    # 全楽曲数を確認
    total_count = db.get_songs_count()
    print(f"   総楽曲数: {total_count}")
    assert total_count == 3, f"総楽曲数が正しくありません（期待: 3, 実際: {total_count}）"

    # 全楽曲を取得して表示
    print("2. 追加された楽曲一覧")
    all_songs = db.get_all_songs()
    assert len(all_songs) == 3, f"取得した楽曲数が正しくありません（期待: 3, 実際: {len(all_songs)}）"
    
    for song in all_songs:
        print(f"   ID: {song.id}, タイトル: {song.title}, ボーカル: {song.vocal}")
        assert song.vocal is not None and len(song.vocal) > 0, f"ボーカル情報が正しくありません（{song.id}）"

    # 重複追加テスト
    print("3. 重複追加テスト")
    duplicate_success = db.add_songs_batch(test_songs)
    print(f"   重複追加成功数: {duplicate_success}")
    assert duplicate_success == 0, f"重複追加のテストが正しくありません（期待: 0, 実際: {duplicate_success}）"

    final_count = db.get_songs_count()
    print(f"   最終楽曲数: {final_count}")
    assert final_count == 3, f"最終楽曲数が正しくありません（期待: 3, 実際: {final_count}）"

    # 検索テスト
    print("4. 検索テスト")
    miku_songs = db.search_songs(vocal="初音ミク")
    print(f"   初音ミクの楽曲数: {len(miku_songs)}")
    assert len(miku_songs) == 1, f"初音ミク検索の結果が正しくありません（期待: 1, 実際: {len(miku_songs)}）"

    print("=== バッチ追加テスト完了 ===")
    print("✓ すべてのテストに合格しました")


if __name__ == "__main__":
    test_batch_add()
