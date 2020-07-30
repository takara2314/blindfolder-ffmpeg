import os
import shutil
import subprocess
import sys
import cv2

# video.mp4 が見つからなければ警告
if not os.path.exists("video.mp4"):
    sys.exit("対象にする動画のファイルを置いてください。また名前は \"video.mp4\" にしてください。")
else:
    print("\"video.mp4\" を読み込みます。")


# stillsフォルダ(静止画保存フォルダ)がなければ作成
if not os.path.exists("stills"):
    os.mkdir("stills")
else:
    print("新しく動画を読み込むために、stillsフォルダの中をすべて削除します。")
    if input("OK(y) / NG(other): ") == "y":
        shutil.rmtree("stills")
        os.mkdir("stills")
        print("フォルダの中身をすべて削除しました。")
    else:
        sys.exit("ファイルの中身を消せる状態にしてから実行してください。")


print("動画を15FPSで読み込み、静止画に変換します。少々お待ちください。")
shutil.copy("video.mp4", "stills")
# 作業ディレクトリをstillsにし、FFmpegでの変換コマンドを実行結果を非表示で実行
os.chdir("stills")
FNULL = open(os.devnull, 'w')
subprocess.run(["ffmpeg", "-i", "video.mp4", "-r", "30", "-vcodec", "png", "image_%03d.png"], stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
os.remove("video.mp4")
print("変換しました。")


# 正面顔のカスケード分類器を読み込む
face_cascade = cv2.CascadeClassifier("../haarcascade_frontalface_default.xml")
# 目のカスケード分類器を読み込む
eye_cascade = cv2.CascadeClassifier("../haarcascade_eye.xml")

print("各静止画から顔と目を検知します。")
counter = 1
os.mkdir("rectangled")
for pngData in os.listdir("./"):
    if not os.path.isfile(pngData):
        continue

    print("load:", pngData)
    # イメージファイルの読み込み
    img = cv2.imread(pngData)

    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 顔を検知
    faces = face_cascade.detectMultiScale(gray)
    for (x,y,w,h) in faces:
        # 検知した顔を矩形で囲む
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        # 顔画像（グレースケール）
        roi_gray = gray[y:y+h, x:x+w]
        # 顔ｇ増（カラースケール）
        roi_color = img[y:y+h, x:x+w]
        # 顔の中から目を検知
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            # 検知した目を矩形で囲む
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    output_file_name = "rectangled\\image_%03d.png" % counter
    cv2.imwrite(output_file_name, img)
    counter += 1

print("検知しました。")


print("1つの動画に変換します。")
os.chdir("rectangled")
FNULL = open(os.devnull, 'w')
subprocess.run(["ffmpeg", "-framerate", "30", "-i", "image_%03d.png", "-vcodec", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "output.mp4"], stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
shutil.move("output.mp4", "../../output.mp4")
print("変換しました。")