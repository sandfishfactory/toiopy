# toiopy

[toio.js](https://github.com/toio/toio.js)を参考に python に書き換えました。

```python
from toiopy.scanner import NearestScanner


def main():
    scanner = NearestScanner(provider)
    cube = scanner.start()

    cube.connect()
    cube.move(100, 100, 1000)
    cube.disconnect()

if __name__ == '__main__':
    provider = NearestScanner.get_provider()
    provider.run_mainloop_with(main)

```

# 前提条件

python は 3.7.1 で動作確認中です。

# インストール手順

```
git clone https://github.com/sandfishfactory/toiopy.git

cd toiopy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Adafruit_Python_BlueFruitLEをcloneしたディレクトリに移動
cd {Adafruit_Python_BluefruitLEディレクトリ}
sudo python setup.py install

cd {toiopyディレクトリ}
```
