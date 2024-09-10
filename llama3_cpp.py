# -*- coding: utf-8 -*-
"""llama-cpp.py

Script to download, convert, and use LLaMA models with llama.cpp

"""

from huggingface_hub import login, snapshot_download, HfApi
import shutil
import os
from llama_cpp import Llama

hf_token = "" 
login(token=hf_token)

# parameters
model_name = "meta-llama/Meta-Llama-3.1-8B"
base_model = "./original_model/"
quantized_model = "./quantized_models/"
gguf_model = "llama_3.1_FP16.gguf"
quantized_gguf_model = "llama_3.1-Q4_K_M.gguf"

# download the base model
snapshot_download(repo_id=model_name, local_dir=base_model, ignore_patterns=["*.pth"])

# clone the llama.cpp repository
os.system("git clone https://github.com/ggerganov/llama.cpp")

# create directories if they do not exist
os.makedirs(quantized_model, exist_ok=True)

# convert model to GGUF format
os.system(f"python llama.cpp/convert_hf_to_gguf.py {base_model} --outfile {quantized_model}/{gguf_model}")

# build llama.cpp and quantize model
os.makedirs("llama.cpp/build", exist_ok=True)
os.system("cd llama.cpp/build && cmake .. && cmake --build . --config Release")
os.system(f"cd llama.cpp/build/bin && ./llama-quantize {quantized_model}/{gguf_model} {quantized_model}/{quantized_gguf_model} q4_K_M")

# save model to Google Drive (assuming you have mounted Google Drive)
drive_path = "/content/drive/My Drive/llama_models/"
os.makedirs(drive_path, exist_ok=True)
shutil.copy(f"{quantized_model}/{quantized_gguf_model}", f"{drive_path}/{quantized_gguf_model}")

# upload model to Hugging Face Hub
api = HfApi()
model_id = "cindyangelira/llama3.1-Q4_K_M-gguf"
api.create_repo(model_id, exist_ok=True, repo_type="model")
api.upload_file(
    path_or_fileobj=f"{quantized_model}/{quantized_gguf_model}",
    path_in_repo=quantized_gguf_model,
    repo_id=model_id,
)

# install llama-cpp-python
os.system("pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122")

# load and use the quantized model
model_path = f"{quantized_model}/{quantized_gguf_model}"
model = Llama(model_path=model_path, n_gpu_layers=-1)

generation_kwargs = {
    "max_tokens": 300,
    "echo": False,
    "top_k": 1
}

prompt = "if x+2a=0, what is a and x?"
response = model(prompt, **generation_kwargs)
print(response['choices'][0]['text'])
