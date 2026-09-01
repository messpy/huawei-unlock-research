# Safety

- 所有・管理する端末にだけ使用すること。
- `flash`、`erase`、`format`、OEMINFO 書換え、firmware 書換えは禁止。
- 一回の実行は最大 5 回で終了する。
- 実行前に `yes` の明示入力が必須。
- Fastboot 接続端末が 1 台かつ固定 serial と一致することを毎回確認する。
- 送信前に pending 状態を atomic write する。
- 不明・timeout・切断・成功らしい応答・`command not allowed` はすべて停止する。
- Unlock がデータ消去を伴う可能性を前提にバックアップ後に行う。

pending を自動解消・再送しません。ログと端末状態を人間が確認してください。
