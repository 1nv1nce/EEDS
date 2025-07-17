from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

#设置原来本地模型的地址
base_model_path = '/root/autodl-tmp/Llama-2-13b-chat-hf'
#设置微调后模型的地址
finetuned_model_path = '/root/autodl-tmp/results/final_checkpoint'
#设置合并后模型的导出地址
save_path = '/root/autodl-tmp/new_model'

tokenizer = AutoTokenizer.from_pretrained(
    base_model_path,
    trust_remote_code=True
)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    torch_dtype=torch.float16,
    device_map='auto'
)
print("load model success")
finetuned_model = PeftModel.from_pretrained(base_model, finetuned_model_path)
print("load adapter success")
model = finetuned_model.merge_and_unload()
print("merge success")

tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)
print("save done.")
