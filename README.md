## 0. gaze_estimation
## 1. 視線推定の流れ 
動画をフレームごとに以下のような流れで視線推定を行います。
```
顔検出
↓
顔検出結果からランドマーク(目、鼻、口、眉毛、輪郭)推定
↓
顔検出結果から頭部姿勢推定
↓
ランドマーク推定と頭部姿勢推定結果から視線推定
```
次に、それぞれの工程について簡単に説明します。
### 1.1 顔検出
フレーム全体から顔を検出します。
顔はバウンディングボックス(bbox)という四角で囲まれます。
![face-detection-adas-0001.png](http://hr-dash.tech/api/files/articles/2026-04/e5a80ba8-d230-4786-ae05-df7d6a8c3a2b.png)
bboxの表現方法は2つあります。
1つはコーナー2点による表現で、もう1つは中心点と幅、高さを使う表現です。
今回は前者の表現が使われています。
![image1-6.png](http://hr-dash.tech/api/files/articles/2026-04/60a9b9dc-9e07-4689-becc-f4ac710b4e66.png)


- 入力:(B(バッチサイズ), C(チャンネル数), H(画像の高さ), W(画像の幅))
- 出力:(1, 1, N(bbox数), 7)

各検出は [image_id, label, conf, x_min, y_min, x_max, y_max]のようになっており、x,yは正規化座標です。
正規化とは x, yをそれぞれW, Hで割って値を0～1にすることです。
- image_id : バッチ内の画像の ID
- label : 予測されたクラス ID (1=顔)
- conf : 予測されたクラスの信頼度
- (x_min, y_min) : 境界ボックスの左上隅の座標
- (x_max, y_max) : 境界ボックスの右下隅の座標

### 1.2 ランドマーク推定
ランドマーク推定は顔検出の結果のx_min, y_min, x_max, y_maxを使用して顔の部分だけを入力して推定を行います。
これをROI(関心領域)といい、注目して処理や分析を行いたい部分を指します。

- 入力:(B(バッチサイズ), C(チャンネル数), H(顔ROIの高さ), W(顔ROIの幅))
- 出力:(1,70) 35個のランドマーク(x,y)が正規化されて出力されます。
![landmarks_illustration.png](http://hr-dash.tech/api/files/articles/2026-04/e4f0e5a2-4ad0-464a-b843-613858e0191d.png)
- 左目:p0,p1
- 右目:p2, p3
- 鼻:p4-p7
- 口:p8-11
- 左眉毛:p12-p14
- 右眉毛:p15-17
- 顔の輪郭:p18-p34

### 1.3 頭部姿勢推定
顔ROIの入力から頭部姿勢を推定します。

- 入力:(B(バッチサイズ), C(チャンネル数), H(顔ROIの高さ), W(顔ROIの幅))
- 出力: yaw(度), pitch(度), roll(度)

yaw,pitch,rollとは頭の向きを3つに分解し数値化したもので簡単にいうと下記のようになります。
- yaw: 首を左右に振る動き カメラ視点で右を向くと＋
- pitch:首を上下に降る動き カメラ視点で下を向くと＋
- roll:首を傾ける動き カメラ視点で右肩が上がると＋
![roll_pitch_yaw.png](http://hr-dash.tech/api/files/articles/2026-04/0216c5c7-b0d0-4dc7-8963-f85248bb4bd9.png)

### 1.4 視線推定
ランドマーク推定で得た左右目の座標と頭部視線推定の結果から視線推定を行います。
- 入力:左右目ORI, 頭部推定結果
- 出力: 正規化していない視線ベクトル(x, y, z)

## 2. 視点推定パイプラインを動かす。

Dockerを使って簡単に動かせるようにしています。

今回使用したモデル
- 顔検出:face-detection-adas-0001
- ランドマーク推定:facial-landmarks-35-adas-0002
- 頭部姿勢推定:head-pose-estimation-adas-0001
- 視線推定:gaze-estimation-adas-0002

### 2.1 準備
#### step1
リポジトリをクローン
```
https://github.com/kohei-kikuchi-11/gaze_estimation.git
```
#### step2
視線推定を行いたい動画をinputディレクトリに人の顔が写っている動画を格納します。

### 2.2 実行
下記コマンドを実行する。自前の動画を使用する場合はrun.shのinputパスを書き換えて実行する。
```
bash run.sh
```
出力動画は下記のように顔bboxと左右目bboxが緑、ランドマークが黄色、視線が青で表されます。
![スクリーンショット 2026-04-10 113218.png](http://hr-dash.tech/api/files/articles/2026-04/bcab4109-e413-4a39-bb52-56bb952c86c6.png)
