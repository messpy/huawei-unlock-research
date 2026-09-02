# Codex Findings

Date: 2026-09-02
Target: Huawei ANE-LX2J
Expected serial: `CHR7N18A24001030`

この文書は、Codex がこの作業環境で実行し、端末から観測した内容だけを記録する。Claude の外部調査・見解・仮説は実測結果として扱わない。

## 実行済みコマンドと観測結果

### ADB から Fastboot への再起動

```text
adb devices
```

stdout:

```text
List of devices attached
CHR7N18A24001030	device
```

その後、以下を実行した。stdout/stderr は空、exit code は 0。

```text
adb -s CHR7N18A24001030 reboot bootloader
```

### index=0

実行コマンド:

```text
fastboot -s CHR7N18A24001030 oem unlock <candidate>
```

stdout/stderr を結合して観測した応答:

```text
FAILED (remote: 'check password failed!')
fastboot: error: Command failed
```

exit code: `1`。timeout なし。

### index=1

実行コマンド:

```text
fastboot -s CHR7N18A24001030 oem unlock <candidate>
```

送信ログ:

```text
[SEND] index=1 code_sha256_12=c08c6ff45c13 command=fastboot oem unlock <redacted>
```

30秒 timeout。Fastboot からの stdout/stderr 応答はなく、`[RECV]` 行は生成されなかった。index=1 は結果未確定として停止した。

## index=1 timeout 後の Fastboot 状態

```text
fastboot devices
```

exit code: `0`、timeout なし。

stdout:

```text
CHR7N18A24001030	 fastboot
```

stderr: 空。

同じ Fastboot セッションで以下を実行した。

```text
fastboot -s CHR7N18A24001030 getvar product
```

10秒 timeout。stdout/stderr は空、exit code は取得不可。

```text
fastboot -s CHR7N18A24001030 oem get-bootinfo
```

10秒 timeout。stdout/stderr は空、exit code は取得不可。

## Fastboot 再起動後の結果

ADB で以下を実行して bootloader へ再起動した。

```text
adb -s CHR7N18A24001030 reboot bootloader
```

再起動後の serial 確認:

```text
fastboot devices
```

exit code: `0`、timeout なし。stdout は `CHR7N18A24001030\t fastboot`、stderr は空。

```text
fastboot -s CHR7N18A24001030 getvar product
```

timeout なし、exit code `0`、stdout は空。stderr:

```text
getvar:product                                     FAILED (remote: 'Command not allowed')
Finished. Total time: 0.006s
```

```text
fastboot -s CHR7N18A24001030 oem get-bootinfo
```

10秒 timeout。stdout/stderr は空、exit code は取得不可。

## 現在の state

```json
{
  "expected_serial": "CHR7N18A24001030",
  "last_sent_index": 1,
  "last_confirmed_failed_index": 0,
  "pending_index": 1,
  "next_index": 1,
  "halt_reason": "fastboot command timed out"
}
```

## 実行していないこと

- index=2 以降の候補送信
- index=1 の再送信
- unlock 以外を含む候補コードの生成・推測
- `flash`、`erase`、`format`、OEMINFO 書換え、firmware 書換え
- Claude が報告した外部情報・仮説を実測として採用すること

## 2026-09-02 限定 probe の実行前確認

この節は外部調査ではなく、この作業環境での実測である。

実行コマンド:

```text
fastboot devices
```

結果: exit code `0`、stdout は空、stderr は空。expected serial
`CHR7N18A24001030` は検出されず、Fastboot 端末が1台だけ存在するという
実行条件を満たさなかった。そのため index=2以降の `fastboot oem unlock` は
**一度も送信していない**。timeout は発生していない。

完全なコマンド結果は Git 管理外の
`logs/limited_probe_preflight_20260902_105528.log` に保存した。

## 通常 Android 起動後の boot-state ベースライン（実測済み）

以下は通常 Android 起動後に読み取り専用の `getprop` で観測済みの比較基準である。
将来の観測値と比較するために保持するが、この記録自体は unlock 成功・失敗の判定を
行うものではない。

```text
ro.boot.flash.locked=1
ro.boot.verifiedbootstate=green
ro.boot.vbmeta.device_state=locked
ro.boot.veritymode=enforcing
ro.build.version.security_patch=2020-04-01
```
