from models.layout import Layout
from parser.corpus_parser import CorpusParser

layout = Layout.load(
    "config/layouts/harmonia_v5_1b.json"
)

parser = CorpusParser(layout)

sequence = parser.parse("Hello!")

print(sequence)

for key in sequence:
    print(key)