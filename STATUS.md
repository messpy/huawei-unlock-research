# Status

## Current progress

- 安全な観測用スキャフォールドを作成済み。
- 実機へのコマンド送信は未実施。
- Luhn + sqrt 候補式は **UNVERIFIED** で、実装していない。
- Huawei 公式情報を確認済み。現在 Bootloader code は提供されていない。

## Next action

1. 正規に発行されたコードが存在するか、Huawei サポートへ確認する。
2. コードと Fastboot serial が揃った場合のみ、バックアップ後に `scripts/run.sh` を使う。
3. 実行後は `scripts/show_status.sh` と `logs/` を確認する。pending があれば自動継続しない。
