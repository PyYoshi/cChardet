#!/bin/bash

function download_github_release_assets() {
    local repo=$1
    local tag=$2
    local outputDir=$3
    local assets=()
    local json=""

    if [ "${tag}" = "latest" ]; then
        json=$(curl -sSL "https://api.github.com/repos/${repo}/releases/${tag}")
    else
        json=$(curl -sSL "https://api.github.com/repos/${repo}/releases/tags/${tag}")
    fi

    tag=$(echo "${json}" | jq -r ".tag_name")

    local i=0
    while true; do
        local url=$(echo "${json}" | jq -r ".assets[$i].browser_download_url")
        if [ "${url}" = "null" ]; then
            break
        fi
        assets+=("${url}")
        i=$((i + 1))
    done

    if [ ! -d "${outputDir}/${tag}" ]; then
        mkdir -p "${outputDir}/${tag}"
    fi

    for url in "${assets[@]}"; do
        local filename=$(basename "${url}")

        if [ -f "${outputDir}/${tag}/${filename}" ]; then
            printf "Skip %s\n" "${filename}"
            continue
        fi

        printf "Downloading %s\n" "${filename}"
        curl -sSL -o "${outputDir}/${tag}/${filename}" "${url}"
    done
}

ARG_VERSION=${1:-"latest"}
ARG_OUTPUT_DIR=${2:-"archives"}

download_github_release_assets "PyYoshi/cchardet" "${ARG_VERSION}" "${ARG_OUTPUT_DIR}"
