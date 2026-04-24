import os
import shlex

import modal
from dotenv import load_dotenv

load_dotenv(override=True)

APP_NAME = os.getenv("MODAL_APP_NAME", "llm-service2")
DEFAULT_MODEL = "Qwen/Qwen3-1.7B"
DEFAULT_DTYPE = os.getenv("VLLM_DTYPE", "auto")

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("python-dotenv", "vllm>=0.7.3")
)

secret = modal.Secret.from_name("huggingface-secret")
volume = modal.Volume.from_name("llm-service-cache", create_if_missing=True)


@app.function(
    image=image,
    secrets=[secret],
    volumes={"/.cache": volume},
    gpu=os.getenv("MODAL_GPU", "A10G"),
    min_containers=1,
    max_containers=3,
    scaledown_window=300,
    timeout=3600,
)
@modal.web_server(port=8000, startup_timeout=600)
def serve():
    model_name = (
        os.getenv("LLM_MODEL_NAME")
        or os.getenv("CHAT_MODEL_NAME")
        or DEFAULT_MODEL
    )
    api_key = os.getenv("LLM_API_KEY") or "abc"
    tensor_parallel_size = os.getenv("TENSOR_PARALLEL_SIZE", "1")
    max_model_len = os.getenv("MAX_MODEL_LEN", "4096")
    gpu_memory_utilization = os.getenv("GPU_MEMORY_UTILIZATION", "0.9")
    dtype = os.getenv("VLLM_DTYPE", DEFAULT_DTYPE)
    generation_config = os.getenv("VLLM_GENERATION_CONFIG", "vllm")
    chat_template_content_format = os.getenv(
        "VLLM_CHAT_TEMPLATE_CONTENT_FORMAT",
        "string",
    )
    extra_args = os.getenv("VLLM_EXTRA_ARGS", "")

    cmd = [
        "vllm",
        "serve",
        model_name,
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--api-key",
        api_key,
        "--tensor-parallel-size",
        tensor_parallel_size,
        "--max-model-len",
        max_model_len,
        "--gpu-memory-utilization",
        gpu_memory_utilization,
        "--dtype",
        dtype,
        "--generation-config",
        generation_config,
        "--chat-template-content-format",
        chat_template_content_format,
        "--trust-remote-code",
        "--served-model-name",
        model_name,
    ]

    if extra_args.strip():
        cmd.extend(shlex.split(extra_args))

    os.execvp(cmd[0], cmd)