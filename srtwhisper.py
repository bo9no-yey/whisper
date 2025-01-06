import whisper
import os
import shutil
import traceback
from pydub import AudioSegment
from tkinter import filedialog
from tkinter import Tk

def generate_srt(file_path, output_folder, error_log_path):
    try:
        # 音声ファイルの読み込み
        audio = AudioSegment.from_file(file_path)

        # 1分（60秒）の間隔で分割
        interval = 60 * 1000  # 1分をミリ秒で表現
        chunks = [audio[i:i + interval] for i in range(0, len(audio), interval)]

        # Whisperモデルの読み込み
        model = whisper.load_model("large-v3")

        # SRTファイル名を設定
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        srt_file_path = os.path.join(output_folder, f"{base_name}.srt")

        with open(srt_file_path, "w", encoding="utf-8") as srt_file:
            start_time = 0
            srt_index = 1
            for i, chunk in enumerate(chunks):
                if chunk.dBFS < -50:
                    print(f"セグメント {i+1} は無音と判断されました。スキップします。")
                    start_time += len(chunk)
                    continue

                print(f"セグメント {i+1}/{len(chunks)} を処理中...")

                chunk.export("temp.wav", format="wav")
                result = model.transcribe("temp.wav", verbose=True, language="ja")
                os.remove("temp.wav")

                print(result['text'])

                end_time = start_time + len(chunk)
                srt_file.write(f"{srt_index}\n")
                srt_file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                srt_file.write(f"{result['text']}\n\n")

                start_time = end_time
                srt_index += 1

            print("全てのセグメントの変換が完了しました。")

    except Exception as e:
        error_log = f"エラーが発生しました: {e}\n"
        error_log += "".join(traceback.format_tb(e.__traceback__))
        error_log += f"{file_path} の処理をスキップします。\n"

        # エラーログをファイルに書き込む
        with open(error_log_path, "a") as file:
            file.write(error_log)

def format_time(ms):
    hours, remainder = divmod(ms, 3600000)
    minutes, seconds = divmod(remainder, 60000)
    seconds, milliseconds = divmod(seconds, 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"

def process_directory():
    root = Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory()
    if not directory_path:
        print("ディレクトリが選択されなかった")
        return

    output_base_path = filedialog.askdirectory()
    if not output_base_path:
        print("出力ディレクトリが選択されなかった")
        return

    error_log_path = os.path.join(output_base_path, "error_log.txt")
    
    mkv_files = [f for f in os.listdir(directory_path) if f.endswith(".mkv")]
    mkv_files.sort(reverse=True)

    for i, filename in enumerate(mkv_files, start=1):
        print(f"ファイル名: {filename} ({i}/{len(mkv_files)})")
        file_path = os.path.join(directory_path, filename)
        output_folder_path = os.path.join(output_base_path, os.path.splitext(filename)[0])
        output_file_path = os.path.join(output_folder_path, filename)

        # ファイルが既に存在する場合はスキップ
        if os.path.exists(output_file_path):
            error_msg = f"エラー: ファイル {output_file_path} は既に存在します。\n"
            print(error_msg)
            with open(error_log_path, "a") as file:
                file.write(error_msg)
            continue

        os.makedirs(output_folder_path, exist_ok=True)
        shutil.move(file_path, output_folder_path)
        generate_srt(os.path.join(output_folder_path, filename), output_folder_path, error_log_path)

process_directory()