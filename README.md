# whisper

## 前提環境

- Python 3.12.8
- ffmpeg version 2024-12-04-git-2f95bc3cb3-full_build-www.gyan.dev

## 環境構築

```bash
python3 -m venv whisper_env
source whisper_env/bin/activate  # Windowsの場合は whisper_env\Scripts\activate
pip install -r requirements.txt
```

## 仮想環境へのアクティベート

bash  
`whisper_env\Scripts\activate`  

ps  
`.\whisper_env\Scripts\Activate.ps1`  

## 実行

`python .\srtwhisper.py`  
