# Status

## Current progress

- 安全な観測用スキャフォールドを作成済み。
- 実機へのコマンド送信は未実施。
- Luhn + sqrt 候補式は **UNVERIFIED** で、実装していない。

## Next action

1. 所有端末をバックアップし Fastboot モードへ起動する。
2. `fastboot devices` で serial を手動確認する。
3. 正当に入手した候補のみをローカルファイルに記入する。
4. `scripts/run.sh` に serial と候補ファイルを渡し、`yes` を入力する。
5. 実行後は `scripts/show_status.sh` と `logs/` を確認する。pending があれば自動継続しない。
