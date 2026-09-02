# Status

## Current progress

- 安全な観測用スキャフォールドを作成済み。
- index=0 と index=1 については過去に実機 Fastboot 試行済み。2026-09-02 の
  限定 probe は Fastboot 端末未検出のため、index=2以降を送信せず停止した。
- Luhn + sqrt 候補式は **UNVERIFIED** で、実装していない。
- Huawei 公式情報を確認済み。現在 Bootloader code は提供されていない。
- `docs/CODES.txt` は手動入力の1行1候補（空行・`#`コメント無視）として、16桁ASCII数字を検証する。
- 実測 index=0 は `check password failed!` のため wrong_code / confirmed failed として解消済み。次回は index=1 から開始する（未送信）。
- timeout 後に確認したところ index=1 は結果未確定。state では過去の未確定記録として
  保持し、index=1 を再送・再分類しない。新規 probe は Fastboot 接続の厳密な事前確認後にのみ
  index=2から開始する。
- 通常 Android 起動後の既知ベースラインは `ro.boot.flash.locked=1`、
  `ro.boot.verifiedbootstate=green`、`ro.boot.vbmeta.device_state=locked`、
  `ro.boot.veritymode=enforcing`、security patch `2020-04-01`。比較用の実測記録として
  `docs/CODEX_FINDINGS.md` に保持する。
- ANE-LX2J / EMUI 9.1.0.324 の custom GSI 利用報告はあるが、C111E37R1P6 完全一致の
  bootloader unlock / Magisk root は **UNVERIFIED**。locked 状態で root 用 image は flash しない。

## Next action

1. HiSuite の **Update** 画面だけで対象端末向けに表示される model/build 情報を記録する。
   Update、Rollback、System Recovery、download、restore は選択しない。
2. exact firmware の整合性が確認できるまで root/recovery/GSI image を flash しない。
3. unlock probe を再開する場合でも index=1 は送信・再分類せず、index=2から最大4候補に限る。
