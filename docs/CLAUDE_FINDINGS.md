# Claude Findings

Date: 2026-09-02
Target: Huawei P20 lite ANE-LX2J
Build: ANE-LX2J 9.1.0.324(C111E37R1P6)
SoC: Kirin 659 / hi6250

# 1. 前提となる実機観測

## index=0

`fastboot oem unlock <candidate>` を実行した結果:

```text
FAILED (remote: 'check password failed!')
fastboot: error: Command failed
```

このためindex=0は不正解として確認済み。

現在:

```text
last_confirmed_failed_index=0
```

## index=1

index=1の候補を送信したところ:

```text
[SEND] index=1
↓
30秒 timeout
↓
[RECV]なし
```

となった。

現在のstate:

```text
last_sent_index=1
last_confirmed_failed_index=0
pending_index=1
next_index=1
```

index=1は不正解とは確定していない。

index=2以降は未送信。

## index=1 timeout直後

以下では端末が認識された:

```text
fastboot devices

CHR7N18A24001030 fastboot
```

しかし同一Fastbootセッションで:

```text
fastboot getvar product
→ 10秒timeout

fastboot oem get-bootinfo
→ 10秒timeout
```

となった。

USB/Fastbootデバイスとしての列挙は残っていたが、
Fastbootコマンド処理が応答しない状態になっていた。

## Fastbootへ入り直した後

端末を再起動し、再びFastboot & Rescue Modeへ入れた。

その後:

```text
fastboot -s CHR7N18A24001030 getvar product
```

はtimeoutせず、約6msで:

```text
FAILED (remote: 'Command not allowed')
Finished. Total time: 0.006s
```

を返した。

したがって、index=1送信後に発生した
`getvar product` のtimeoutは恒久的なFastboot故障ではなかった。

一方:

```text
fastboot -s CHR7N18A24001030 oem get-bootinfo
```

はFastbootへ入り直した後も10秒timeoutした。

このため `oem get-bootinfo` のtimeoutだけを、
Fastboot全体の異常判定には使用できない。

# 2. Claudeの結論

Claudeの主要な結論は以下。

**index=1の30秒timeoutをBootloader Unlock成功の兆候として扱うべきではない。**

現時点ではindex=1の正誤は判定不能。

timeoutだけを理由として、

```text
index=1 = correct unlock code
```

とは判断できない。

# 3. Claudeが調査した外部情報

ClaudeはXDA Forums上に、
Huawei端末のBootloader Unlock関連コマンドについて、
結果が返るまで意図的な遅延が存在するという投稿を発見したと報告している。

Claudeが紹介した投稿では、
ある端末についてコマンド実行後に結果が返るまで
約5秒の遅延が組み込まれているとされている。

その投稿者は、この遅延について
Bootloader Unlock Codeのブルートフォース試行を遅くするための
仕組みではないかと推測している。

ClaudeはさらにGitHub上に:

```text
Avoiding 5 attempts 30s delay
```

というタイトルの関連Issueが存在すると報告した。

Claudeはこれらの情報から、
Huawei BootloaderにはUnlock Codeの大量試行を妨げる
意図的なdelay / anti-bruteforce mechanismが存在する可能性がある、
と評価している。

# 4. Claudeによるindex=1 timeoutの評価

Claudeは以下の仮説を比較した。

## 仮説A: 正しいUnlock Codeだった

現時点では証拠不足。

timeoutそのものはUnlock成功を示す直接的な証拠ではない。

## 仮説B: Wrong Code + intentional delay

Claudeが発見したXDA/GitHub情報と整合する。

Claudeはこの可能性を有力と評価している。

ただしANE-LX2Jで同じdelay機構が存在することは未確認。

## 仮説C: Fastboot anti-bruteforce mechanism

Huawei側が試行回数などに応じて
Fastboot処理を一定時間遅延させている可能性。

外部コミュニティ情報とは整合するが、
この端末で実証されていない。

## 仮説D: Fastboot firmware hang

今回の実測とも整合する。

index=1送信後、

```text
fastboot devices
```

は動作する一方で、

```text
getvar product
```

までtimeoutする状態になったため、
Fastbootのコマンド処理レイヤーが一時的に停止していた可能性がある。

## 仮説E: USB/Fastboot client issue

