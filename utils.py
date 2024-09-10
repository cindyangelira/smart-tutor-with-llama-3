import io
import torch
import torchaudio
from models import load_models

# load models
p2t, tokenizer, model, tokenizer_au, model_au = load_models()

def process_image(image):
    math = p2t.recognize_text_formula(image)
    return math

def waveform_to_bytes(waveform, sample_rate=22050):
    waveform = waveform.squeeze().cpu()
    buf = io.BytesIO()
    torchaudio.save(buf, waveform.unsqueeze(0), sample_rate, format="wav")
    buf.seek(0)
    return buf.read()

def generate_solution(math, tokenizer, model):
    messages = [
        {"role": "system", "content": f'"""{math}"""'},
        {"role": "user", "content": "You are an AI that helps students solve problems. Please provide a step-by-step solution in LaTeX format. If the question is not programming related, don't respond with code in your answer. Ensure the response ends with a complete sentence and final answer. Write inline formulas using the $latex code$ format."},
    ]

    prompt = tokenizer.encode(
        f"{messages[0]['content']} {messages[1]['content']}",
        return_tensors='pt'
    ).to(model.device)

    outputs = model.generate(
        input_ids=prompt,
        max_new_tokens=512,  # limit the number of output tokens to 512
        eos_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.2
    )

    output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    prompt_marker = 'Write inline formulas using the $latex code$ format.'
    if prompt_marker in output:
        output = output.split(prompt_marker, 1)[-1].strip()

    output = output.rsplit('.', 1)[0] + '.' if output else ''
    
    return output

def text_to_speech(text, tokenizer_au, model_au):
    inputs = tokenizer_au(text, return_tensors="pt")
    torch.manual_seed(555)  # make deterministic

    with torch.no_grad():
        outputs = model_au(**inputs)
    
    audio_bytes = waveform_to_bytes(outputs.waveform)
    return audio_bytes
