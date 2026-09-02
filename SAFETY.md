# Safety

- 所有・管理する端末にだけ使用すること。
- `flash`、`erase`、`format`、OEMINFO 書換え、firmware 書換えは禁止。
- 一回の実行は最大 4 回で終了する。
- 実行前に `yes` の明示入力が必須。
- Fastboot 接続端末が 1 台かつ固定 serial と一致することを毎回確認する。
- 送信前に pending 状態を atomic write する。
- 不明・timeout・切断・成功らしい応答・`command not allowed` はすべて停止する。
- Unlock がデータ消去を伴う可能性を前提にバックアップ後に行う。

pending を自動解消・再送しません。ログと端末状態を人間が確認してください。

## 固定運用方針（2026-09-02以降）

- Codex側の作業は無料・非破壊・分解なしとする。Web検索・外部調査は行わない。
- 実行するのはユーザーが指定したコマンドだけで、結果を日時付きログへ保存する。
- testpoint、PotatoNV、DOWNLOAD_VCOM、NV/USRKEY/FBLOCK、FRP/OEMINFO、unlock、
  flash/erase/format、firmware/recovery/boot書込み、root化は禁止する。
- Fastbootはread-only確認、またはユーザーが明示した具体的な1候補の検証だけ許可する。
- 候補コードの生成・選定・回数判断は行わない。index=0は確定失敗、index=1はtimeout不明で再送しない。
- ユーザー指定の候補を検証する場合も、接続確認、固定serial確認、1候補、完全ログ、応答後確認で終了する。