完全には排除できない。

ただし `fastboot devices` では端末が認識され続けていたため、
単純なUSB切断だけでは今回の挙動を説明しにくい。

# 5. Claudeの総合評価

Claudeは、

```text
index=1 timeout = Unlock成功
```

という解釈を支持していない。

現時点では:

```text
index=1 = UNKNOWN / PENDING
```

として維持するのが適切。

また、index=0とindex=1の応答差については、

「正しいコードだったため処理が変化した」

よりも、

「Huawei側の意図的な遅延」
「anti-bruteforce」
「Fastboot firmware hang」

などを先に検討すべきとしている。

# 6. 5秒 / 30秒delayについての注意

Claudeは以下の外部情報を報告した:

- XDA上の約5秒delayに関する投稿
- GitHub上の「Avoiding 5 attempts 30s delay」というIssue

ただし、これらについてプロジェクト側ではまだ元情報を独立検証していない。

特にGitHub Issueのタイトルだけでは:

- 5回ごとに30秒delayなのか
- 5回失敗した後に30秒delayなのか
- 各試行にdelayが入るのか
- Fastboot全体が30秒停止するのか
- 自動再起動等を含むのか

までは確定できない。

また、それらが:

```text
ANE-LX2J
Kirin 659
EMUI 9.1
ANE-LX2J 9.1.0.324(C111E37R1P6)
```

にそのまま適用できるかも未確認。

したがって現時点では:

```text
CLAUDE REPORTED
INDEPENDENTLY UNVERIFIED
```

として扱う。

# 7. 16桁Unlock Code前提について

Claudeはこの前提について評価を下げるべきと指摘した。

実機で確認できた事実は:

```text
16桁の候補を送信
↓
check password failed!
```

だけ。

これは:

```text
ANE-LX2JのUnlock Codeは16桁
```

という証明にはならない。

Huawei側の実装が入力長不正でも専用エラーを返さず、
単純なpassword mismatchとして:

```text
check password failed!
```

を返す可能性があるため。

したがって16桁という前提は現時点では未実証。

# 8. Luhn + sqrt候補生成方式について

現在検討されている候補生成方式:

```text
Luhn-like IMEI sum
+
floor(sqrt(IMEI) * 1024)
```

についても、ANE-LX2JのBootloader Unlock Codeとの関連は
実証されていない。

Claudeの評価:

```text
UNVERIFIED
```

この方式の出典・アルゴリズム・対象Huawei世代を
独立調査する必要がある。

# 9. Claudeが提案した非破壊確認

Claudeはindex=1を再送する前に、
通常Androidを起動してBootloader関連propertyを確認することを提案した。

候補:

```text
adb shell getprop ro.boot.flash.locked
adb shell getprop ro.boot.verifiedbootstate
```

特に:

```text
ro.boot.flash.locked
```

について、値が取得できる場合はBootloader Lock Stateを判断する材料になる可能性がある。

また、通常起動時にBootloader Unlock警告画面が表示されるかどうかを
目視確認する方法も補助的な確認手段として提案された。

ただし、これらpropertyがANE-LX2J / EMUI 9.1で
どの程度信頼できるかについても独立確認が必要。

# 10. Claudeから見た次の調査事項

以下を独立して調査する必要がある。

1. XDAの約5秒delay報告の元投稿
2. GitHubの「Avoiding 5 attempts 30s delay」の元Issue
3. 5 attempts / 30s delayの正確な意味
4. ANE-LX2J / P20 lite / Kirin659への適用可能性
5. `check password failed!` の実装上の意味
6. Huaweiのこの世代のUnlock Codeが16桁である根拠
7. Luhn + sqrt方式の出典
8. `ro.boot.flash.locked` のANE-LX2Jでの信頼性
9. `ro.boot.verifiedbootstate` のANE-LX2Jでの信頼性
10. index=1 timeoutの原因

# 11. 現時点の安全方針

Claudeの調査を踏まえても、現在は:

```text
last_sent_index=1
last_confirmed_failed_index=0
pending_index=1
next_index=1
```

を維持する。

index=1をfailedにしない。

index=1をsuccessにも分類しない。

index=2へ進めない。

外部情報を独立検証してから次の実機操作を判断する。
