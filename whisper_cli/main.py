from openai import OpenAI

from typing import Optional
import typer
from rich import print

import whisper_cli.env as env
from whisper_cli.env import _read_user_config

app = typer.Typer(no_args_is_help=True)
app.add_typer(env.env_app)
app.add_typer(env.key_app)


def get_file_type(file_name: str) -> str:
    """Returns the file type of the file_name."""
    return file_name.split(".")[-1]


def _check_response_format(response_format: Optional[str]):
    if response_format is None:
        return None
    elif response_format in ["json", "text", "srt", "verbose_json", "vtt"]:
        return response_format
    else:
        raise ValueError("Response format not supported by OpenAI.")


def get_file_content(file_name: str) -> str:
    """Returns the content of the file_name."""

    if get_file_type(file_name) not in [
        "mp3",
        "mp4",
        "mpeg",
        "mpga",
        "m4a",
        "wav",
        "webm",
    ]:
        raise ValueError("File type not supported.")

    return open(file_name, "rb")


def get_api_key(env: str = "default") -> str:
    """Returns the API key for the current environment."""
    user_config = _read_user_config()
    for key, value in user_config.items():
        if "active" in value:
            return value["api_key"]

    raise ValueError(
        "No active environment found. Activate one using `whisper activate-env`."
    )


def show_result(result, response_format: Optional[str]):
    """Show result."""

    print(result)


@app.command()
def transcribe(
    file_name: str,
    model: str = "whisper-1",
    prompt: Optional[str] = None,
    response_format: Optional[str] = None,
    temperature: float = 0,
    language: Optional[str] = None,
):
    """Transcribe audio file using whisper."""
    client = OpenAI(api_key=get_api_key())

    # Create kwargs dict, only including non-None values
    kwargs = {
        "model": model,
        "file": get_file_content(file_name),
        "temperature": temperature,
    }

    if prompt is not None:
        kwargs["prompt"] = prompt
    if response_format is not None:
        kwargs["response_format"] = _check_response_format(response_format)
    if language is not None:
        kwargs["language"] = language

    transcript = client.audio.transcriptions.create(**kwargs)

    # TODO: return based on response_format
    show_result(transcript, response_format)


@app.command()
def translate(
    file_name: str,
    model: str = "whisper-1",
    prompt: Optional[str] = None,
    response_format: Optional[str] = None,
    temperature: float = 0,
):
    """Translate audio file using whisper."""
    client = OpenAI(api_key=get_api_key())

    # Create kwargs dict, only including non-None values
    kwargs = {
        "model": model,
        "file": get_file_content(file_name),
        "temperature": temperature,
    }

    if prompt is not None:
        kwargs["prompt"] = prompt
    if response_format is not None:
        kwargs["response_format"] = _check_response_format(response_format)

    translation = client.audio.translations.create(**kwargs)

    show_result(translation, response_format)


if __name__ == "__main__":
    app()
