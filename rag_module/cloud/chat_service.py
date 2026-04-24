import modal
from dotenv import load_dotenv
import os
from typing import Any

load_dotenv(override=True)

MODEL_NAME = os.getenv("CHAT_MODEL_NAME")

app = modal.App("llm-service")

secret = modal.Secret.from_name("huggingface-secret")

volume = modal.Volume.from_name("llm-service-cache", create_if_missing=True)

image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi", "transformers", "torch", "python-dotenv", "accelerate"
    )
    .env(
        {
            "CHAT_MODEL_NAME": MODEL_NAME
        }
    )
)

@app.function(
    image=image,
    secrets=[secret],
    volumes={"/.cache": volume},
    gpu="A10G",

    min_containers=1,
    max_containers=3,

    timeout=3600,
)
@modal.asgi_app()
def serve():
    from fastapi import FastAPI, Body, HTTPException
    from pydantic import BaseModel, ConfigDict
    import os
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    from time import time
    from uuid import uuid4

    class ChatMessage(BaseModel):
        role: str
        content: str

    class ChatCompletionRequest(BaseModel):
        model_config = ConfigDict(extra="ignore")

        model: str | None = None
        messages: list[ChatMessage]
        temperature: float | None = 0.1
        max_tokens: int | None = 32768
        max_completion_tokens: int | None = None
        top_p: float | None = 1.0
        stream: bool | None = False
        stop: str | list[str] | None = None

    def build_prompt(messages: list[ChatMessage], tokenizer: Any) -> str:
        chat_messages = [m.model_dump() for m in messages]
        if hasattr(tokenizer, "apply_chat_template"):
            try:
                return tokenizer.apply_chat_template(
                    chat_messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=True
                )
            except Exception:
                pass

        parts = []
        for message in messages:
            parts.append(f"{message.role.lower()}: {message.content}")
        parts.append("assistant:")
        return "\n".join(parts)

    def lifespan(app: FastAPI):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model_name = os.getenv("CHAT_MODEL_NAME")
        # Load the tokenizer and the model once at startup.
        app.state.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/.cache")
        app.state.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            cache_dir="/.cache",
            trust_remote_code=True,
        )
        app.state.model.eval()
        yield
    
    app = FastAPI(lifespan=lifespan)

    @app.get("/v1/models")
    def list_models():
        current_model = os.getenv("CHAT_MODEL_NAME") or "unknown"
        return {
            "object": "list",
            "data": [
                {
                    "id": current_model,
                    "object": "model",
                    "owned_by": "modal",
                }
            ],
        }

    @app.post("/v1/chat/completions")
    def chat_completions(payload: ChatCompletionRequest = Body()):
        if payload.stream:
            raise HTTPException(status_code=400, detail="Streaming is not supported by this adapter")
        if not payload.messages:
            raise HTTPException(status_code=400, detail="messages is required")

        tokenizer = app.state.tokenizer
        model = app.state.model
        max_new_tokens = payload.max_tokens if payload.max_tokens is not None else 32768
        temperature = payload.temperature if payload.temperature is not None else 0.1
        top_p = payload.top_p if payload.top_p is not None else 1.0

        input_template = build_prompt(payload.messages, tokenizer)

        try:
            inputs = tokenizer(input_template, return_tensors="pt")
            inputs = {key: value.to(model.device) for key, value in inputs.items()}

            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=temperature > 0,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.eos_token_id,
                )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"generation_failed: {str(exc)}") from exc

        prompt_len = inputs["input_ids"].shape[-1]
        output_ids = generated_ids[0][prompt_len:].tolist()
        
        content = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")

        response = {
            "id": f"chatcmpl-{uuid4().hex}",
            "object": "chat.completion",
            "created": int(time()),
            "model": payload.model or (os.getenv("CHAT_MODEL_NAME") or MODEL_NAME or "unknown"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_len,
                "completion_tokens": len(output_ids),
                "total_tokens": prompt_len + len(output_ids)
            }
        }
        return response
        
    return app

