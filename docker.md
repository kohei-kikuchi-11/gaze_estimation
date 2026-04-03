# Docker 

## 1.Docker とは

Docker は「コンテナ型の仮想化技術」を使って、アプリケーションやその実行環境をパッケージ化するツールです。

簡単に言うと、

- アプリを動かすのに必要なもの（プログラム、ライブラリ、設定など）を一つの「箱（コンテナ）」にまとめて、
- どこでも同じように動かせるようにする仕組み

です。

### 1.1.どんな便利なことがあるの？
#### 1.**「動かない」がなくなる**

開発者によくあるやりとり：

> 「え、このアプリ、俺の環境では動いたんだけどな…？」

Docker を使えば、全員が同じ環境で動かせるので、**環境差によるトラブルが少なくなります**。

#### 2.**環境構築がラクチン**
普通のアプリだと「Python のバージョンは3.10、MySQL も入れて、設定はこうで…」と環境構築が面倒ですが、  
Docker では「Dockerfile」や「docker-compose.yml」に必要な設定を書いておくだけ。

他の人はコマンド一発で同じ環境を再現できます：

```bash
docker compose up
```

#### 3.**複数のアプリやサービスを同時に動かせる**
例えば、Webアプリ + DB + キャッシュサーバー みたいな構成も、Docker なら簡単にセットアップ＆起動できます。

#### 4.**軽量＆高速な仮想化**
仮想マシンよりも軽量で起動も速いです。  
例えば、VirtualBoxよりも数秒で立ち上がるし、リソース消費も少ないです。

#### 5.**CI/CDやデプロイがスムーズ**
自動テスト、ビルド、デプロイにもDockerが使われています。  
本番環境と同じコンテナでテストをすることができます。

### 1.2.まとめ：Dockerを使うと…

- 「どこでも同じように動く」
- 「環境構築がラク」
- 「複雑なシステムも簡単に起動」
- 「軽くて速い」
- 「チーム開発や本番運用でも安心」

このように開発者にとってかなり強力な味方になるツールです。

## 2.Hello-World

まずは Docker における Hello-World をしてみましょう。

wsl または ターミナルで以下を実行してみましょう。

```sh
docker container run hello-world
```

以下が出力されれば正常に動作しています。

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
e6590344b1a5: Pull complete 
Digest: sha256:fc08e727181e2668370f47db6319815c279ed887e2f01be96b94106bc2781430
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

## 3. 主要登場要素

Docker を学ぶ上でまず頭に入れてほしい主要登場要素が以下の3つです。

1. **Docker container**
2. **Docker image**
3. **Dockerfile**

### 3.1.Docker container：**実行中のアプリケーション**

コンテナは、Dockerによって起動された**軽量な実行環境**です。

- 各コンテナは他のプロセスと分離されており、独立したファイルシステムやネットワーク空間を持ちます。
- ただし、ホストOSのカーネルを共有しているため、仮想マシンよりも高速かつ軽量です。
- コンテナ自体は**一時的かつ実行中の状態**であり、再起動や複製には image が必要です。

> ❗ コンテナは“実体”ですが、永続性がなく、再現には image が必要になります。

### 3.2.Docker image：**コンテナのもとになる静的な実行環境**

イメージは、**アプリケーションとその依存関係（OS、ライブラリ、設定など）を含む読み取り専用のテンプレート**です。

- コンテナの「起動元」であり、これを基にして複数のコンテナを起動できます。
- 変更不可能で、レイヤー構造（差分の積み重ね）になっているため、効率的なキャッシュや再利用が可能です。
- image はバージョン管理もでき、環境の再現性や移植性を担保します。

> ✅ image があることで、**同一のアプリケーション環境をどこでも同じように再現・配布**できます。

### 3. Dockerfile：**image を構築するための設定ファイル**

Dockerfileは、Docker imageを構築する際の**手順を記述した宣言的なスクリプト**です。

