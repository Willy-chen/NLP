import torch
import requests, urllib
from requests_html import HTML
from requests_html  import HTMLSession

# import wikipedia as wiki
from transformers import AutoModelForQuestionAnswering, BertTokenizer, BertModel, AutoTokenizer, pipeline
from collections import OrderedDict
from bs4 import BeautifulSoup as bs
from pprint import pprint


def parse_results(response):
    
    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".IsZvec"
    css_identifier_diet = ".hgKElc"
    # css_identifier_similar = ".Wt5Tfe span"
    css_identifier_ecom = ".PZPZlf span"
    css_identifier_exchange = ".b1hJbf"
    css_identifier_calculate = ".vUGUtc, .qv3Wpe"
    css_identifier_weather = ".nawv0d"
    css_identifier_support = ".kno-rdesc span"
    css_identifier_internet_diet = ".kp-blk"

    results = response.html.find(css_identifier_result)

    output = []
    diet = response.html.find(css_identifier_diet, first=True)
    # similar = response.html.find(css_identifier_similar, first=False)
    ecom = response.html.find(css_identifier_ecom, first=False)
    exchange = response.html.find(css_identifier_exchange, first=True)
    calculate = response.html.find(css_identifier_calculate, first=False)
    weather = response.html.find(css_identifier_weather, first=False)
    support = response.html.find(css_identifier_support, first=False)
    idiet = response.html.find(css_identifier_internet_diet, first=True)

    if diet:
        output.append({'diet':diet.text})
    else:
        output.append({'diet':None})

    # if similar:
    #     output.append({'similar':""})
    #     print(similar)
    #     for it in similar:
    #         if 'class' in it.attrs and it.attrs['class'][0] == 'hgKElc':
    #             print(it.attrs)
    #             output[-1]['similar'] += it.html + ' '
    # else:
    #     output.append({'similar':None})

    if ecom:
        output.append({'ecom':""})
        for it in ecom:
            # if 'class' in it.attrs:
            #     print( it.attrs['class'][0])
            #     print(it.attrs['class'][0] == 'a4vfUd')
            # if 'class' in it.attrs and it.attrs['class'][0]=='jBBUv':
            #     print(it.attrs['class'])
            if 'jscontroller' in it.attrs and it.attrs['jscontroller']=='B82lxb':
                output[-1]['ecom']+=it.text+' '
            if 'jsname' in it.attrs and it.attrs['jsname']=='qRSVye':
                output[-1]['ecom']+=it.text+' '
            if 'class' in it.attrs and it.attrs['class'][0]=='jBBUv':
                output[-1]['ecom']+=it.attrs['aria-label']+' '
    else:
        output.append({'ecom':None})

    if exchange:
        output.append({'exchange':exchange.text.replace('\n',' ')})
    else:
        output.append({'exchange':None})

    if calculate:
        output.append({'calculate':""})
        for it in calculate:
            output[-1]['calculate'] += it.text.replace('\n',' ')+' '
    else:
        output.append({'calculate':None})

    if weather:
        output.append({'weather':""})
        output[-1]['weather'] += weather[0].find(".VQF4g")[0].text.replace('\n', ' ') + ' '
        output[-1]['weather'] += weather[0].find(".wtsRwe")[0].text.replace('\n', ' ')[:-5]
        for it in weather[0].find('span'):
            # if 'id' in it.attrs:
            #     print(it.attrs['id'])
            if 'id' in it.attrs and it.attrs['id'] == 'wob_tm':
                output[-1]['weather'] += f' {it.text}°C'
            if 'id' in it.attrs and it.attrs['id'] == 'wob_ttm':
                output[-1]['weather'] += f' {it.text}°F'
    else:
        output.append({'weather':None})

    if support:
        output.append({'support':[]})
        # print(support[0].find(".kno-rdesc")[0].text)
        for it in support:
            tmp = it.find('a')
            if tmp:
                for iit in tmp:
                    output[-1]['support'].append(f'[{it.text}]({str(iit.absolute_links.pop())})')                
            else:
                output[-1]['support'].append(it.text)

    else:
        output.append({'support':None})

    if idiet:
        output.append({'internet_diet':idiet.text})
    else:
        output.append({'internet_diet':None})

    for result in results:

        item = {
            'title': result.find(css_identifier_title, first=True).text,
            'link': result.find(css_identifier_link, first=True).attrs['href'],
            'text': result.find(css_identifier_text, first=True).text
        }
        
        output.append(item)
        
    return output


