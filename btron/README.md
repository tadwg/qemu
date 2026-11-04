# QEMU (qemu-system-i386) の Windows 向けビルド

超漢字V (BTRON3) を Windows 上の QEMU で動かすための、QEMU のビルドです。
GitHub Actions (`.github/workflows/btron-windows.yml`) で、本家の QEMU のソースを取得してビルドします。

- もとにする版: 本家の `v11.1.3` (https://gitlab.com/qemu-project/qemu)
- 変更: `btron/patches/*.patch` (今はなし。本家と同じ)
- ビルド対象: `qemu-system-i386` のみ (Windows x86_64 用。Linux 上の MinGW でクロスビルド)
- 表示: GTK と SDL。省いた機能: 説明書、ツール類、ゲストエージェント、VNC、SPICE、USB の転送、curl、暗号化ライブラリ

## 使い方

1. GitHub の Actions の実行結果から `qemu-i386-win64-v11.1.3` (zip) をダウンロードして展開する
2. 展開した `qemu` フォルダの `qemu-system-i386.exe` を実行する (必要な DLL は同じフォルダにある)

```
qemu-system-i386.exe -m 256 -drive file=disk.img,format=raw,if=ide -nic user,model=pcnet -rtc base=localtime -display gtk
```

## ライセンス

QEMU は GNU General Public License version 2 です (`COPYING`)。このブランチの変更とビルド結果も同じ条件です。
同梱の DLL (GTK、GLib、SDL2 など) は、それぞれのライセンス (主に LGPL) に従います。
ビルドに使ったソースは、本家の上記の版と `btron/patches` です (zip 内の `QEMU-SOURCE.txt` に版を記録)。
