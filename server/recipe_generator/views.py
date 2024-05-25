from rest_framework import views, status
from rest_framework.response import Response
from .serializers import AIRequestSerializer, AIResponseSerializer
from transformers import FlaxAutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH, use_fast=True)
model = FlaxAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

prefix = "items: "
generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95
}

special_tokens = tokenizer.all_special_tokens
tokens_map = {
    "<sep>": "--",
    "<section>": "\n"
}

def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")
    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]

    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)
        for k, v in tokens_map.items():
            text = text.replace(k, v)
        new_texts.append(text)
    return new_texts

def generation_function(texts):
    _inputs = texts if isinstance(texts, list) else [texts]
    inputs = [prefix + inp for inp in _inputs]
    inputs = tokenizer(
        inputs,
        max_length=256,
        padding="max_length",
        truncation=True,
        return_tensors="jax"
    )

    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    output_ids = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        **generation_kwargs
    )
    generated = output_ids.sequences
    generated_recipe = target_postprocessing(
        tokenizer.batch_decode(generated, skip_special_tokens=False),
        special_tokens
    )
    return generated_recipe

class AIView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = AIRequestSerializer(data=request.data)
        if serializer.is_valid():
            input_text = serializer.validated_data["input_text"]
            output_text = generation_function(input_text)
            response_data = AIResponseSerializer({"output_text": output_text}).data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class RecipeGenerationView(views.APIView):
    def post(self, request, *args, **kwargs):
        items = request.data.get('items', [])  # Assuming 'items' is the key for the list of items
        generated = generation_function(items)
        
        # Modify the response structure to match the serializer's expectations
        response_data = {"output_text": generated}  # Use "output_text" as the key
        
        return Response(response_data, status=status.HTTP_200_OK)