- 使用するベースイメージ（例：`python:3.11`）や、
- 必要なパッケージのインストール方法（例：`apt-get`, `pip install`）、
- 実行ファイルや環境変数の指定などを定義します。

これを`docker build`コマンドで実行することで、**Docker imageが作成されます**。

> 📘 Dockerfileの記述が、Docker環境のコードによる構成管理（Infrastructure as Code）を実現します。

---

### 🔁 全体の流れと関係性

```
Dockerfile（構成の定義）  
   ↓ docker build  
Docker image（コンテナのもとになる静的な実行環境）  
   ↓ docker run  
Docker container（稼働中のアプリケーション）
```

### まとめ：

| 要素 | 役割 | 特徴 |
|------|------|------|
| **Dockerfile** | imageを作る手順書 | 宣言的・コード管理可能・再現性担保 |
| **Docker image** | コンテナのひな型 | 静的・読み取り専用・差分で構成 |
| **Docker container** | 実行中のアプリ環境 | 動的・軽量・使い捨て可能 |

---

この三層構造を理解すると、Dockerの設計思想──**再現性・移植性・効率性**が見えてきます。  
必要に応じて、自動化（CI/CD）や本番環境へのデプロイにもスムーズに応用できます。

## 6. Python ベースイメージで Python 環境を作成

### 6.1. pull
Docker Hub から Python のベースイメージを pull します。

https://hub.docker.com/_/python

```sh
docker pull python:3.13
```

ここで `python:3.13` は `python` がイメージ名、`3.13` がタグ名となっています。

以下コマンドで pull 済みのイメージを確認することができます。

```sh
docker image ls
```

ちなみに以下のようにタグなしで pull することもできます。

```sh
docker pull python
```

そして `docker image ls` で確認するとタグ名が latest となっていることが分かります。

これは一般的には最新の安定版を指すため、pull したタイミングによっては前のバージョンから変わっている可能性があります。

基本は latest タグは使わないようにするのが better でしょう。

### 6.2. run

run でイメージからコンテナを作成 + 起動 + コンテナ内でコマンド実行します。

```sh
docker container run -it python:3.13 /bin/bash
```

別のターミナルで

```sh
docker container ls
```

すると起動中のコンテナのリストが表示されます。NAME は指定しない場合はランダムに付与されます。

もし NAME を付けたい場合は

```sh
docker container run -it --name sample python:3.13 /bin/bash
```

### 6.3. stop

コンテナを停止するには

```sh
docker container stop sample
# docker container stop df1cd
```

とするか、コンテナに入っている shell で exit で抜け出します。

あくまでコンテナの停止なので

```sh
docker container ls -a
```

すると残っていることが確認できます。
抜けたDockerにまた入るコマンド
docker container start sample
↓
docker container exec -it sample /bin/bash
### 6.4. rm

コンテナを削除する方法です。コンテナ消すとコンテナ内で保存していたファイルは消えてしまうので注意です。(後ほど回避方法を解説します)

```sh
docker container rm sample
# docker container rm df1cd
```

またコンテナ起動時に `--rm` オプションを付けることで

```sh
docker container run -it --name sample --rm python:3.13 /bin/bash
```

コンテナから抜けると同時にコンテナが削除されるようにも設定できます。

コンテナが溜まるとディスク容量を圧迫したりするため、都度削除する `--rm` はよく使います。

### 6.5. mount

コンテナ内のファイルをホスト側に保存したり、ホスト側のファイルをコンテナ内で使用できるように、ホスト側のディレクトリやファイルをマウントすることができます。

まずマウントしたいディレクトリを用意します。

```sh
mkdir src
touch src/sample.py
```

そして `-v` でホスト側とコンテナ側のマウント先を指定します。

```sh
docker container run -it --name sample -v ./src:/workspace python:3.13 /bin/bash
```

するとコンテナ内の `/workspace` 下に `sample.py` が確認できます。

こちらは単にコピーされている訳ではなく、同じものであるため、`sample.py` をホスト側で編集するとコンテナ内の `sample.py` も変更されます。

## 7. docker build

