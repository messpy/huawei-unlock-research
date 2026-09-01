# Research notes

本プロジェクトは Fastboot の実機応答を観測するためのものです。

## Candidate formula status

Luhn + sqrt 式による候補生成の主張は **UNVERIFIED** です。根拠、端末世代への適用性、再現性はいずれも確認されていないため、実装していません。候補を使う場合は、所有者が正当に入手・確認した値だけを外部ローカルファイルから明示的に与えてください。

## Response classification

- `command not allowed`: 即停止し pending を保持。
- `OKAY` / `success` / `unlocked`: 成功らしい応答として即停止し pending を保持。
- timeout、端末消失、未知の返答: 失敗に確定せず pending で停止。
- 明示的な invalid / incorrect / mismatch の unlock-code 失敗のみ、失敗確定として次候補へ進行。
