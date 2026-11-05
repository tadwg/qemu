# QEMU (qemu-system-i386) の Windows 向けビルド

超漢字V (BTRON3) を Windows 上の QEMU で動かすための、QEMU のビルドです。
GitHub Actions (`.github/workflows/btron-windows.yml`) で、本家の QEMU のソースを取得し、
`btron/patches/*.patch` を当ててビルドします。

- もとにする版: 本家の `v11.1.3` (https://gitlab.com/qemu-project/qemu)
- 変更: `btron/patches/0001-ui-gtk-grab-on-focus.patch` (GTK 表示の起動オプション `grab-on-focus` を追加。下記)
- ビルド対象: `qemu-system-i386` のみ (Windows x86_64 用。Linux 上の MinGW でクロスビルド)
- 表示: GTK と SDL。省いた機能: 説明書、ツール類、ゲストエージェント、VNC、SPICE、USB の転送、curl、暗号化ライブラリ

English summary: [below](#english-summary).

## ダウンロード

- 最新ビルド: [qemu-i386-win64.zip](https://github.com/tadwg/qemu/releases/download/btron-latest/qemu-i386-win64.zip)
- リリースのページ: https://github.com/tadwg/qemu/releases/tag/btron-latest

`btron` ブランチを更新するたびにビルドし、上のリリースの zip を差し替えます。
どのビルドかは、zip 内の `QEMU-SOURCE.txt` に記録しています。

## 使い方

zip を展開し、`qemu` フォルダの `qemu-system-i386.exe` を実行します (必要な DLL は同じフォルダにあります)。

```
qemu-system-i386.exe -m 256 -drive file=disk.img,format=raw,if=ide -nic user,model=pcnet -rtc base=localtime -display gtk,grab-on-focus=on
```

## grab-on-focus

### 問題

Windows のホストで GTK 表示を使い、ゲストが絶対座標のポインタ (vmmouse、USB タブレットなど) を使っていると、
ホストの日本語入力 (IME) がオンのときに、キーが IME に取られてゲストに届きません。
ゲストの OS によらず起きます (超漢字では、qemukbpd / qemumouse を使ったときに、かな漢字変換ができない、
変換中に Windows 側にフォーカスが移って英数しか入らなくなる、などの形で報告がありました)。

相対座標のマウス (超漢字の lowkbpd の PS/2 マウスなど) では起きません。

### 原因 (QEMU v11.1.3 のソースによる)

- Windows の GTK 表示は、入力をつかんでいる (grab) 間だけ、低レベルのキーボードフック (`ui/win32-kbd-hook.c`)
  でキーを受け取り、Windows に渡さずにゲストに送ります。このときホストの IME はキーを見ません
- つかんでいないときは通常の Windows のメッセージでキーを受け取るので、IME がオンだと先に IME が処理します
- 相対座標のポインタでは、ウィンドウを最初にクリックしたときに自動で入力をつかみます (`gd_button_event`)。
  絶対座標のポインタでは自動ではつかみません

本家にある回避策: Ctrl+Alt+G で入力をつかむ (ポインタも閉じ込める)、`-display gtk,grab-on-hover=on`
(ポインタがウィンドウ上にある間だけキーボードをつかむ)、ホストの IME をオフにしておく。

### 対策

起動オプション `-display gtk,grab-on-focus=on` を追加し、ウィンドウにフォーカスがある間だけキーボードをつかみます。

- フォーカスがないとき: マウスの移動だけがゲストに伝わる
- クリック (このクリックはゲストにも伝わる) や Alt+Tab でフォーカスを得ると: キーは低レベルのキーボードフックで
  ゲストに送られ、IME には渡らない
- 他のウィンドウをクリックするなどしてフォーカスを失うと: もとに戻る (押されたままのキーは離す。これは本家の動作)

作りの要点:

- フォーカスを得たときに、キーボードフックを有効にし (`win32_kbd_set_grab(true)`)、`kbd_owner` を設定する
- GDK のキーボードの取り込み (`gdk_seat_grab`) は使わない。ポインタはつかまず、X11 などでフォーカスの
  イベントが連鎖する心配もない
- フォーカスを失ったときは、Ctrl+Alt+G でポインタもつかんでいる場合を除いて、`gd_ungrab_keyboard()` で戻す
- オプションを付けなければ、本家と同じ動作

注意: フォーカスがある間は Alt+Tab や Windows キーもゲストに送られます (相対座標のポインタで入力をつかんでいる
ときと同じ)。QEMU から離れるときは、他のウィンドウをマウスでクリックしてください (Ctrl+Alt+Del は Windows に
届きます)。Ctrl+Alt+G は従来どおり使えます。

### 変更内容 (diff)

`btron/patches/0001-ui-gtk-grab-on-focus.patch` と同じ内容です (QEMU v11.1.3 に対する差分)。

```diff
--- a/include/ui/gtk.h
+++ b/include/ui/gtk.h
@@ -134,6 +134,7 @@
     int grab_x_root;
     int grab_y_root;
     VirtualConsole *kbd_owner;
+    bool grab_on_focus;
     VirtualConsole *ptr_owner;
 
     gboolean full_screen;
--- a/qapi/ui.json
+++ b/qapi/ui.json
@@ -1324,6 +1324,13 @@
 #
 # @grab-on-hover: Grab keyboard input on mouse hover.
 #
+# @grab-on-focus: Grab keyboard input while the window has the
+#     keyboard focus, without grabbing the pointer.  The grab is
+#     released when the window loses the focus.  On Windows hosts the
+#     keys then go through the low-level keyboard hook, so the host
+#     input method (IME) does not take them.  Defaults to "off".
+#     (Since 11.2)
+#
 # @zoom-to-fit: Zoom guest display to fit into the host window.  When
 #     turned off the host window will be resized instead.  In case the
 #     display device can notify the guest on window resizes
@@ -1349,6 +1356,7 @@
 { 'struct'  : 'DisplayGTK',
   'data'    : { '*clipboard'         : 'bool',
                 '*grab-on-hover'     : 'bool',
+                '*grab-on-focus'     : 'bool',
                 '*zoom-to-fit'       : 'bool',
                 '*show-tabs'         : 'bool',
                 '*show-menubar'      : 'bool',
--- a/ui/gtk.c
+++ b/ui/gtk.c
@@ -1875,6 +1875,17 @@
     VirtualConsole *vc = opaque;
 
     win32_kbd_set_window(gd_win32_get_hwnd(vc));
+    if (vc->s->grab_on_focus && vc->type == GD_VC_GFX && !vc->s->kbd_owner) {
+        /*
+         * Keyboard only, and no GDK seat grab: the window keeps the focus
+         * by itself, the pointer stays free, and on Windows the keys go
+         * through the low-level keyboard hook (not the host IME).
+         */
+        win32_kbd_set_grab(true);
+        vc->s->kbd_owner = vc;
+        gd_update_caption(vc->s);
+        trace_gd_grab(vc->label, "kbd", "grab-on-focus");
+    }
     return TRUE;
 }
 
@@ -1886,6 +1897,9 @@
 
     win32_kbd_set_window(NULL);
     gtk_release_modifiers(s);
+    if (s->grab_on_focus && s->kbd_owner == vc && s->ptr_owner != vc) {
+        gd_ungrab_keyboard(s);
+    }
     return TRUE;
 }
 
@@ -2807,6 +2821,8 @@
         opts->u.gtk.grab_on_hover) {
         gtk_menu_item_activate(GTK_MENU_ITEM(s->grab_on_hover_item));
     }
+    s->grab_on_focus = opts->u.gtk.has_grab_on_focus &&
+                       opts->u.gtk.grab_on_focus;
     if (opts->u.gtk.has_show_tabs &&
         opts->u.gtk.show_tabs) {
         gtk_menu_item_activate(GTK_MENU_ITEM(s->show_tabs_item));
```

### 確認状況

- Windows のホスト (GTK 表示、超漢字V + qemukbpd) で、IME がオンのままかな漢字変換ができることを、利用者が確認
- 確認していないこと: Linux / macOS のホストでの動作 (オプションを付けたとき)、SDL 表示 (SDL 表示は QEMU の
  キーボードフックではなく SDL 自身の取り込みを使うので、このパッチは効かない)、`qemu-options.hx` の説明

### 関連する情報

- SDL 表示での同様の問題と修正 (Windows ホスト + 中国語 IME。フォーカスを得たときに `SDL_StopTextInput()` で
  IME を切り離す): https://github.com/omacom/try-omarchy-windows/pull/334
- 本家の課題管理での要望 (CJK のホストでは IME の入力をさせないでほしい): https://gitlab.com/qemu-project/qemu/-/work_items/2813

### 本家への提案について

このパッチは AI (Claude) の支援で作成したもので、本家には送っていません。QEMU には、AI が生成したコードを
含む投稿を受け付けない方針 (`docs/devel/code-provenance.rst`) があるため、本家に提案する場合は、上の
「問題」「原因」「対策」の説明をもとに、課題 (issue) として報告するか、人が書き直したパッチを送ってください。

## English summary

**Problem.** On Windows hosts with the GTK display, when the guest uses an absolute pointing device
(vmmouse, USB tablet, ...), keys are taken by the host IME while it is on, and do not reach the guest.
QEMU only routes keys through its low-level keyboard hook (`ui/win32-kbd-hook.c`) while the input is
grabbed, and with an absolute pointer the input is never grabbed implicitly (only relative-mode clicks
grab it, see `gd_button_event`).

**Change.** A new GTK display option, `-display gtk,grab-on-focus=on`, grabs the keyboard only (no GDK seat
grab, the pointer stays free) while the window has the keyboard focus, and releases it on focus out.
The diff against v11.1.3 is shown above and in `btron/patches/0001-ui-gtk-grab-on-focus.patch`.

**Status.** Confirmed by a user on a Windows host (Japanese IME, BTRON guest). Not tested on Linux or macOS
hosts. The patch was written with the help of an AI assistant and has not been submitted upstream; see
QEMU's `docs/devel/code-provenance.rst`.

## ライセンス

QEMU は GNU General Public License version 2 です (`COPYING`)。このブランチの変更とビルド結果も同じ条件です。
同梱の DLL (GTK、GLib、SDL2、SDL3 など) は、それぞれのライセンス (主に LGPL、SDL は zlib) に従います。
ビルドに使ったソースは、本家の上記の版と `btron/patches` です。
