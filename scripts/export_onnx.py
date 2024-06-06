import os

import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from loguru import logger

def export_onnx():
    device = "cuda"
    model_path = "../models/qhy-0"
    config = XttsConfig()
    config_path = os.path.join(model_path, "config.json")
    checkpoint_dir = model_path
    speaker_file = os.path.join(model_path, 'speakers_xtts.pth')

    # Check for exists
    if not os.path.exists(speaker_file):
        logger.info("No speaker file found")
        speaker_file = None

    config.load_json(str(config_path))

    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, use_deepspeed=False, speaker_file_path=speaker_file,
                               checkpoint_dir=str(checkpoint_dir))
    model.to(device)

    # 为示例输入创建张量
    # 这里的示例输入形状需要与模型期望的输入形状匹配
    text_inputs = torch.ones((1, 15), dtype=torch.long).to(device)
    text_lengths = torch.ones((1,), dtype=torch.long).to(device)
    audio_codes = torch.ones((1, 45), dtype=torch.long).to(device)
    wav_lengths = torch.ones((1,), dtype=torch.long).to(device)
    cond_latents = torch.ones((1, 32, 1024)).to(device)
    return_attentions = False
    return_latent = True

    # 定义输入名称和形状字典
    input_gpt_dict = {
        "text_inputs": text_inputs,
        "text_lengths": text_lengths,
        "audio_codes": audio_codes,
        "wav_lengths": wav_lengths,
        "cond_latents": cond_latents,
        "return_attentions": return_attentions,
        "return_latent": return_latent
    }

    # 导出模型为ONNX格式
    torch.onnx.export(
        model.gpt,
        input_gpt_dict,  # 输入字典
        os.path.join(model_path, "gpt_model.onnx"),  # 导出文件路径
        input_names=["text_inputs", "text_lengths", "audio_codes", "wav_lengths", "cond_latents"],  # 输入张量的名称
        output_names=["output"],  # 输出张量的名称
        dynamic_axes={
            "text_inputs": {0: "batch", 1: "sequence"},
            "audio_codes": {0: "batch", 1: "sequence"},
            "cond_latents": {0: "batch"}
        },  # 动态轴
        verbose=True,  # 输出详细信息
    )

if __name__ == "__main__":
    export_onnx()
    # test_inference()