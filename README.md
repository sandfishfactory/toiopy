# toiopy

[toio.js](https://github.com/toio/toio.js)を参考に python に書き換えました。

```python
from toiopy.scanner import NearestScanner


def main():
    scanner = NearestScanner(provider)
    cubes = scanner.start()
    cube = cubes[0]

    cube.connect()
    cube.move(100, 100, 1000)
    cube.disconnect()

if __name__ == '__main__':
    provider = NearestScanner.get_provider()
    provider.run_mainloop_with(main)

```

# 前提条件

python は 3.7.1 で動作確認中です。