model_name = "peggyhuang/bert-base-uncased-coqa"

# a) Get predictions
# nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
# QA_input = {
#     'question': 'Why is model conversion important?',
#     'context': 'The option to convert models between FARM and transformers gives freedom to the user and let people easily switch between frameworks.'
# }
# res = nlp(QA_input)
# pprint(res)

# b) Load model & tokenizer
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = BertModel.from_pretrained(model_name)

question = 'when did the first finalfantasy release?'

# get passages from wiki
# results = wiki.search(question)
# print("Wikipedia search results for our question:\n")
# pprint(results)

# page = wiki.page(results[0])
# text = page.content
# print(f"\nThe {results[0]} Wikipedia article contains {len(text)} characters.")


text = ""

query = urllib.parse.quote_plus(question)
url = f"https://www.google.com/search?q={query}"
headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')}
response = None

try:
    session = HTMLSession()
    response = session.get(url)
    
except requests.exceptions.RequestException as e:
    print(e)

results = parse_results(response)

flag = True
for result in results:
    if list(result.keys())[0] != 'title' and list(result.items())[0][1] != None and list(result.items())[0][1] != '':
        text += ( urllib.parse.unquote(str(list(result.items())[0][1])+'\n'))
        flag = False
        break

if flag:
    for result in results:
        if list(result.keys())[0] == 'title':
            text += ( urllib.parse.unquote(str(result['text'])+'\n'))

print(text)

# 1. TOKENIZE THE INPUT
# note: if you don't include return_tensors='pt' you'll get a list of lists which is easier for 
# exploration but you cannot feed that into a model. 
inputs = tokenizer.encode_plus(question, text, return_tensors="pt", return_token_type_ids=True) 
print(f"This translates into {len(inputs['input_ids'][0])} tokens.")
# print(inputs)
# identify question tokens (token_type_ids = 0)
qmask = inputs['token_type_ids'].lt(1)
qt = torch.masked_select(inputs['input_ids'], qmask)
print(f"The question consists of {qt.size()[0]} tokens.")

chunk_size = model.config.max_position_embeddings - qt.size()[0] - 1 # the "-1" accounts for
# having to add a [SEP] token to the end of each chunk
print(f"Each chunk will contain {chunk_size - 2} tokens of the Wikipedia article.")

inputs = tokenizer.encode_plus(question, text, return_tensors="pt")
# create a dict of dicts; each sub-dict mimics the structure of pre-chunked model input
chunked_input = OrderedDict()
for k,v in inputs.items():
    q = torch.masked_select(v, qmask)
    c = torch.masked_select(v, ~qmask)
    chunks = torch.split(c, chunk_size)

    for i, chunk in enumerate(chunks):
        if i not in chunked_input:
            chunked_input[i] = {}

        thing = torch.cat((q, chunk))
        if i != len(chunks)-1:
            if k == 'input_ids':
                thing = torch.cat((thing, torch.tensor([102])))
            else:
                thing = torch.cat((thing, torch.tensor([1])))

        chunked_input[i][k] = torch.unsqueeze(thing, dim=0)

# 2. OBTAIN MODEL SCORES
# the AutoModelForQuestionAnswering class includes a span predictor on top of the model. 
# the model returns answer start and end scores for each word in the text
# answer_start_scores, answer_end_scores = model(**inputs, return_dict=False)
# answer_start = torch.argmax(answer_start_scores)  # get the most likely beginning of answer with the argmax of the score
# answer_end = torch.argmax(answer_end_scores) + 1  # get the most likely end of answer with the argmax of the score

# 3. GET THE ANSWER SPAN
# once we have the most likely start and end tokens, we grab all the tokens between them
# and convert tokens back to words!
# ans = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

def convert_ids_to_string(tokenizer, input_ids):
    return tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids))

answer = ''

# now we iterate over our chunks, looking for the best answer from each chunk
for _, chunk in chunked_input.items():
    answer_start_scores, answer_end_scores = model(**chunk, return_dict=False)

    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1

    ans = convert_ids_to_string(tokenizer, chunk['input_ids'][0][answer_start:answer_end])
    
    # print(ans)

    # if the ans == [CLS] then the model did not find a real answer in this chunk
    if ans != '[CLS]' and ans != '':
        answer += ans + " / "
        
print(answer)