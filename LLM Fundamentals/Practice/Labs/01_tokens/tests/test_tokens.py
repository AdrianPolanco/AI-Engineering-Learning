from tokens.tokenizer import Tokenizer
from pytest import fixture

# Declarando una fixture que devolvera una instancia de Tokenizer 
# que vivira durante toda la sesion de pruebas en vez de devolver una nueva
# en cada caso de prueba
@fixture(scope="session")
def tokenizer():
    return Tokenizer("gpt-5")

# Declarando una fixture que devolvera un str
@fixture
def prompt():
    return "Hola, soy Adrian"

# Declarando una fixture que devolvera una list[int]
@fixture
def tokens():
    return [49864, 11, 28957, 78304]

# Pytest inspecciona las firmas de las fixture (nombre y tipo)
# y los inyecta a las funciones, por tanto, los parametros que se reciben
# deben llamarse igual que la funcion de la fixture
# por eso tokenizer, prompt y tokens
def test_tokenize(tokenizer: Tokenizer, prompt: str, tokens: list[int]):
    encoded_tokens = tokenizer.tokenize(prompt)

    assert encoded_tokens == tokens

# Todas las funciones que sirven como casos de prueba deben empezar por el
# prefijo test_ para que pytest pueda identificarlas y ejecutarlas
def test_detokenize(tokenizer: Tokenizer, prompt: str, tokens: list[int]):
    decoded_prompt = tokenizer.detokenize(tokens)

    assert prompt == decoded_prompt

def test_input_prices(tokenizer: Tokenizer):
        tokens = list(range(1,1000001))
        price = tokenizer.__calculate_price(tokens, tokenizer.PRICE_PER_MILLION_OF_INPUT_TOKENS)
        assert price == 10

def test_output_prices(tokenizer: Tokenizer):
     tokens = list(range(1,1000001))
     price = tokenizer.__calculate_price(tokens, tokenizer.PRICE_PER_MILLION_OF_OUTPUT_TOKENS)
     assert price == 20