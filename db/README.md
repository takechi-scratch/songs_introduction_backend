# Songs Databaseドキュメント

**このドキュメントはGitHub Copilotエージェントによって作成されました。**

このディレクトリには、楽曲データベースの管理機能が含まれています。

## 基本的な使用方法

```python
from db.songs_database import SongsDatabase
from utils.songs_class import Song

# データベースを初期化
db = SongsDatabase("db/data/songs.db")  # デフォルトパス

# 楽曲データを作成
song = Song(
    id="song001",
    title="サンプル楽曲",
    publishedTimestamp=1694000000,
    publishedType=0,  # 0: オリジナルチャンネル, 1: その他
    durationSeconds=240,
    thumbnailURL="https://example.com/thumbnail.jpg",
    vocal=["初音ミク"],  # リスト形式
    illustrations=["イラストレーター名"],  # リスト形式
    movie=["動画制作者名"],  # リスト形式
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

# タイトルの部分一致検索
love_songs = db.search_songs(title="恋")

# 複数条件で検索
specific_songs = db.search_songs(
    vocal="初音ミク",
    mainChord="C",
    publishedType=0
)

# 期間指定検索
recent_songs = db.search_songs(
    publishedAfter=1640000000,  # UNIXタイムスタンプ
    publishedBefore=1700000000
)

# ソート順を指定
sorted_songs = db.search_songs(
    order="bpm",  # ソート項目
    asc=True      # 昇順
)
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

**注意**: `vocal`, `illustrations`, `movie` はLIST型（JSON配列として保存）

## フィールドの説明

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| id | TEXT | ○ | YouTube動画ID（プライマリキー） |
| title | TEXT | ○ | 楽曲タイトル |
| publishedTimestamp | INTEGER | ○ | 公開日時（UNIXタイムスタンプ） |
| publishedType | INTEGER | ○ | 公開タイプ（0: オリジナルチャンネル, 1: その他） |
| durationSeconds | INTEGER | - | 動画の長さ（秒） |
| thumbnailURL | TEXT | - | サムネイルURL |
| vocal | LIST | - | ボーカル名のリスト |
| illustrations | LIST | - | イラストレーター名のリスト |
| movie | LIST | - | 動画制作者名のリスト |
| bpm | INTEGER | - | テンポ（BPM） |
| mainKey | INTEGER | - | 主音（MIDIノート番号） |
| chordRate6451 | REAL | - | コード進行6451の出現率 |
| chordRate4561 | REAL | - | コード進行4561の出現率 |
| mainChord | TEXT | - | 主コード |
| pianoRate | REAL | - | ピアノ使用率 |
| modulationTimes | INTEGER | - | 転調回数 |
| comment | TEXT | - | コメント |

## 検索可能なフィールド

### 完全一致検索
- `id`, `mainChord`, `mainKey`, `publishedType`

### 部分一致検索（LIKE）
- `title`, `comment`

### リスト内検索
- `vocal`, `illustrations`, `movie` - リスト内に指定した値が含まれるかを検索

### 範囲検索
- `publishedAfter`, `publishedBefore` - 公開日時の範囲検索

### ソート
- `order` パラメータで任意のフィールドでソート可能
- `asc` パラメータで昇順/降順を指定（デフォルト: 降順）

## エラーハンドリング

- 重複するIDの楽曲を追加しようとした場合は、`IntegrityError`がキャッチされ、`False`が返されます
- 存在しない楽曲を更新・削除しようとした場合は、`False`が返されます
- データベースファイルが存在しない場合は、自動的に作成されます

## 類似楽曲検索

曲調が似ている楽曲を検索する高度な機能も提供されています：

```python
# 指定した楽曲に似た楽曲を検索
similar_songs = db.find_nearest_song(
    target="song001",  # 楽曲IDまたはSongオブジェクト
    limit=10,          # 取得する楽曲数
    parameters=None,   # カスタムパラメータ（オプション）
    is_reversed=False  # スコアの昇順/降順
)

# 結果はSongInQueueオブジェクトのリストで返される
for song_in_queue in similar_songs:
    print(f"{song_in_queue.song.title}: {song_in_queue.score}")
```

## バッチ更新

YouTube Data APIから取得したデータで一括更新が可能です：

```python
from utils.songs_class import SongVideoData

# 更新データのリストを作成
update_data = [
    SongVideoData(
        id="song001",
        title="更新されたタイトル",
        publishedTimestamp=1694000000,
        durationSeconds=240,
        thumbnailURL="https://example.com/new_thumbnail.jpg"
    ),
    # ... more songs
]

# バッチ更新を実行
success = db.update_songs_data_batch(update_data)
```

## パフォーマンス考慮事項

- 大量のデータを扱う場合は、`add_songs_batch()`を使用してください
- 検索結果はデフォルトで`publishedTimestamp`の降順（新しい順）でソートされます
- SQLiteの制限により、同時書き込みには対応していません
- 類似楽曲検索は全楽曲を走査するため、データ量が多い場合は時間がかかる可能性があります
