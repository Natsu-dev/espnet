import datetime
import os
from contextlib import redirect_stdout
import re
import sys
import pyopenjtalk
from espnet2.text.build_tokenizer import build_tokenizer

args = sys.argv
input_path = args[1]
output_path = args[2]

# 置換用リスト
double_tokens = ["sh", "cl", "ts", "ch", "ky", "ry", "gy", "hy", "ny", "by", "my", "py", "dy", "ty"]
single_tokens = ["し", "っ", "つ", "ち", "き", "り", "ぎ", "ひ", "に", "び", "み", "ぴ", "ぢ", "て"]

_remove_titles = ["BASIC5000_2036", "BASIC5000_3026", "BASIC5000_3078", "BASIC5000_3127", "BASIC5000_3165", "BASIC5000_3182", "BASIC5000_3460", "BASIC5000_3498", "BASIC5000_3531", "BASIC5000_3541", "BASIC5000_3593", "BASIC5000_3632", "BASIC5000_3762", "BASIC5000_3816", "BASIC5000_3908", "BASIC5000_3931", "BASIC5000_3967", "BASIC5000_4026", "BASIC5000_4051", "BASIC5000_4064", "BASIC5000_4091", "BASIC5000_4244", "BASIC5000_4353", "BASIC5000_4454", "BASIC5000_4474"]

tokenizer_kana = build_tokenizer(
    token_type="phn",
    bpemodel=None,
    delimiter=None,
    space_symbol="<space>",
    non_linguistic_symbols=None,
    g2p_type="pyopenjtalk_kana"
)

tokenizer = build_tokenizer(
    token_type="phn",
    bpemodel=None,
    delimiter=None,
    space_symbol="<space>",
    non_linguistic_symbols=None,
    g2p_type="pyopenjtalk_prosody"
)

def file_check(path):
    if os.path.isdir(path):
        # directoryだったら中のファイルに対して再帰的にこの関数を実行
        filenames = os.listdir(path)
        for filename in filenames:
            file_check(path + "/" + filename)
    else:
        # fileだったら処理
        open_filepath = path
        write_filepath = output_path + path.replace(input_path, "")

        print(f"open_filepath: {open_filepath}")

        if "text" in path:
            kanaize(open_filepath, write_filepath)

        elif "spk2utt" in path:
            remove_titles(open_filepath, write_filepath)

        elif "utt2spk" in path:
            remove_title_lines(open_filepath, write_filepath)

        elif "wav.scp" in path:
            remove_title_lines(open_filepath, write_filepath)

        print(f"write_filepath: {write_filepath}")


def kanaize(input_file_name, output_file_name):
    out_lines = []
    with open(input_file_name, encoding="utf8") as f:
        lines = f.read().split("\n")

    # 文字列置換
    for i in range(len(lines)):
        line_split = lines[i].split(" ", 1)
        # print(line_split[1])
        if len(line_split) == 2:
            # 音素変換できないやつを炙り出す
            #line_kanaized = "".join(tokenizer_kana.text2tokens(line_split[1]))
            #if re.search(r"[々〇〻\u3400-\u9FFF\uF900-\uFAFF]|[\uD840-\uD87F][\uDC00-\uDFFF]", line_kanaized):
            #    _remove_titles.append(line_split[0])

            line_split[1] = " ".join(tokenizer.text2tokens(line_split[1]))
            # 2文字からなる音素の置換
            for j in range(len(double_tokens)):
                line_split[1] = line_split[1].replace(double_tokens[j], single_tokens[j])
                lines[i] = line_split[0] + " " + line_split[1]

        # print(lines[i])

    for k in range(len(lines)):
        if lines[k].split(" ")[0] in _remove_titles:
            print(f"removed line: {lines[k]}")
        else:
            out_lines.append(lines[k])

    # ファイル名をつけて保存
    with open(output_file_name, mode="w", encoding="utf8") as f:
        f.write("\n".join(out_lines))

def remove_titles(input_file_name, output_file_name):
    with open(input_file_name, encoding="utf8") as f:
        text = f.read()

    # _remove_titlesに入ってるやつは除外
    for remove_title in _remove_titles:
        if remove_title in text:
            text = text.replace(f"{remove_title} ", "")
            print(f"removed title: {remove_title}")

    # ファイル名をつけて保存
    with open(output_file_name, mode="w", encoding="utf8") as f:
        f.write(text)

def remove_title_lines(input_file_name, output_file_name):
    out_lines = []
    with open(input_file_name, encoding="utf8") as f:
        lines = f.read().split("\n")

    # _remove_titlesに入ってるやつは除外
    for i in range(len(lines)):
        if lines[i].split(" ")[0] in _remove_titles:
            print(f"removed line: {lines[i]}")
        else:
            out_lines.append(lines[i])

    # ファイル名をつけて保存
    with open(output_file_name, mode="w", encoding="utf8") as f:
        f.write("\n".join(out_lines))


file_check(input_path)
print(f"Done tokenizing '{args[1]}'.")
with open(f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}", mode="w", encoding="utf8") as f:
    f.write("\"" + "\", \"".join(_remove_titles) + "\"")
