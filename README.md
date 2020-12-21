
# algorithm-runner

> 시스템 입/출력을 사용하는 알고리즘 스크립트를 테스트하기 위한 Runner

<p align="center">
<img src="image/preview.png" width="720">
</p>

## 사용방법

```bash
usage: runner.py [-h] [--cwd CWD] config

positional arguments:
  config

optional arguments:
  -h, --help  show this help message and exit
  --cwd CWD
```

## 설치

1. 이 저장소를 원하는 경로에 클론합니다.
2. 클론한 위치에서 아래의 명령어로 필요한 라이브러리들을 설치합니다.
   
   ```
   pip install -r requirements.txt
   ```

3. Runner 실행을 위한 yaml 파일을 작성합니다.
   
    ```yaml
    script: python test.py
    tests:
      - input: |
          1 2 3
        output: |
          6
      - input: |
          1 2 4
        output: |
          6
      - input: |
          1 a 1
        output: |
          2
    ```

## Yaml 작성 방법

### script

Runner가 수행할 스크립트

- 하나의 스크립트 파일 실행

Python 스크립트를 테스트할 경우 다음과 같이 작성합니다.

```yaml
script: python test.py
```

다른 언어를 테스트할 경우 `script` 자리를 변경해주면 됩니다.

```yaml
script: node test.js
```

- 여러 스크립트 파일 실행

동일한 테스트 케이스에 대해 여러 언어를 테스트할 경우 `script`를 리스트 형태로 작성하면 됩니다.

```yaml
script:
    - python test.py
    - node test.js
```

### tests

Runner가 수행할 테스트 케이스

이 속성은 반드시 리스트로 작성해야 하며 각 리스트의 항목은 입력은 `input`, 입력에 따른 예상 결과는 `output`에 작성해야 합니다.

```yaml
tests:
    - input: |
        1 2 3
      output: |
        6
    - input: |
        1 3 3
      output: |
        7
```

입/출력은 여러 줄로 작성할 수 있습니다.

```yaml
tests:
    - input: |
        1 2 3
        5 6 7
      output: |
        6
        18
```