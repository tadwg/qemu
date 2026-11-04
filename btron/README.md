# QEMU (qemu-system-i386) の Windows 向けビルド

超漢字V (BTRON3) を Windows 上の QEMU で動かすための、QEMU のビルドです。
GitHub Actions (`.github/workflows/btron-windows.yml`) で、本家の QEMU のソースを取得してビルドします。

- もとにする版: 本家の `v11.1.3` (https://gitlab.com/qemu-project/qemu)
- 変更: `btron/patches/*.patch`
  - `0001-ui-gtk-grab-on-focus.patch`: GTK 表示の起動オプション `grab-on-focus` を追加 (下記)
- ビルド対象: `qemu-system-i386` のみ (Windows x86_64 用。Linux 上の MinGW でクロスビルド)
- 表示: GTK と SDL。省いた機能: 説明書、ツール類、ゲストエージェント、VNC、SPICE、USB の転送、curl、暗号化ライブラリ

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

## grab-on-focus (Windows のホストでのかな漢字変換)

絶対座標のマウス (超漢字の qemukbpd / qemumouse の vmmouse、USB タブレットなど) を使うと、本家の QEMU は
入力をつかまないため、Windows の日本語入力 (IME) がオンだとキーを IME に取られ、ゲストに届きません。

`-display gtk,grab-on-focus=on` を付けると、QEMU のウィンドウにフォーカスがある間だけキーボードをつかみます
(ポインタはつかみません)。

- フォーカスがないとき: マウスの移動だけがゲストに伝わる
- クリック (このクリックはゲストにも伝わる) や Alt+Tab でフォーカスを得ると: キーは低レベルのキーボードフックで
  ゲストに送られ、IME には渡らない
- 他のウィンドウをクリックするなどしてフォーカスを失うと: もとに戻る (押されたままのキーは離す)

注意: フォーカスがある間は Alt+Tab や Windows キーもゲストに送られます。QEMU から離れるときは、他のウィンドウを
マウスでクリックしてください (Ctrl+Alt+Del は Windows に届きます)。Ctrl+Alt+G (ポインタもつかむ) は従来どおり使えます。

## ライセンス

QEMU は GNU General Public License version 2 です (`COPYING`)。このブランチの変更とビルド結果も同じ条件です。
同梱の DLL (GTK、GLib、SDL2 など) は、それぞれのライセンス (主に LGPL) に従います。
ビルドに使ったソースは、本家の上記の版と `btron/patches` です。
