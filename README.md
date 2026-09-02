# Huawei ANE-LX2J Bootloader Unlock Research

Huawei P20 lite 系 `ANE-LX2J`（Android 9 / EMUI 9.1 / Kirin 659）の、所有・管理する実機に対する Fastboot 応答観測プロジェクトです。

## Scope

ユーザーが正当に入手した Unlock Code 候補を、一回あたり最大 4 件だけ送信し、端末の応答を保守的に観測します。無限試行、コード生成、保護回避は行いません。

禁止操作: `flash`、`erase`、`format`、OEMINFO 書換え、firmware 書換え。

## Use

1. 所有者が正当に入手した候補を、ローカルのテキストファイルに 1 行ずつ用意します。実コードは Git に追加しません。
2. 端末を Fastboot モードへ起動し、serial を手動確認します。
3. 実行します。

```sh
./scripts/run.sh --expected-serial SERIAL --codes-file /absolute/path/to/codes.txt
```

初回実行時に serial と候補ファイルのハッシュが `state/probe-state.json` に固定されます。以後、別端末・複数端末・未解決の pending がある状態では送信せず停止します。状態は `./scripts/show_status.sh` で確認できます。

コードの値はログに書かず、送信操作と SHA-256 短縮識別子だけを記録します。
