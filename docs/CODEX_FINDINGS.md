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

## 2026-09-02 ADB read-only 再確認

`adb devices` は expected serial `CHR7N18A24001030` を唯一の `device` として返した。
以下の read-only `getprop` はすべて exit code `0` だった。

```text
ro.product.model=ANE-LX2J
ro.build.version.release=9
ro.build.version.emui=EmotionUI_9.1.0
ro.build.version.security_patch=2020-04-01
ro.boot.flash.locked=1
ro.boot.verifiedbootstate=green
ro.boot.vbmeta.device_state=locked
ro.boot.veritymode=enforcing
```

完全なコマンド結果は Git 管理外の `logs/boot_state_20260902_130523.log` に保存した。
この確認では書き込み、再起動、Fastboot、unlock、flash を実行していない。

## haexhub index=2 fresh Fastboot session再検証（2026-09-02）

AndroidからFastbootへ移行し、対象端末1台とSHA-256先頭12桁 `7004ad3a3cfa` を確認後、index=2を1回送信した。

```text
[STDOUT] (empty)
[STDERR]
FAILED (remote: 'check password failed!')
fastboot: error: Command failed
exit_code=1
elapsed_seconds=0
timeout=no
classification=confirmed_failed
```

ログ: `logs/index2_fresh_recheck_20260902_182031.log`。index=3以降や追加操作は実行していない。

## haexhub index=3 probe（2026-09-02）

ADBで対象端末1台とlocked/green状態を確認後、Fastbootへ移行し、SHA-256先頭12桁
`3eb5c2f1956e`を確認してindex=3を1回送信した。

```text
[STDOUT] (empty)
[STDERR]
FAILED (remote: 'check password failed!')
fastboot: error: Command failed
exit_code=1
elapsed_seconds=0
timeout=no
classification=confirmed_failed
```

ログ: `logs/index3_probe_20260902_183526.log`。index=4以降や追加操作は実行していない。

## haexhub index=2 probe（2026-09-02）

Fastboot端末1台と候補SHA-256先頭12桁 `7004ad3a3cfa` を確認後、ユーザー指定候補を1回送信した。

```text
[STDOUT] (empty)
[STDERR] (empty)
exit_code=124
timeout=yes
classification=unknown
```

ログ: `logs/haexhub_index2_20260902_172607.log`。index=3以降、再送、追加の状態変更は実行していない。

## 2026-09-02 read-only hardware/path inventory

唯一の expected serial `CHR7N18A24001030` が `device` 状態で1台だけ存在することを確認した。
新規取得値は `ro.product.board=ANE`、`ro.board.platform=hi6250`、`ro.hardware=hi6250`、
`ro.boot.hardware=hi6250`、`ro.product.device=HWANE`。`ro.boot.boardid` と `ro.boot.hwrev` は
空（exit 0）、`settings get global oem_unlock_allowed` は `null`（exit 0）だった。
既知の build と locked/green/enforcing baseline は再確認値として同一だった。

`cat /proc/partitions` は permission denied（exit 1）。by-name listing は読み取り可能で、
`frp` を含むリンク一覧をログに保存した。これらは領域の読み出し・書き込みを意味しない。

PotatoNV 2022.03 x86 ZIP の展開先は `/private/tmp/potatonv-2022.03`。ZIP SHA-256 は
`98344a77eeddee99f4ca145c586a6656b7f98da0cc04be1007dc102ec62ae416`。一覧と
`hisi65x_a`/`hisi65x_b` の存在を記録した。ログは `logs/read_only_inventory_20260902_152356.log`。
ADB、端末状態、PotatoNVには変更を加えていない。

## haexhub index=1 再送記録（2026-09-02）

ユーザー指定により、Fastboot端末1台を確認後、候補1件を一度だけ送信した。
候補自体は記録せず、SHA-256先頭12桁 `a456ce19794d` のみ保存する。

```text
[STDOUT] (empty)
[STDERR]
FAILED (remote: 'check password failed!')
fastboot: error: Command failed
exit_code=1
timeout=no
classification=confirmed_failed
```

ログ: `logs/haexhub_index1_20260902_171741.log`。追加候補、再送、flash、erase、
reboot、設定変更は実行していない。

## OEM unlock / FRP 関連 property の read-only 確認

唯一の expected ADB serial を確認した上で、以下を取得した。

```text
ro.oem_unlock_supported=<empty>
settings global oem_unlock_allowed=1
ro.frp.pst=/dev/block/bootdevice/by-name/frp
```

これらは Fastboot unlock の実行可否、FRP lock state、testpoint/NV操作の安全性を
確定するものではない。書き込み、設定変更、再起動、Fastboot、unlock、flash は実行していない。

## macOS HiSuite の確認

macOS 版 HiSuite を起動して端末接続を確認したが、アプリ内に
`Update` / `システム更新` 画面は存在しなかった。したがって、このクライアントから
firmware 提示情報は取得していない。Update、Rollback、System Recovery、download、
restore は実行していない。

## 端末情報画面の read-only 確認

ADB の `exec-out screencap` で端末情報画面を一時的に確認した。画面上で
model `ANE-LX2J`、build `9.1.0.324(C111E37R1P6)`、EMUI `9.1.0`、Android `9`、
security patch `2020-04-01`、CPU `HiSilicon Kirin 659` を確認した。

画面に IMEI が表示されたため、スクリーンショットは記録・Git管理せず、その場で削除した。
この確認では端末への書き込みや設定変更をしていない。

## OTA 識別用 build property の read-only 確認

唯一の expected ADB serial を確認した上で、以下を read-only で取得した。

```text
ro.build.version.incremental=9.1.0.324C111
ro.build.display.id=ANE-LX2J 9.1.0.324(C111E37R1P6)
ro.build.version.base_os=HUAWEI/ANE-LX2J/HWANE:9/HUAWEIANE-LX2J/9.1.0.282C111:user/release-keys
```

この確認では書き込み、再起動、Fastboot、unlock、flash を実行していない。
