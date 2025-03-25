#!/usr/bin/env python3

import argparse
import os
import sys
from core.config_utils import load_key, save_key
from st_components.imports_and_utils import *
import step2_whisperX
import step3_1_spacy_split
import step3_2_splitbymeaning
import step4_1_summarize
import step4_2_translate_all
import step5_splitforsub
import step6_generate_final_timeline
import step7_merge_sub_to_vid
import step8_1_gen_audio_task
import step8_2_gen_dub_chunks
import step9_extract_refer_audio
import step10_gen_audio
import step11_merge_full_audio
import step12_merge_dub_to_vid

def process_subtitles(pause_before_translate=False):
    """Process video subtitles."""
    print("Starting subtitle processing...")
    
    print("Using Whisper for transcription...")
    step2_whisperX.transcribe()
    
    print("Splitting long sentences...")
    step3_1_spacy_split.split_by_spacy()
    step3_2_splitbymeaning.split_sentences_by_meaning()
    
    print("Summarizing and translating...")
    step4_1_summarize.get_summary()
    if pause_before_translate:
        input("⚠️ PAUSE_BEFORE_TRANSLATE. Go to `output/log/terminology.json` to edit terminology. Then press ENTER to continue...")
    step4_2_translate_all.translate_all()
    
    print("Processing and aligning subtitles...")
    step5_splitforsub.split_for_sub_main()
    step6_generate_final_timeline.align_timestamp_main()
    
    print("Merging subtitles to video...")
    step7_merge_sub_to_vid.merge_subtitles_to_video()
    
    print("Subtitle processing complete! 🎉")

def process_dubbing():
    """Process video dubbing."""
    print("Starting audio processing...")
    
    print("Generate audio tasks...")
    step8_1_gen_audio_task.gen_audio_task_main()
    step8_2_gen_dub_chunks.gen_dub_chunks()
    
    print("Extract reference audio...")
    step9_extract_refer_audio.extract_refer_audio_main()
    
    print("Generate all audio...")
    step10_gen_audio.gen_audio()
    
    print("Merge full audio...")
    step11_merge_full_audio.merge_full_audio()
    
    print("Merge dubbing to the video...")
    step12_merge_dub_to_vid.merge_video_audio()
    
    print("Audio processing complete! 🎇")

def main():
    parser = argparse.ArgumentParser(description='VideoLingo CLI - Video translation and dubbing tool')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Subtitle processing command
    sub_parser = subparsers.add_parser('subtitles', help='Process video subtitles')
    sub_parser.add_argument('--pause-before-translate', action='store_true',
                           help='Pause before translation to edit terminology')
    
    # Dubbing command
    dub_parser = subparsers.add_parser('dub', help='Process video dubbing')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure settings')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'),
                             help='Set a configuration value')
    config_parser.add_argument('--get', metavar='KEY',
                             help='Get a configuration value')
    
    args = parser.parse_args()
    
    if args.command == 'subtitles':
        process_subtitles(args.pause_before_translate)
    elif args.command == 'dub':
        process_dubbing()
    elif args.command == 'config':
        if args.set:
            key, value = args.set
            # Convert string to boolean if needed
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            save_key(key, value)
            print(f"Set {key} = {value}")
        elif args.get:
            value = load_key(args.get)
            print(f"{args.get} = {value}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 