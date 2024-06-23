import sys, os

from llama_cpp import Llama
#from exllamav2 import ExLlamaV2, ExLlamaV2Config, ExLlamaV2Cache, ExLlamaV2Tokenizer, Timer
#from exllamav2.generator import ExLlamaV2DynamicGenerator, ExLlamaV2Sampler



class LlamaCPP():
    def __init__(self, model_dir: str, **kwargs):
        print(f"Loading model: {model_dir}...")
        self.model_dir = model_dir
        self.llm = Llama(
            model_path=self.model_dir,
            n_gpu_layers=-1,
            seed=1234,
            n_ctx=4096,
        )

        defaults = {
            "temperature": 1.0,
            "repeat_penalty": 1.025,
            "min_p": 0.5,
            "top_p": 1.0,
            "top_k": 0,
            "max_tokens": 4096,
        }
        defaults.update(kwargs)
        self.args = defaults

        
    def generate(self, prompt: str, **kwargs):
        llm_args = self.args
        llm_args.update(kwargs)
        print("Prompt: ", prompt)
        print("Args: ", llm_args)
        output = self.llm(
            prompt,
            echo=False,
            **llm_args
        )
        print(f"output: {output}")
        response = output["choices"][0]["text"]

        return response


"""
class ExLlama():
    def __init__(self, model_dir: str, **kwargs):
        print(f"Loading model: {model_dir}...")
        self.model_dir = model_dir
        self.config = ExLlamaV2Config(self.model_dir)
        self.model = ExLlamaV2(self.config)
        self.cache = ExLlamaV2Cache(self.model, max_seq_len = 32768, lazy = True)
        self.model.load_autosplit(self.cache, progress = True)

        print("Loading tokenizer...")
        self.tokenizer = ExLlamaV2Tokenizer(self.config)

        # Initialize the generator with all default parameters
        self.generator = ExLlamaV2DynamicGenerator(
            model = self.model,
            cache = self.cache,
            tokenizer = self.tokenizer,
        )

        defaults = {
            "temperature": 1.0,
            "token_repetition_penalty": 1.025,
            "min_p": 0.5,
            "top_p": 1.0,
            "top_k": 0,
        }
        defaults.update(kwargs)
        self.args = defaults

        self.generator.warmup()



    def generate(self, prompt: str, max_new_tokens: int=250, **kwargs):
        args = self.args.update(kwargs)
        gen_settings = ExLlamaV2Sampler.Settings(**args)
        output = self.generator.generate(prompt = prompt, max_new_tokens = max_new_tokens, gen_settings = gen_settings, add_bos = True)
        print(output)
        return output
  


    def batch_generate(self, prompts: list, max_new_tokens: int=250):
        outputs = self.generator.generate(prompt = prompts, max_new_tokens = max_new_tokens, gen_settings = self.gen_settings, add_bos = True)
        print(outputs)
        return outputs
"""