import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, VitsTokenizer, VitsModel
from huggingface_hub import login
import json
from pix2text import Pix2Text
from dotenv import load_dotenv
import os

load_dotenv()
HF_KEY= os.getenv("HUGGING_FACE")

def load_config():
    with open('config.json') as f:
        return json.load(f)

def load_models():
    config = load_config()
    
    # get model configuration
    pix2text_model_name = config['pix2text']['model_name']
    llama_model_name = config['llama']['model_name']
    vits_model_name = config['vits']['model_name']
    llama_quantization_config = config['llama']['quantization_config']

    login(token=HF_KEY)

    # load the Pix2Text model
    p2t = Pix2Text.from_config(pix2text_model_name)

    # load Llama 3.1 8B
    tokenizer = AutoTokenizer.from_pretrained(
        llama_model_name,
        token=HF_KEY
    )

    # quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=llama_quantization_config['load_in_4bit'],
        bnb_4bit_use_double_quant=llama_quantization_config['bnb_4bit_use_double_quant'],
        bnb_4bit_quant_type=llama_quantization_config['bnb_4bit_quant_type'],
        bnb_4bit_compute_dtype=torch.float16,
    )

    # define model
    model = AutoModelForCausalLM.from_pretrained(
        llama_model_name,
        quantization_config=bnb_config,
        token=HF_KEY,
        device_map='auto'
    )
    
    tokenizer_au = VitsTokenizer.from_pretrained(vits_model_name)
    model_au = VitsModel.from_pretrained(vits_model_name)

    return p2t, tokenizer, model, tokenizer_au, model_au
