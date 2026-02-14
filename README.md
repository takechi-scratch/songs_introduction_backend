# MIMIさん全曲紹介 バックエンド

https://mimi-api.takechi.f5.si/docs/

## 技術スタック
- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)

など。ライセンスなどは [クレジット](https://mimi.takechi.f5.si/docs/credits) を参照してください。

## 開発のしかた
0. 仮想環境を作成・必要なパッケージをインストール。
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
0. /.env.example を参考に、環境変数を設定。

1. `source .venv/bin/activate`で仮想環境を起動。
2. `python main.py`でAPIサーバーを起動。（開発モードなら、ホットリロードにも対応）

## デプロイ
MIMIさん全曲紹介の本番環境では、VPSにファイルをコピーし、systemdでサービスとして登録しています。

## クレジット
本当にありがとうございます。

https://mimi.takechi.f5.si/docs/credits