今度は docker image を Docker Hub から pull するのではなく、作成する方法を学びます。

イメージを作成するにはイメージの設計図となる Dockerfile を用意する必要があります。

簡単な Python のプログラムを動かすことができる環境を Docker で用意してみましょう。

まず以下を `Dockerfile` という名前で用意します。フォルダ構成は以下のようにします。

```
myapp/
├── src/
|   |- sample.py
└── Dockerfile
```

```Dockerfile
FROM ubuntu:20.04

# 必要なパッケージをインストール（Python と pip）
RUN apt-get update && apt-get install -y vim python3 python3-pip

# 作業ディレクトリへ移動 (なければ作成)
WORKDIR /app

# アプリのファイルをコピー
COPY src/sample.py .

# コンテナ起動時に実行されるコマンド設定
CMD ["/bin/bash"]
```

sample.py の中身はシンプルに以下を記載しておきましょう。

```py
print("Hello from Docker!")
```

代表的なコマンドは以下です。

| コマンド | 説明 | 使用例 |
| --- | --- | --- |
| `FROM` | ベースとなるイメージを指定します。最初に必ず記述します。 | `FROM ubuntu:20.04` |
| `RUN`           | コンテナ内でコマンドを実行します。主にパッケージのインストールや設定を行います。                  | `RUN apt-get update && apt-get install -y python3`                                          |
| `COPY`          | ホストマシンのファイルやディレクトリをコンテナ内にコピーします。                                  | `COPY ./app.py /app/`                                                                      |
| `ADD`           | `COPY` と似ていますが、アーカイブファイル（例：.tar）を展開したり、URL からファイルをコピーしたりします。(基本は COPY を使ったほうが better です) | `ADD myapp.tar /app/`                                                                      |
| `WORKDIR`       | 作業ディレクトリを設定します。以降のコマンドはこのディレクトリ内で実行されます。                     | `WORKDIR /app`                                                                              |
| `CMD`           | コンテナ起動時に実行されるコマンドを指定します。1つの `CMD` しか記述できません。                    | `CMD ["python3", "app.py"]`                                                                 |
| `VOLUME`        | コンテナとホスト間で共有するディレクトリを指定します。データの永続化に使います。                    | `VOLUME ["/data"]`                                                                           |
| `ENV`           | 環境変数を設定します。コンテナ内で使われる環境変数を指定できます。                               | `ENV APP_HOME /app`                                                                         |
| `ARG`           | ビルド時に渡される引数を定義します。`docker build` コマンドの `--build-arg` と合わせて使います。        | `ARG VERSION=1.0`                                                                           |

Dockerfile があるディレクトリ上で以下コマンドを実行すると Dockerfile を元にイメージが生成されます。

```sh
docker image build  . .はカレントディレクトリを指している
```

ここで `-t` オプションはイメージ名を指定しています。

さてイメージが作成されているか確認してみましょう。

```sh
docker image ls
```

また作成されたイメージは先程説明した Python 環境のコンテナ作成のように起動をすることができます。

```sh
docker run --rm -it --name myapp-container myapp-image
```

## 8. JupyterLab サーバー起動

JupyterLab サーバーを作成するコンテナについては以下 Docker 公式 Docs を参考にコマンドを解説します。

https://docs.docker.com/guides/jupyter/

以下コマンドによ JpyterLab サーバーを起動することができます。

```sh
docker container run --rm -p 8888:8888 -v .:/home/jovyan/work quay.io/jupyter/base-notebook start-notebook.py
```

復習となりますが、まず `quay.io/jupyter/base-notebook` 使用する Docker イメージの名前です。

これは Jupyter のベースノートブックイメージで、Jupyter ノートブックを動かすための基本的な設定が含まれています。

`start-notebook.py` はコンテナ起動時に最初に実行するコマンドで、コンテナ内に既に用意されている JupyterLab を開始するための Python スクリプトがコンテナ内で実行されます。

