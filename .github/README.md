# QEMU fork: GTK `grab-on-focus` (keys reach the guest under the Windows IME)

This is **not** an official QEMU repository. It is a fork of [qemu/qemu](https://github.com/qemu/qemu)
(the official repository is https://gitlab.com/qemu-project/qemu) with one small change to the GTK display,
and a Windows build of `qemu-system-i386` for running BTRON (Cho-Kanji V) guests.

日本語の説明は[下](#日本語)にあります。

## The change

A new GTK display option:

```
-display gtk,grab-on-focus=on
```

It grabs the **keyboard only** while the QEMU window has the keyboard focus, and releases it when the
focus is lost. The pointer is not grabbed.

**Why.** On Windows hosts, when the guest uses an absolute pointing device (vmmouse, USB tablet, ...),
QEMU never grabs the input implicitly, so keys arrive as ordinary window messages and the host input
method (IME) takes them while it is on: the guest gets no keys (or the wrong ones). With a relative
pointer the first click grabs the input, and while grabbed QEMU routes keys through its low-level
keyboard hook (`ui/win32-kbd-hook.c`), which the IME never sees. `grab-on-focus` gives absolute-pointer
guests the same keyboard path, while the mouse still moves freely in and out of the window.

**Status.** Confirmed on a Windows host (Japanese IME, BTRON guest). Not tested on Linux or macOS hosts.
Without the option, QEMU behaves exactly as upstream.

## Links

- Download (Windows x86_64, `qemu-system-i386`, QEMU v11.1.3 + this change):
  [qemu-i386-win64.zip](https://github.com/tadwg/qemu/releases/download/btron-latest/qemu-i386-win64.zip)
  ([release page](https://github.com/tadwg/qemu/releases/tag/btron-latest))
- Details (problem, cause, design, the diff, test status): [btron/README.md](../btron/README.md)
- The patch against v11.1.3: [btron/patches/0001-ui-gtk-grab-on-focus.patch](../btron/patches/0001-ui-gtk-grab-on-focus.patch)
- The same change as a commit on upstream master: branch
  [`grab-on-focus`](https://github.com/tadwg/qemu/tree/grab-on-focus)
- Build: [.github/workflows/btron-windows.yml](workflows/btron-windows.yml) (cross-built with MinGW on Fedora;
  the source is fetched from upstream at build time, so the other files in this branch are an unmodified
  snapshot of upstream master and are not what is built)

## For upstream

This change was written with the help of an AI assistant (Claude) and has **not** been submitted to QEMU.
QEMU does not accept contributions that include AI-generated content (see
`docs/devel/code-provenance.rst` in the QEMU source). If you think upstream QEMU should handle this,
please report it as an issue at https://gitlab.com/qemu-project/qemu/-/issues using the description
above, or write your own implementation. Related reports:
[omacom/try-omarchy-windows#334](https://github.com/omacom/try-omarchy-windows/pull/334) (the same problem
with the SDL display and a Chinese IME),
[qemu-project/qemu#2813](https://gitlab.com/qemu-project/qemu/-/work_items/2813) (a request not to let
the host IME process input).

## 日本語

本家の QEMU のフォークで、公式のリポジトリではありません。GTK 表示に起動オプション `grab-on-focus` を
追加し、Windows のホストで日本語入力 (IME) がオンでも、ゲストにキーが届くようにしました。
超漢字V (BTRON) を QEMU で動かすための Windows 用ビルド (`qemu-system-i386`) を配布しています。

- `-display gtk,grab-on-focus=on` を付けると、QEMU のウィンドウにフォーカスがある間だけキーボードをつかみます
  (ポインタはつかみません)。キーは低レベルのキーボードフックでゲストに送られ、ホストの IME には渡りません
- ダウンロード: [qemu-i386-win64.zip](https://github.com/tadwg/qemu/releases/download/btron-latest/qemu-i386-win64.zip)
- 問題・原因・対策・変更内容 (diff)・確認状況の詳しい説明: [btron/README.md](../btron/README.md)
- 本家の master に当てた同じ変更: [`grab-on-focus` ブランチ](https://github.com/tadwg/qemu/tree/grab-on-focus)
- この変更は AI (Claude) の支援で作成したもので、本家には送っていません。本家に提案する場合は、課題 (issue)
  として報告するか、人が書き直したものを送ってください
- このブランチの `btron/` と `.github/` 以外のファイルは、フォークした時点の本家の master のままです
  (ビルドは本家の v11.1.3 のソースを取得して使います)

QEMU is licensed under the GNU GPL version 2 (`COPYING`); this change and the builds are under the same terms.
