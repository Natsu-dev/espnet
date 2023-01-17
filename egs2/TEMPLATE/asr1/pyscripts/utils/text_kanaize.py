import os
from contextlib import redirect_stdout
import sys
import pyopenjtalk
from espnet2.text.build_tokenizer import build_tokenizer

args = sys.argv
input_file_name = args[1]
output_file_name = args[1]

tokenizer = build_tokenizer(
    token_type="phn",
    bpemodel=None,
    delimiter=None,
    space_symbol="<space>",
    non_linguistic_symbols=None,
    g2p_type="pyopenjtalk_kana"
)

with open(input_file_name, encoding="utf8") as f:
    lines = f.read().split("\n")

with redirect_stdout(open(os.devnull, 'w')):
# 文字列置換
    for i in range(len(lines)):
        line_split = lines[i].split(" ", 1)
        if len(line_split) != 2:
            continue
        lines[i] = line_split[0] + " " + " ".join(tokenizer.text2tokens(line_split[1]))
        # print(lines[i])

# 同じファイル名で保存
with open(output_file_name, mode="w", encoding="utf8") as f:
    f.write("\n".join(lines))

print(f"Done tokenizing '{args[1]}'.")
