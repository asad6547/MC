name: Build APK

on:
  workflow_dispatch:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v2
        id: buildozer
        with:
          command: buildozer android debug
          buildozer_version: stable

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: mc-browser-apk
          path: bin/*.apk
