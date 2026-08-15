import tiktoken

class Tokenizer:
    def __init__(self, model_name: str) -> None:
        self.enc = tiktoken.encoding_for_model(model_name)
        self.PRICE_PER_MILLION_OF_INPUT_TOKENS = 10.0
        self.PRICE_PER_MILLION_OF_OUTPUT_TOKENS = 20.0

    def tokenize(self, prompt: str) -> list[int]:
        tokens = self.enc.encode(prompt)
        print(tokens)
        price = self.__calculate_price(tokens, self.PRICE_PER_MILLION_OF_INPUT_TOKENS)
        print(f"You will pay {price}$ for {len(tokens)} input tokens produced")
        return tokens

    def detokenize(self, tokens: list[int]) -> str:
        price = self.__calculate_price(tokens, self.PRICE_PER_MILLION_OF_OUTPUT_TOKENS)
        original_prompt = self.enc.decode(tokens)
        print(original_prompt)
        print(f"You will pay {price}$ for {len(tokens)} output tokens produced.")
        return original_prompt

    def __calculate_price(self, tokens: list[int], reference_price: float) -> float:
        return len(tokens) * reference_price / 1000000

    