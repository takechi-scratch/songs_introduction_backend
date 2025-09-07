# Songs Databaseドキュメント
このディレクトリ内には、Github Copilotがエージェントとして生成したコードが含まれています。

## 基本的な使用方法

```python
from db.songs import SongsDatabase
from utils.songs_class import Song

# データベースを初期化
db = SongsDatabase("db/data/songs.db")  # デフォルトパス

# 楽曲データを作成
song = Song(
    id="song001",
    title="サンプル楽曲",
    publishedTimestamp=1694000000,
    isPublishedInOriginalChannel=True,
    durationSeconds=240,
    vocal="初音ミク",
    illustrations="イラストレーター名",
    movie="動画制作者名",
    bpm=120,
    mainKey=60,
    chordRate6451=0.5,
    chordRate4561=0.3,
    mainChord="C",
    pianoRate=0.8,
    modulationTimes=2,
    comment="楽曲の説明"
)
```

## 主要な機能

### 1. 楽曲の追加

```python
# 1つの楽曲を追加
success = db.add_song(song)
if success:
    print("楽曲が追加されました")
else:
    print("楽曲は既に存在します")

# 複数の楽曲を一括追加
songs = [song1, song2, song3]
added_count = db.add_songs_batch(songs)
print(f"{added_count}曲が追加されました")
```

### 2. 楽曲の取得

```python
# IDで楽曲を取得
song = db.get_song_by_id("song001")
if song:
    print(f"タイトル: {song.title}")

# 全楽曲を取得
all_songs = db.get_all_songs()
print(f"総楽曲数: {len(all_songs)}")

# 楽曲数のみを取得
count = db.get_songs_count()
print(f"楽曲数: {count}")
```

### 3. 楽曲の検索

```python
# ボーカルで検索
miku_songs = db.search_songs(vocal="初音ミク")

# BPMで検索
fast_songs = db.search_songs(bpm=150)

# 複数条件で検索
specific_songs = db.search_songs(
    vocal="初音ミク",
    mainChord="C",
    isPublishedInOriginalChannel=True
)

# タイトルの部分一致検索
love_songs = db.search_songs(title="恋")
```

### 4. 楽曲の更新

```python
# 楽曲データを変更
song.title = "新しいタイトル"
song.comment = "更新されたコメント"

# データベースに反映
success = db.update_song(song)
if success:
    print("楽曲が更新されました")
else:
    print("楽曲が見つかりません")
```

### 5. 楽曲の削除

```python
# 1つの楽曲を削除
success = db.delete_song("song001")
if success:
    print("楽曲が削除されました")

# 全楽曲を削除（注意：デバッグ用）
db.clear_all_songs()
```

## データベーステーブル構造

```sql
CREATE TABLE songs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publishedTimestamp INTEGER NOT NULL,
    isPublishedInOriginalChannel BOOLEAN NOT NULL,
    durationSeconds INTEGER NOT NULL,
    vocal TEXT NOT NULL,
    illustrations TEXT NOT NULL,
    movie TEXT NOT NULL,
    bpm INTEGER NOT NULL,
    mainKey INTEGER NOT NULL,
    chordRate6451 REAL NOT NULL,
    chordRate4561 REAL NOT NULL,
    mainChord TEXT NOT NULL,
    pianoRate REAL NOT NULL,
    modulationTimes INTEGER NOT NULL,
    comment TEXT NOT NULL
)
```

## 検索可能なフィールド

### 完全一致検索
- `id`, `bpm`, `mainKey`, `modulationTimes`, `durationSeconds`, `publishedTimestamp`
- `isPublishedInOriginalChannel` (boolean)
- `chordRate6451`, `chordRate4561`, `pianoRate` (float)

### 部分一致検索（LIKE）
- `title`, `vocal`, `illustrations`, `movie`, `mainChord`, `comment`

## エラーハンドリング

- 重複するIDの楽曲を追加しようとした場合は、`IntegrityError`がキャッチされ、`False`が返されます
- 存在しない楽曲を更新・削除しようとした場合は、`False`が返されます
- データベースファイルが存在しない場合は、自動的に作成されます

## パフォーマンス考慮事項

- 大量のデータを扱う場合は、`add_songs_batch()`を使用してください
- 検索結果は`publishedTimestamp`の降順（新しい順）でソートされます
- SQLiteの制限により、同時書き込みには対応していません
