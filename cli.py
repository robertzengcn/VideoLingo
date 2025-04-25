#!/usr/bin/env python3

import argparse
import os
import sys
import json
from core.config_utils import load_key
from core.video_config import video_config
from st_components.imports_and_utils import *
import core.step2_whisperX
import core.step3_1_spacy_split
import core.step3_2_splitbymeaning
import core.step4_1_summarize
import core.step4_2_translate_all
import core.step5_splitforsub
import core.step6_generate_final_timeline
import core.step7_merge_sub_to_vid
import core.step8_1_gen_audio_task
import core.step8_2_gen_dub_chunks
import core.step9_extract_refer_audio
import core.step10_gen_audio
import core.step11_merge_full_audio
import core.step12_merge_dub_to_vid

def process_subtitles(video_path, output_dir):
    """Process video subtitles."""
    try:
        # Set video path and output directory in config
        video_config.video_path = video_path
        video_config.output_dir = output_dir
        
        print(f"Starting subtitle processing for video: {video_path}")
        
        print("Using Whisper for transcription...")
        step2_whisperX.transcribe()
        
        print("Splitting long sentences...")
        step3_1_spacy_split.split_by_spacy()
        step3_2_splitbymeaning.split_sentences_by_meaning()
        
        print("Summarizing and translating...")
        step4_1_summarize.get_summary()
        step4_2_translate_all.translate_all()
        
        print("Processing and aligning subtitles...")
        step5_splitforsub.split_for_sub_main()
        step6_generate_final_timeline.align_timestamp_main()
        
        print("Merging subtitles to video...")
        step7_merge_sub_to_vid.merge_subtitles_to_video()
        
        print("Subtitle processing complete! 🎉")
        return True
    except Exception as e:
        print(f"Error processing subtitles for {video_path}: {str(e)}")
        return False
    finally:
        # Reset config after processing
        video_config.reset()

def process_dubbing(video_path, output_dir=None):
    """Process video dubbing."""
    try:
        # Set video path and output directory in config
        video_config.video_path = video_path
        if output_dir:
            video_config.output_dir = output_dir
        
        print(f"Starting audio processing for video: {video_path}")
        
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
        return True
    except Exception as e:
        print(f"Error processing dubbing for {video_path}: {str(e)}")
        return False
    finally:
        # Reset config after processing
        video_config.reset()

def process_batch(video_list_path, output_base_dir, mode='subtitles'):
    """Process multiple videos from a list file."""
    if not os.path.exists(video_list_path):
        print(f"Error: Video list file '{video_list_path}' does not exist.")
        return
    
    try:
        with open(video_list_path, 'r', encoding='utf-8') as f:
            video_list = json.load(f)
    except json.JSONDecodeError:
        print("Error: Video list file must be a valid JSON file containing a list of video paths.")
        return
    
    if not isinstance(video_list, list):
        print("Error: Video list file must contain a JSON array of video paths.")
        return
    
    results = []
    for video_path in video_list:
        # Create a unique output directory for each video
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(output_base_dir, video_name)
        
        if mode == 'subtitles':
            success = process_subtitles(video_path, output_dir)
        else:  # mode == 'dub'
            success = process_dubbing(video_path, output_dir)
        
        results.append({
            'video': video_path,
            'success': success
        })
    
    # Print summary
    print("\nProcessing Summary:")
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['video']}")

def main():
    parser = argparse.ArgumentParser(description='VideoLingo CLI - Video translation and dubbing tool')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Subtitle processing command
    sub_parser = subparsers.add_parser('subtitles', help='Process video subtitles')
    sub_parser.add_argument('video_path', help='Path to the input video file')
    sub_parser.add_argument('--output-dir', help='Output directory for processed files')
    
    # Dubbing command
    dub_parser = subparsers.add_parser('dub', help='Process video dubbing')
    dub_parser.add_argument('video_path', help='Path to the input video file')
    dub_parser.add_argument('--output-dir', help='Output directory for processed files')
    
    # Batch processing command
    batch_parser = subparsers.add_parser('batch', help='Process multiple videos')
    batch_parser.add_argument('video_list', help='JSON file containing list of video paths')
    batch_parser.add_argument('output_dir', help='Base output directory for all processed videos')
    batch_parser.add_argument('--mode', choices=['subtitles', 'dub'], default='subtitles',
                            help='Processing mode (subtitles or dubbing)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure settings')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'),
                             help='Set a configuration value')
    config_parser.add_argument('--get', metavar='KEY',
                             help='Get a configuration value')
    
    args = parser.parse_args()
    
    video_config.video_path = args.video_path
    video_config.output_dir = args.output_dir
    if args.command == 'subtitles':
        if not args.output_dir:
            print("Error: --output-dir is required for subtitle processing")
            sys.exit(1)
        process_subtitles(args.video_path, args.output_dir)
    elif args.command == 'dub':
        process_dubbing(args.video_path, args.output_dir)
    elif args.command == 'batch':
        process_batch(args.video_list, args.output_dir, args.mode)
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