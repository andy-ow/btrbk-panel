pkgname=btrbk-panel-git
_pkgname=btrbk-panel
pkgver=0.0.0.r0.g0000000
pkgrel=1
pkgdesc="YAD GUI panel for running btrbk groups via pkexec"
arch=('any')
url="https://github.com/TWOJ_LOGIN/${_pkgname}"
license=('custom')
depends=('yad' 'polkit' 'btrbk')
optdepends=('polkit-gnome: graphical authentication agent')
provides=("${_pkgname}")
conflicts=("${_pkgname}")

# repo git jako źródło
source=("${_pkgname}::git+${url}.git")
sha256sums=('SKIP')

pkgver() {
  cd "${srcdir}/${_pkgname}"
  # wersja z tagów: v1.2.3-4-gHASH -> 1.2.3.r4.gHASH
  git describe --long --tags --always \
    | sed -E 's/^v//; s/([^-]+)-([0-9]+)-g/\\1.r\\2.g/'
}

package() {
  cd "${srcdir}/${_pkgname}"

  install -Dm755 btrbk-panel.sh "${pkgdir}/usr/bin/btrbk-panel"
  install -Dm755 btrbk-helper   "${pkgdir}/usr/lib/btrbk-panel/btrbk-helper"

  # opcjonalnie desktop entry
  if [[ -f btrbk-panel.desktop ]]; then
    install -Dm644 btrbk-panel.desktop "${pkgdir}/usr/share/applications/btrbk-panel.desktop"
  fi
}
pkgver=1.0
pkgrel=1
pkgdesc="YAD GUI panel for running btrbk groups via pkexec"
arch=('any')
url="local"
license=('custom')
depends=('yad' 'polkit' 'btrbk')
optdepends=('polkit-gnome: graphical authentication agent')
source=('btrbk-panel.sh'
        'btrbk-helper')
sha256sums=('SKIP'
            'SKIP')

package() {
    install -Dm755 "$srcdir/btrbk-panel.sh" \
        "$pkgdir/usr/bin/btrbk-panel"

    install -Dm755 "$srcdir/btrbk-helper" \
        "$pkgdir/usr/lib/btrbk-panel/btrbk-helper"

    install -Dm644 "$srcdir/btrbk-panel.desktop" \
    "$pkgdir/usr/share/applications/btrbk-panel.desktop"}
