from fastapi import Body, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import BertConfig, BertForSequenceClassification, BertTokenizerFast, default_data_collator
from torch.utils.data import DataLoader
from accelerate import Accelerator
from fastapi.responses import JSONResponse
import json
import pickle
import torch

import schemas

# ============================================================================

model_path = './Taipei_FAQ_model/'

with open(model_path + 'label_encoder.pkl', 'rb') as reader:
    le = pickle.load(reader)

tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
config = BertConfig.from_pretrained(model_path + 'config.json')
model = BertForSequenceClassification.from_pretrained(model_path + 'pytorch_model.bin', config=config)

with open('./data/Taipei_FAQ.json', 'r') as f:
    taipei_data = json.load(f)

# ============================================================================
    
class Dataset(torch.utils.data.Dataset):
  def __init__(self, encodings):
    self.encodings = encodings

  def __getitem__(self, idx):
    return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

  def __len__(self):
    return len(self.encodings.input_ids)

def FAQ_model(model, question):
    input_encodings = tokenizer([question], truncation=True, padding=True)
    input_dataset = Dataset(input_encodings)

    data_collator = default_data_collator
    input_dataloader = DataLoader(input_dataset, collate_fn=data_collator, batch_size=1)

    accelerator = Accelerator()
    model, input_dataloader = accelerator.prepare(model, input_dataloader)

    for batch in input_dataloader:
        outputs = model(**batch)
        predicted = outputs.logits.argmax(dim=-1)
    return predicted

# ============================================================================

app = FastAPI()

# mount assets, html file
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search")
async def search_item(search_input: schemas.SearchRequest):
    search_query = search_input.query

    num_answer = FAQ_model(model, search_query)
    original_answer = le.inverse_transform([num_answer.item()])
    answer = original_answer[0].strip("[]'")

    unit_info = {}

    if answer in taipei_data:
       unit_info = {
          'unit': answer,
          'address': taipei_data[answer]['地址'],
          'link': taipei_data[answer]['網址'],
          'phone': taipei_data[answer]['電話'],
          'fax': taipei_data[answer]['傳真'],
          'service': taipei_data[answer]['服務時間']
       }

       print(f'Unit information: {unit_info}')

    return JSONResponse(content={"unit_info": unit_info})
