# Status

## Current progress

- 安全な観測用スキャフォールドを作成済み。
- index=0 と index=1 については過去に実機 Fastboot 試行済み。2026-09-02 の
  限定 probe は Fastboot 端末未検出のため、index=2以降を送信せず停止した。
- Luhn + sqrt 候補式は **UNVERIFIED** で、実装していない。
- Huawei 公式情報を確認済み。現在 Bootloader code は提供されていない。
- `docs/CODES.txt` は手動入力の1行1候補（空行・`#`コメント無視）として、16桁ASCII数字を検証する。
- 実測 index=0 は `check password failed!` のため wrong_code / confirmed failed として解消済み。index=1 は未確定の履歴として保持し、再送・再分類しない。新規 probe は index=2 から開始する。
- timeout 後に確認したところ index=1 は結果未確定。state では過去の未確定記録として
  保持し、index=1 を再送・再分類しない。新規 probe は Fastboot 接続の厳密な事前確認後にのみ
  index=2から開始する。
- 通常 Android 起動後の既知ベースラインは `ro.boot.flash.locked=1`、
  `ro.boot.verifiedbootstate=green`、`ro.boot.vbmeta.device_state=locked`、
  `ro.boot.veritymode=enforcing`、security patch `2020-04-01`。比較用の実測記録として
  `docs/CODEX_FINDINGS.md` に保持する。
- ANE-LX2J / EMUI 9.1.0.324 の custom GSI 利用報告はあるが、C111E37R1P6 完全一致の
  bootloader unlock / Magisk root は **UNVERIFIED**。locked 状態で root 用 image は flash しない。
- PotatoNV は `ANE` / Kirin 65x(A) を対象に含むが、testpoint 経由で NVME `USRKEY` を
  書き換えるため、このリポジトリの安全制約では実行禁止。HCU の ANE-LX1 / Kirin 659
  対応表も ANE-LX2J C111E37R1P6 の適用根拠にはならない。
- ANE-LX2 / EMUI 9.1.0.353 では PotatoNV が FBLOCK 書込み中に失敗した公開報告がある。
  exact ANE-LX2Jではないが、family-level 対応表だけで実行可としない。詳細は
  `docs/POTATONV_SAFETY_RESEARCH.md` に記録する。
- PotatoNV 実行準備は **NOT READY**。Windows/VCOM環境、trusted ANE-LX2J testpoint 図、
  exact復旧経路、USRKEY-only手順、検証済みユーザーデータbackup が未達。詳細は
  `docs/POTATONV_EXECUTION_READINESS.md` に記録する。

## Next action

1. ユーザーが指定したread-onlyコマンドがある場合のみ、固定serialを確認して実行・ログ化する。
2. index=1は再送しない。新規候補はユーザーが具体的なコードとindexを指定した場合に限り、1候補だけ検証する。
3. 端末状態を変更する操作、候補生成、Web検索、分解は行わない。