### -p オプションについて
`-p` オプションは、ポートの公開を設定するために使用します。具体的には、ホストマシン（あなたのコンピュータ）とコンテナ間でポート番号をバインドします。

最初の 8888 これは ホストマシンのポート番号です。コンテナがこのポートを外部（ホスト側）に公開し、ホストマシン上でアクセスできるようにします。

後ろの 8888 これは コンテナ内のポート番号です。コンテナがこのポートでリッスン（待機）して、外部からの接続を受け入れます。

つまり、このコマンドでは ホストのポート 8888 をコンテナのポート 8888 にマッピングしているという意味です。

この設定によって、ホストマシンからコンテナ内のアプリケーションにアクセスできるようになります。

JupyterLab は通常、デフォルトでポート 8888 を使用して、ブラウザでアクセスできるようにします。このコマンドでは、コンテナ内の Jupyter サーバーがポート 8888 で動作し、ホストマシンの同じポート番号（8888）にアクセスできるように設定しています。

コマンドを実行した後、ブラウザで http://localhost:8888 にアクセスすることで、JupyterLab が表示されるはずです。これは、ホストのポート 8888 がコンテナ内のポート 8888 にマッピングされているためです。

## 9. docker compose

さらに Docker を便利に使いこなすために、Docker Compose について触れていきます。

Docker Compose は 複数の Docker コンテナを一括で定義・管理・実行できるツールとなっています。

まずあなたの環境で Docker Compose が使えるか確認してみましょう。

```sh
docker compose version
```

コマンドを実行してバージョンの確認ができたら使用可能です。

続いて Docker Compose を使うと便利なことの一部を紹介します。

### 9.1. docker build/run 時のオプション等のコマンド入力を省略

JupyterLab サーバー起動の際に以下コマンドでコンテナ実行をしました。

```sh
docker container run -p 8888:8888 -v .:/home/jovyan/work quay.io/jupyter/base-notebook start-notebook.py
```

こちらを Docker Compose の設定ファイル `docker-compose.yml` に書き直すと

```
services:
  jupyter:  # 任意のサービス名
    image: quay.io/jupyter/base-notebook
    ports:
      - "8888:8888"
    volumes:
      - .:/home/jovyan/work
    command: start-notebook.py
```

となります。

設定ファイルに書き込んでおくことで、起動は以下コマンドだけで済みます。

```sh
docker compose up
```

### 9.2. 複数コンテナの起動

参考に 「SQL100本ノック」のリポジトリを見てみましょう。

https://github.com/The-Japan-DataScientist-Society/100knocks-preprocess

こちらの `docker-compose.yml` を見てみましょう。

詳細は省きますが、この `docker-compose.yml` では

1. PostgreSQL
2. JupyterNotebook

の2つのコンテナを以下コマンドで同時に起動し、また連携もさせることができます。

```sh
docker compose up
```

## 10. 課題

1. 「SQL100本ノック」を Docker Compose で環境を作成して試しに解いてみる
   - 余力があれば `docker-compose.yml` の中身を見てみる
2. Python3 を実行可能な環境を作成する Dockerfile を作成する
   - 最終的には
      ```sh
      docker compose run {service名}
      ```
      で Python が実行できるコンテナ内に入ることができることが目標
   - 以下条件も満たすこと
      - ベースイメージは `ubuntu: 20.04` を使用すること
      - コンテナ内で vim, curl コマンドが使えること
      - コンテナ内で numpy, pandas が使えるように requirements.txt を用意して docker build 時にインストールさせること
      - ホスト側の Dockerfile があるディレクトリとコンテナ内の `/workspace` をマウントする
      - GitHub にリポジトリを用意して以下構成で配置する

      ```sh
      prj
      |- Dockerfile
      |- docker-compose.yml
      |- requirements.txt
      |- README.md
      ```

## 今回できなかった話
- VSCode 拡張機能「Dec Containers」を使って Docker container 内で作業
- Dockerfile とキャッシュの話
- docker build 時のビルドコンテキストの話
- RUN apt-get install 時のキャッシュ削除について
