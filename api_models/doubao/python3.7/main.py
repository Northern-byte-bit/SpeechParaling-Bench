import asyncio
import argparse
import os

import config
from audio_manager import DialogSession

DEFAULT_INPUT_DIR = "audio_dataset_en/para_con/con_long_sin"
DEFAULT_OUTPUT_DIR = "api_models/doubao/output_en/para_con/con_long_sin"


async def run_one(file_path: str, audio_format: str, mod: str,
                  recv_timeout: int, output_dir: str) -> None:
    base = os.path.splitext(os.path.basename(file_path))[0]
    os.makedirs(output_dir, exist_ok=True)
    out_wav = os.path.join(output_dir, f"{base}.wav")
    session = DialogSession(
        ws_config=config.ws_connect_config,
        output_audio_format=audio_format,
        audio_file_path=file_path,
        mod=mod,
        recv_timeout=recv_timeout,
        output_file_path=out_wav,
    )
    await session.start()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Real-time Dialog Client (batch)")
    parser.add_argument("--format",
                        type=str,
                        default="pcm",
                        help="The audio format (e.g., pcm, pcm_s16le).")
    parser.add_argument(
        "--audio",
        type=str,
        default="",
        help="single audio file; if empty, will run batch from input dir.")
    parser.add_argument("--mod",
                        type=str,
                        default="audio",
                        help="text or audio mode; default audio")
    parser.add_argument("--recv_timeout",
                        type=int,
                        default=10,
                        help="Timeout for receiving messages, range [10,120]")
    parser.add_argument("--input_dir",
                        type=str,
                        default=DEFAULT_INPUT_DIR,
                        help="directory containing wav files for batch")
    parser.add_argument("--output_dir",
                        type=str,
                        default=DEFAULT_OUTPUT_DIR,
                        help="directory to store outputs")

    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    if args.audio:
        await run_one(args.audio, args.format, args.mod, args.recv_timeout,
                      output_dir)
        return

    files = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if f.lower().endswith(".wav")
    ]
    files.sort()
    for fp in files:
        await run_one(fp, args.format, args.mod, args.recv_timeout, output_dir)


if __name__ == "__main__":
    asyncio.run(main())
