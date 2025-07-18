import argparse
import importlib
import os
import tempfile
from itertools import chain
from typing import List
import sys

from pose_format import Pose

from spoken_to_signed.gloss_to_pose import gloss_to_pose, CSVPoseLookup, concatenate_poses
from spoken_to_signed.gloss_to_pose.lookup.fingerspelling_lookup import FingerspellingPoseLookup
from spoken_to_signed.text_to_gloss.types import Gloss


def _text_to_gloss(text: str, language: str, glosser: str, **kwargs) -> List[Gloss]:
    module = importlib.import_module(f"spoken_to_signed.text_to_gloss.{glosser}")
    return module.text_to_gloss(text=text, language=language, **kwargs)


def _gloss_to_pose(sentences: List[Gloss], lexicon: str, spoken_language: str, signed_language: str) -> Pose:
    # Không dùng fingerspelling backup
    pose_lookup = CSVPoseLookup(lexicon)
    poses = [gloss_to_pose(gloss, pose_lookup, spoken_language, signed_language) for gloss in sentences]
    if len(poses) == 1:
        return poses[0]
    return concatenate_poses(poses, trim=False)


def _get_models_dir():
    home_dir = os.path.expanduser("~")
    sign_dir = os.path.join(home_dir, ".sign")
    os.makedirs(sign_dir, exist_ok=True)
    models_dir = os.path.join(sign_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    return models_dir


def _pose_to_video(pose: Pose, video_path: str):
    models_dir = _get_models_dir()
    pix2pix_path = os.path.join(models_dir, "pix2pix.h5")
    if not os.path.exists(pix2pix_path):
        print("Downloading pix2pix model")
        import urllib.request
        urllib.request.urlretrieve(
            "https://firebasestorage.googleapis.com/v0/b/sign-mt-assets/o/models%2Fgenerator%2Fmodel.h5?alt=media",
            pix2pix_path)

    import subprocess

    try:
        subprocess.run(["command", "-v", "pose_to_video"], shell=True, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "The command 'pose_to_video' does not exist. Please install the `transcription` package using "
            "`pip install git+https://github.com/sign-language-processing/transcription`")

    pose_path = tempfile.mktemp(suffix=".pose")
    with open(pose_path, "wb") as f:
        pose.write(f)

    args = ["pose_to_video", "--type=pix_to_pix",
            "--model", pix2pix_path,
            "--pose", pose_path,
            "--video", video_path,
            "--upscale"]
    print(" ".join(args))
    subprocess.run(args, shell=True, check=True)


def _text_input_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--glosser", choices=['simple', 'spacylemma', 'rules', 'nmt'], required=True)

    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--lexicon", type=str)
    pre_args, _ = pre_parser.parse_known_args()

    if pre_args.lexicon:
        lookup = CSVPoseLookup(pre_args.lexicon)
        spoken_languages = list(lookup.words_index.keys())
        signed_languages = set(chain.from_iterable(lookup.words_index[lang].keys() for lang in spoken_languages))
    else:
        spoken_languages = ['de', 'fr', 'it', 'en']
        signed_languages = ['sgg', 'gsg', 'bfi', 'ase']

    parser.add_argument("--spoken-language", choices=spoken_languages, required=True)
    parser.add_argument("--signed-language", choices=signed_languages, required=True)


def text_to_gloss():
    args_parser = argparse.ArgumentParser()
    _text_input_arguments(args_parser)
    args = args_parser.parse_args()

    print("Text to gloss")
    print("Input text:", args.text)
    sentences = _text_to_gloss(args.text, args.spoken_language, args.glosser)
    print("Output gloss:", sentences)


def pose_to_video():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--pose", type=str, required=True)
    args_parser.add_argument("--video", type=str, required=True)
    args = args_parser.parse_args()

    with open(args.pose, "rb") as f:
        pose = Pose.read(f.read())

    _pose_to_video(pose, args.video)

    print("Pose to video")
    print("Input pose:", args.pose)
    print("Output video:", args.video)


def text_to_gloss_to_pose():
    args_parser = argparse.ArgumentParser()
    _text_input_arguments(args_parser)
    args_parser.add_argument("--lexicon", type=str, required=True)
    args_parser.add_argument("--pose", type=str, required=True)
    args = args_parser.parse_args()

    sentences = _text_to_gloss(args.text, args.spoken_language, args.glosser)
    pose = _gloss_to_pose(sentences, args.lexicon, args.spoken_language, args.signed_language)

    with open(args.pose, "wb") as f:
        pose.write(f)

    print("Text to gloss to pose")
    print("Input text:", args.text)
    print("Output pose:", args.pose)


def text_to_gloss_to_pose_to_video():
    args_parser = argparse.ArgumentParser()
    _text_input_arguments(args_parser)
    args_parser.add_argument("--lexicon", type=str, required=True)
    args_parser.add_argument("--video", type=str, required=True)
    args = args_parser.parse_args()

    sentences = _text_to_gloss(args.text, args.spoken_language, args.glosser, signed_language=args.signed_language)
    pose = _gloss_to_pose(sentences, args.lexicon, args.spoken_language, args.signed_language)
    _pose_to_video(pose, args.video)

    print("Text to gloss to pose to video")
    print("Input text:", args.text)
    print("Output video:", args.video)

# ...existing code...
import argparse
import sys
import os
from pose_format import Pose
from spoken_to_signed.gloss_to_pose import CSVPoseLookup, concatenate_poses

def direct_to_pose():
    args_parser = argparse.ArgumentParser(description="Convert text to gloss to pose")
    args_parser.add_argument("--text", type=str, required=True, help="Input text to convert")
    args_parser.add_argument("--glosser", choices=['simple', 'spacylemma', 'rules', 'nmt', 'gpt'], required=True, help="Glosser method to use")
    args_parser.add_argument("--lexicon", type=str, required=True, help="Path to lexicon directory")
    args_parser.add_argument("--spoken-language", choices=['vi', 'de', 'fr', 'it', 'en'], required=True, help="Spoken language")
    args_parser.add_argument("--signed-language", choices=['vsl', 'sgg', 'ssr', 'slf', 'gsg', 'bfi', 'ase'], required=True, help="Signed language")
    args_parser.add_argument("--pose", type=str, required=True, help="Output pose file path")
    
    args = args_parser.parse_args()

    try:
        print(f"Converting text to gloss: '{args.text}'")
        
        # Step 1: Convert text to gloss using the specified glosser
        sentences = _text_to_gloss(
            text=args.text,
            language=args.spoken_language,
            glosser=args.glosser,
            signed_language=args.signed_language
        )
        
        print(f"Generated glosses: {sentences}")
        
        if not sentences:
            print("Error: No glosses generated from input text")
            sys.exit(1)
        
        # Step 2: Convert gloss to pose
        print("Converting gloss to pose...")
        pose = _gloss_to_pose(
            sentences=sentences,
            lexicon=args.lexicon,
            spoken_language=args.spoken_language,
            signed_language=args.signed_language
        )
        
        if pose is None:
            print("Error: Failed to generate pose from glosses")
            sys.exit(1)
        
        # Step 3: Save pose to file
        print(f"Saving pose to: {args.pose}")
        with open(args.pose, "wb") as f:
            pose.write(f)
        
        print("Successfully completed text to gloss to pose conversion!")
        print(f"Input text: {args.text}")
        print(f"Generated glosses: {sentences}")
        print(f"Output pose file: {args.pose}")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Update the main execution
if __name__ == "__main__":
    # Determine which function to run based on script name or argument
    import sys
    if len(sys.argv) > 0 and 'text_to_gloss_to_pose' in sys.argv[0]:
        direct_to_pose()
    else:
        direct_to_pose()  # Default to the new function
        
        
# python -m spoken_to_signed.bin --text "chào tôi tên là Thành, tôi dạy ở UIT" --glosser gpt --lexicon "assets/vietnamese_lexicon" --spoken-language vi --signed-language vsl --pose output.pose