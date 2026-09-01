# Research notes

本プロジェクトは Fastboot の実機応答を観測するためのものです。

## Official availability check (2026-09-01)

Huawei の公式サポート記事は、Bootloader code を現在いかなる場合も提供していないと明記しています（[Huawei Support](https://consumer.huawei.com/latin/support/content/es-us00771596/)）。したがって、正規に発行されたコードが手元にない状態で推測候補を送信する根拠は確認できません。ANE-LX2J 自体は Huawei 日本のソフトウェア一覧に掲載されています（[Huawei Japan](https://consumer.huawei.com/jp/support/content/ja-jp00747265/)）。

## Candidate formula status

Luhn + sqrt 式による候補生成の主張は **UNVERIFIED** です。根拠、端末世代への適用性、再現性はいずれも確認されていないため、実装していません。候補を使う場合は、所有者が正当に入手・確認した値だけを外部ローカルファイルから明示的に与えてください。

## Response classification

- `command not allowed`: 即停止し pending を保持。
- `OKAY` / `success` / `unlocked`: 成功らしい応答として即停止し pending を保持。
- timeout、端末消失、未知の返答: 失敗に確定せず pending で停止。
- 明示的な invalid / incorrect / mismatch の unlock-code 失敗のみ、失敗確定として次候補へ進行。
