#!/usr/bin/env bash
# Portable install: OpenGrep, 2ms, KICS, Grype, Microsoft SBOM Tool.
# Vendored for CI (no ~/.cursor/skills dependency). [Corpus: adr-037]
# Installs to ~/.local/share/security-static-analysis/{bin,assets} (or SEC_TOOLS_DIR).
set -euo pipefail

PREFIX="${SEC_TOOLS_DIR:-${HOME}/.local/share/security-static-analysis}"
BIN_DIR="${PREFIX}/bin"
ASSETS_DIR="${PREFIX}/assets"
mkdir -p "${BIN_DIR}" "${ASSETS_DIR}"
export PATH="${BIN_DIR}:${PATH}"

log() { printf '[security] %s\n' "$*"; }
err() { printf '[security] ERROR: %s\n' "$*" >&2; }

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH_RAW="$(uname -m)"
case "${ARCH_RAW}" in
  x86_64 | amd64) ARCH="amd64" ;;
  aarch64 | arm64) ARCH="arm64" ;;
  *) err "unsupported arch ${ARCH_RAW}"; exit 1 ;;
esac

download() { curl -fsSL "$1" -o "$2"; }

log "installing → ${BIN_DIR} (${OS}/${ARCH})"

# OpenGrep
if [[ ! -x "${BIN_DIR}/opengrep" || "${SEC_FORCE:-0}" == "1" ]]; then
  curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
  ln -sfn "${HOME}/.opengrep/cli/latest/opengrep" "${BIN_DIR}/opengrep"
fi

# 2ms
if [[ ! -x "${BIN_DIR}/2ms" || "${SEC_FORCE:-0}" == "1" ]]; then
  case "${OS}-${ARCH}" in
    linux-amd64) A=linux-amd64.zip ;;
    linux-arm64) A=linux-arm64.zip ;;
    darwin-amd64) A=macos-amd64.zip ;;
    darwin-arm64) A=macos-arm64.zip ;;
    *) err "no 2ms asset"; exit 1 ;;
  esac
  tmp="$(mktemp -d)"
  download "https://github.com/checkmarx/2ms/releases/latest/download/${A}" "${tmp}/${A}"
  unzip -qo "${tmp}/${A}" -d "${tmp}/out"
  bin="$(find "${tmp}/out" -type f \( -name 2ms -o -name 2ms.exe \) | head -1)"
  install -m 0755 "${bin}" "${BIN_DIR}/2ms"
  rm -rf "${tmp}"
fi

# KICS — prefer SEC_KICS_VERSION; else newest release that ships the platform tarball
# (GitHub sometimes publishes a "latest" tag with zero binary assets, e.g. v2.1.21).
if [[ ! -x "${BIN_DIR}/kics" || ! -d "${ASSETS_DIR}/kics/assets/queries" || "${SEC_FORCE:-0}" == "1" ]]; then
  case "${OS}" in linux) osn=linux ;; darwin) osn=darwin ;; *) err "no kics os ${OS}"; exit 1 ;; esac
  resolve_kics_ver() {
    if [[ -n "${SEC_KICS_VERSION:-}" ]]; then
      printf '%s\n' "${SEC_KICS_VERSION}"
      return 0
    fi
    curl -fsSL "https://api.github.com/repos/Checkmarx/kics/releases?per_page=20" | python3 -c '
import json, sys
osn, arch = sys.argv[1], sys.argv[2]
for rel in json.load(sys.stdin):
    tag = rel.get("tag_name") or ""
    ver_num = tag[1:] if tag.startswith("v") else tag
    name = f"kics_{ver_num}_{osn}_{arch}.tar.gz"
    for a in rel.get("assets") or []:
        if (a.get("name") or "") == name:
            print(tag)
            raise SystemExit(0)
sys.stderr.write("no KICS release with platform binary assets\n")
raise SystemExit(1)
' "${osn}" "${ARCH}"
  }
  ver="$(resolve_kics_ver)"
  ver_num="${ver#v}"
  asset="kics_${ver_num}_${osn}_${ARCH}.tar.gz"
  log "KICS ${ver} (${asset})"
  tmp="$(mktemp -d)"
  download "https://github.com/Checkmarx/kics/releases/download/${ver}/${asset}" "${tmp}/${asset}"
  tar -xzf "${tmp}/${asset}" -C "${tmp}"
  bin="$(find "${tmp}" -type f -name kics | head -1)"
  install -m 0755 "${bin}" "${BIN_DIR}/kics"
  rm -rf "${ASSETS_DIR}/kics"
  mkdir -p "${ASSETS_DIR}/kics"
  if [[ -d "${tmp}/assets/queries" ]]; then
    cp -R "${tmp}/assets" "${ASSETS_DIR}/kics/"
  else
    download "https://github.com/Checkmarx/kics/releases/download/${ver}/extracted-info.zip" "${tmp}/extracted-info.zip"
    unzip -qo "${tmp}/extracted-info.zip" -d "${tmp}/extracted"
    cp -R "${tmp}/extracted/assets" "${ASSETS_DIR}/kics/"
  fi
  rm -rf "${tmp}"
fi

# Grype
if [[ ! -x "${BIN_DIR}/grype" || "${SEC_FORCE:-0}" == "1" ]]; then
  curl -sSfL https://get.anchore.io/grype | sh -s -- -b "${BIN_DIR}"
fi

# SBOM Tool
if [[ ! -x "${BIN_DIR}/sbom-tool" || "${SEC_FORCE:-0}" == "1" ]]; then
  case "${OS}-${ARCH}" in
    linux-amd64) A=sbom-tool-linux-x64 ;;
    darwin-amd64) A=sbom-tool-osx-x64 ;;
    darwin-arm64) A=sbom-tool-osx-arm64 ;;
    *) err "no sbom-tool asset for ${OS}-${ARCH}"; exit 1 ;;
  esac
  download "https://github.com/microsoft/sbom-tool/releases/latest/download/${A}" "${BIN_DIR}/sbom-tool"
  chmod 0755 "${BIN_DIR}/sbom-tool"
fi

log "done — export PATH=\"${BIN_DIR}:\$PATH\""
printf '%s\n' "${BIN_DIR}"
