import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spacy_utils.split_by_comma import split_by_comma_main
from spacy_utils.split_by_connector import split_sentences_main
from spacy_utils.split_by_mark import split_by_mark
from spacy_utils.split_long_by_root import split_long_by_root_main
from spacy_utils.load_nlp_model import init_nlp
from core.video_config import video_config

def split_by_spacy():
    output_dir = video_config.output_dir
    final_split_file = os.path.join(output_dir, "log", "sentence_splitbynlp.txt")
    if os.path.exists(final_split_file):
        print("File 'sentence_splitbynlp.txt' already exists. Skipping split_by_spacy.")
        return
    
    nlp = init_nlp()
    split_by_mark(nlp)
    split_by_comma_main(nlp)
    split_sentences_main(nlp)
    split_long_by_root_main(nlp)
    return

if __name__ == '__main__':
    split_by_spacy()