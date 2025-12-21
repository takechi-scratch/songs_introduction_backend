# Songs Databaseドキュメント
このディレクトリ内には、Github Copilotがエージェントとして生成したコードが含まれています。

## 基本的な使用方法

```python
from src.db.songs import SongsDatabase
from src.utils.songs_class import Song

# データベースを初期化
db = SongsDatabase("data/songs.db")  # デフォルトパス

# 楽曲データを作成
song = Song(
    id="song001",
    title="サンプル楽曲",
    publishedTimestamp=1694000000,
    publishedType=1,
    durationSeconds=240,
    vocal=["初音ミク"],
    illustrations=["イラストレーター名"],
    movie=["動画制作者名"],
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
    publishedType=1
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

### 6. 類似楽曲の検索（Similarity Search）

```python
# 楽曲に似た曲を検索
target_song = db.get_song_by_id("song001")
similar_songs = db.find_nearest_song(target_song, limit=10)

# 楽曲IDで類似曲を検索
similar_songs = db.find_nearest_song("song001", limit=5)

# カスタムパラメータで類似度を調整
from src.utils.songs_class import SongsCustomParameters
params = SongsCustomParameters(
    vocal=3.0,
    illustrations=1.0,
    movie=1.0,
    bpm=5.0,
    chordRate6451=3.0,
    chordRate4561=1.0,
    pianoRate=2.0,
    mainKey=2.0,
    mainChord=2.0,
    modulationTimes=1.0
)
similar_songs = db.find_nearest_song("song001", limit=10, parameters=params)
```

### 7. 楽曲データの一括更新（Batch Update）

```python
from src.utils.songs_class import SongVideoData

# 動画情報を更新するデータを作成
updates = [
    SongVideoData(
        id="song001",
        title="更新されたタイトル",
        publishedTimestamp=1694100000,
        durationSeconds=250,
        thumbnailURL="https://example.com/thumb1.jpg"
    ),
    SongVideoData(
        id="song002",
        title="別の更新タイトル",
        publishedTimestamp=1694200000,
        durationSeconds=180,
        thumbnailURL="https://example.com/thumb2.jpg"
    )
]

# 一括更新を実行
success = db.update_songs_data_batch(updates)
if success:
    print("楽曲データが一括更新されました")
```

## データベーステーブル構造

```sql
CREATE TABLE songs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publishedTimestamp INTEGER NOT NULL,
    publishedType INTEGER NOT NULL,
    durationSeconds INTEGER,
    thumbnailURL TEXT,
    vocal LIST,
    illustrations LIST,
    movie LIST,
    bpm INTEGER,
    mainKey INTEGER,
    chordRate6451 REAL,
    chordRate4561 REAL,
    mainChord TEXT,
    pianoRate REAL,
    modulationTimes INTEGER,
    comment TEXT
)
```

## フィールド説明

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| id | TEXT | ✓ | 楽曲の一意な識別子 |
| title | TEXT | ✓ | 楽曲タイトル |
| publishedTimestamp | INTEGER | ✓ | 公開日時（Unixタイムスタンプ） |
| publishedType | INTEGER | ✓ | 公開タイプ（0: 再投稿, 1: オリジナルチャンネル） |
| durationSeconds | INTEGER | | 楽曲の長さ（秒） |
| thumbnailURL | TEXT | | サムネイルURL |
| vocal | LIST | | ボーカル名のリスト（例: ["初音ミク"]） |
| illustrations | LIST | | イラストレーター名のリスト |
| movie | LIST | | 動画制作者名のリスト |
| bpm | INTEGER | | テンポ（BPM） |
| mainKey | INTEGER | | 主調（MIDIノート番号） |
| chordRate6451 | REAL | | コード進行6451の出現率 |
| chordRate4561 | REAL | | コード進行4561の出現率 |
| mainChord | TEXT | | 主要コード |
| pianoRate | REAL | | ピアノ音色の使用率 |
| modulationTimes | INTEGER | | 転調回数 |
| comment | TEXT | | コメント・説明 |

## 検索可能なフィールド

### 完全一致検索
- `id`, `bpm`, `mainKey`, `modulationTimes`, `durationSeconds`, `publishedTimestamp`
- `publishedType` (integer: 0 or 1)
- `chordRate6451`, `chordRate4561`, `pianoRate` (float)

### 部分一致検索（LIKE）
- `title`, `mainChord`, `comment`

### リスト内検索
- `vocal`, `illustrations`, `movie` - リスト内の値で検索

## エラーハンドリング

- 重複するIDの楽曲を追加しようとした場合は、`IntegrityError`がキャッチされ、`False`が返されます
- 存在しない楽曲を更新・削除しようとした場合は、`False`が返されます
- データベースファイルが存在しない場合は、自動的に作成されます

## パフォーマンス考慮事項

- 大量のデータを扱う場合は、`add_songs_batch()`を使用してください
- 検索結果は`publishedTimestamp`の降順（新しい順）でソートされます
- SQLiteの制限により、同時書き込みには対応していません
