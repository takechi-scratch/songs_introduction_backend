# songs_introduction_backend

**このREADMEは GitHub Copilot エージェントによって更新されました。**

MIMIさん全曲分析のバックエンドAPI

## 概要

このプロジェクトは、楽曲データベースを管理し、類似楽曲の検索やYouTube Data APIとの連携を提供するFastAPIベースのバックエンドAPIです。

## 主な機能

- 楽曲データのCRUD操作（作成・読取・更新・削除）
- 高度な検索機能（ボーカル、BPM、コード進行などで検索）
- 類似楽曲の自動検索（曲調分析アルゴリズム）
- YouTube Data APIとの連携（動画情報の自動取得・更新）
- YouTubeプレイリストの自動作成
- Firebase Authenticationによる認証

## 技術スタック

- **言語**: Python 3.12
- **Webフレームワーク**: FastAPI
- **データベース**: SQLite3
- **認証**: Firebase Authentication
- **外部API**: YouTube Data API v3
- **スケジューリング**: APScheduler

## セットアップ

### 必要条件

- Python 3.12以上
- pip

### インストール

1. リポジトリをクローン

```bash
git clone https://github.com/takechi-scratch/songs_introduction_backend.git
cd songs_introduction_backend
```

2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

3. 環境変数を設定

`.env.example`を`.env`にコピーして、必要な環境変数を設定してください。

```bash
cp .env.example .env
```

4. データベースの初期化

アプリケーションを起動すると、自動的にデータベースが初期化されます。

### 開発環境での実行

```bash
ENV=development python main.py
```

サーバーは`http://localhost:8000`で起動します。

## API ドキュメント

サーバー起動後、以下のURLでAPIドキュメントを確認できます：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## データベース構造

詳細なデータベース構造とAPIの使用方法については、[db/README.md](db/README.md)を参照してください。

### 主なテーブル: songs

| フィールド名 | 型 | 必須 | 説明 |
|------------|-----|------|------|
| id | TEXT | ○ | YouTube動画ID（プライマリキー） |
| title | TEXT | ○ | 楽曲タイトル |
| publishedTimestamp | INTEGER | ○ | 公開日時（UNIXタイムスタンプ） |
| publishedType | INTEGER | ○ | 公開タイプ（0: オリジナル, 1: その他） |
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

## テスト

プロジェクトには以下のテストが含まれています：

### データベーステスト

基本的なCRUD操作をテストします：

```bash
PYTHONPATH=. python tests/test_db.py
```

### バッチ追加テスト

複数の楽曲を一括で追加する機能をテストします：

```bash
PYTHONPATH=. python tests/test_batch.py
```

## プロジェクト構造

```
.
├── db/                      # データベース関連
│   ├── songs_database.py    # データベースクラス
│   ├── database_migration.py # データベース移行スクリプト
│   ├── update_youtube_data.py # YouTube データ更新
│   └── README.md            # データベースドキュメント
├── utils/                   # ユーティリティモジュール
│   ├── songs_class.py       # 楽曲データモデル
│   ├── youtube_data_api.py  # YouTube API クライアント
│   ├── auth.py              # 認証機能
│   ├── fastapi_models.py    # FastAPIモデル定義
│   └── config.py            # 設定ファイル
├── scripts/                 # スクリプト
│   ├── load_songs.py        # 楽曲データのロード
│   ├── export_songs.py      # 楽曲データのエクスポート
│   └── songs_cli.py         # CLI ツール
├── tests/                   # テストファイル
│   ├── test_db.py           # データベーステスト
│   └── test_batch.py        # バッチ追加テスト
├── main.py                  # メインアプリケーション
└── requirements.txt         # Python依存関係

```

## ライセンス

MIT License

## 作者

takechi ([@takechi_scratch](https://x.com/takechi_scratch/))