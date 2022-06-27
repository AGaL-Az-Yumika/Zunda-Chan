#Voicevoxコアライブラリ他
import discord
from discord import app_commands
import core
from colorama import Fore, Back, Style
import datetime
from tqdm import tqdm
import wave
import re
import asyncio
from halo import Halo

#変数初期化 or Botトークンの設定
TOKEN = 'OTQ0ODA0NDQ3MjQxMDExMzEy.GpHIRX.DRZlK1P3itnNG-4tFytIr6_bioGlKLtVFBKy3g'
intents = discord.Intents.default()
intents.message_content = True
vclist = {}
spinner = Halo(text='AzZS Engine Starting Now...', spinner='dots')

def Log_Info(inputText):
    print(Fore.LIGHTBLACK_EX + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + Fore.CYAN + " INFO     " + Fore.YELLOW + "AzZunda-System　" + Fore.LIGHTWHITE_EX + inputText + Style.RESET_ALL)

def Log_Warning(inputText):
    print(Fore.LIGHTBLACK_EX + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + Fore.YELLOW + " WARNING  " + Fore.YELLOW + "AzZunda-System　" + Fore.LIGHTWHITE_EX + inputText + Style.RESET_ALL)

def Log_Error(inputText):
    print(Fore.LIGHTBLACK_EX + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + Fore.RED + " ERROR    " + Fore.YELLOW + "AzZunda-System　" + Fore.LIGHTWHITE_EX + inputText + Style.RESET_ALL)

#BotAPIへの接続
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
Log_Info("Az-Zunda-System 2022(c)")
Log_Info("Write: AzureBit_Yumika and Suwanohiro")

#BotAPI準備完了時の処理(VoiceVox Coreの初期化)
@client.event
async def on_ready():
    Log_Info("システムエンジンを初期化中...")
    with tqdm(total=100, desc='Progress') as pbar:
        pbar.update(30)
        #VoiceVoxの初期化(GPU無効・ずんだもん)
        spinner.start()
        core.initialize(False, 0)
        pbar.update(60)
        #OpenjTalkのライブラリを取得
        core.voicevox_load_openjtalk_dict("C:\\Users\\yumik\\Desktop\\open_jtalk_dic_utf_8-1.11")
        pbar.update(10)
        spinner.stop()
    Log_Info("エンジンの初期化が正常に完了しました。設定値は　CPU Mode です")
    Log_Info("エンジンが読み上げ対象を待機しています...")

#入室コマンドの実行条件
@tree.command(guild = discord.Object(id=541621751906304020), name = 'join', description='ずんだもんをボイスチャンネルへ参加させるためのコマンドです')
async def join(interaction: discord.Interaction):
    Log_Info("ボイスチャンネルへの参加を要求されました")
    #呼び出し対象ユーザーの入室チェックとすでに参加している場合はボットの退室処理を実行
    if interaction.user.voice is None:
        Log_Error("音声チャンネルへ入室していないためボットを参加させることができません")
        await interaction.response.send_message(f"音声チャンネルへ入室していないためボットを参加させることができません。", ephemeral=True)
        return
    if interaction.guild.voice_client is not None:
        del vclist[interaction.guild.id]
        vc = interaction.guild.voice_client
        await vc.disconnect()
        Log_Warning("すでにボットが参加しているため切断させました")
        await interaction.response.send_message(f"すでにボットが参加しているため切断させました。", ephemeral=True)
        return
    else:
        vclist[interaction.guild.id] = interaction.channel.id
        #|ATTENTION|:退室時の呼び出し対象の値とは若干違うので注意
        vc = interaction.user.voice.channel
        #入室処理を非同期で実行
        await vc.connect()
        Log_Info("ボイスチャンネルへ正常に参加しました")
        await interaction.response.send_message(f"ボイスチャンネルへ正常に参加しました。", ephemeral=True)
        return

#退室コマンドの実行条件
@tree.command(guild = discord.Object(id=541621751906304020), name = 'disconnect', description='ずんだもんをボイスチャンネルから退出させるためのコマンドです。')
async def disconnect(interaction: discord.Interaction):
    Log_Info("ボットの退室を要求されました")
    #ボットの参加チェックを実施後、参加済みの場合のみ退室処理を実行
    if interaction.guild.voice_client is not None:
        del vclist[interaction.guild.id]
        #|ATTENTION|:入室時の呼び出し対象の値とは若干違うので注意
        vc = interaction.guild.voice_client
        #退室処理を非同期で実行
        await vc.disconnect()
        Log_Info("ボットを正常に退室させました")
        await interaction.response.send_message(f"ボットを正常に退室させました。", ephemeral=True)
        return
    else:
        Log_Error("ボットがボイスチャンネルへ参加していません")
        await interaction.response.send_message(f"ボットがボイスチャンネルへ参加していません。", ephemeral=True)
        return

#メッセージ取得処理
@client.event
async def on_message(message):
    #ボットから送信されたメッセージはスキップします。
    if message.author.bot:
        Log_Info("ボットからのメッセージを検出したため処理を中断しました")
        return
    voice = discord.utils.get(client.voice_clients, guild=message.guild)

    #取得文字列からURLと絵文字を正規表現除外。また、VoiceVox WAV 音声データ生成し、Discordボイスチャンネルにて音声を再生するようにOpusを経由して送信
    if voice and voice.is_connected and message.channel.id == vclist[message.guild.id]:
        pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        pattern_kai = "\n"
        pattern_emoji = "\<.+?\>"

        output = re.sub(pattern, "URL省略", message.content)
        output = re.sub(pattern_kai, "。", output)
        output = re.sub(pattern_emoji, "", output)
        if len(output) > 50:
            output = output[:len(output)-50]
            output += "。以下略"
        Log_Info("メッセージ検出: " + output)

        while message.guild.voice_client.is_playing():
            await asyncio.sleep(0.1)
        source = discord.FFmpegPCMAudio(creat_WAV(output))
        message.guild.voice_client.play(source)
        return
    else:
        return

#音声チャンネルにボットのみとなった場合に自動的に退室させる。
@client.event
async def on_voice_state_update(member, before, after):
    voicestate = member.guild.voice_client
    if voicestate is None:
        return
    if len(voicestate.channel.members) == 1:
        await voicestate.disconnect()

#VoiceVox WAV 音声データの生成
def creat_WAV(inputText):
    filename = "Output.wav"
    #VoiceVox Coreにて音声データの生成
    wavefmt = core.voicevox_tts(inputText, 1)
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(wavefmt)
    wf.close()
    return filename

#ボット実行
if __name__ == '__main__':
    client.run(TOKEN)
