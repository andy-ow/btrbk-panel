pkgname=btrbk-panel-git
_pkgname=btrbk-panel
pkgver=0.1.0.r0.g0000000
pkgrel=1
pkgdesc="YAD GUI panel for running btrbk groups via pkexec"
arch=('any')
url="ssh://git@github.com/andy-ow/${_pkgname}.git"
license=('custom')

depends=('python' 'python-freesimplegui' 'tk' 'polkit' 'btrbk')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
optdepends=('polkit-gnome: graphical authentication agent')

provides=("${_pkgname}")
conflicts=("${_pkgname}")

source=("${_pkgname}::git+${url}")
sha256sums=('SKIP')

pkgver() {
  cd "${srcdir}/${_pkgname}"
  git describe --long --tags --always \
    | sed -E 's/^v//; s/([^-]+)-([0-9]+)-g/\1.r\2.g/'
}

build() {
  cd "${srcdir}/${_pkgname}"
  python -m build --wheel --no-isolation
}

package() {
  cd "${srcdir}/${_pkgname}"

  # instalacja wheel do $pkgdir (to tworzy /usr/bin/btrbk-panel z [project.scripts])
  python -m installer --destdir="${pkgdir}" dist/*.whl

  # dodatkowe pliki "nie-pythonowe"
  install -Dm755 src/btrbk_panel/btrbk-helper \
    "${pkgdir}/usr/lib/btrbk-panel/btrbk-helper"

  install -Dm644 src/btrbk_panel/btrbk-panel.desktop \
    "${pkgdir}/usr/share/applications/btrbk-panel.desktop"
}

