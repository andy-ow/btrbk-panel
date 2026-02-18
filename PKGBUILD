pkgname=btrbk-panel-git
_pkgname=btrbk-panel
pkgver=b6c7433
pkgrel=1
pkgdesc="YAD GUI panel for running btrbk groups via pkexec"
arch=('any')
#url="ssh://git@github.com/andy-ow/${_pkgname}.git"
url="https://git@github.com/andy-ow/${_pkgname}.git"
license=('custom')

depends=('python' 'python-freesimplegui' 'tk' 'polkit' 'btrbk')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-hatchling')
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
  /usr/bin/python -m build --wheel --no-isolation
}

package() {
  cd "${srcdir}/${_pkgname}"

  # instalacja wheel do $pkgdir (to tworzy /usr/bin/btrbk-panel z [project.scripts])
  /usr/bin/python -m installer --destdir="${pkgdir}" dist/*.whl

  install -Dm644 src/btrbk_panel/btrbk-panel.desktop \
    "${pkgdir}/usr/share/applications/btrbk-panel.desktop"
}

