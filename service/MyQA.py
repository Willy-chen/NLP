import torch

max_seq_length = 512

question_answering_model = torch.hub.load('huggingface/pytorch-transformers', 'modelForQuestionAnswering', 'bert-large-uncased-whole-word-masking-finetuned-squad')


# Loading from a TF checkpoint file instead of a PyTorch model (slower)
# config = AutoConfig.from_json_file('./tf_model/bert_tf_model_config.json')

# question_answering_model = torch.hub.load('huggingface/pytorch-transformers', 'modelForQuestionAnswering', './tf_model/bert_tf_checkpoint.ckpt.index', from_tf=True, config=config)

# question_answering_model = torch.hub.load('huggingface/pytorch-transformers', 'modelForQuestionAnswering', './tf_model/bert_tf_checkpoint.ckpt.index')
question_answering_tokenizer = torch.hub.load('huggingface/pytorch-transformers', 'tokenizer', 'bert-base-uncased')

# The format is paragraph first and then question
# text_1 = "In May 1983, she married Nikos Karvelas, a composer, with whom she collaborated in 1975 and in November she gave birth to her daughter Sofia. After their marriage, she started a close collaboration with Karvelas. Since 1975, all her releases have become gold or platinum and have included songs by Karvelas. In 1986, she participated at the Cypriot National Final for Eurovision Song Contest with the song Thelo Na Gino Star (\"I Want To Be A Star\"), taking second place. This song is still unreleased up to date. In 1984, Vissi left her record company EMI Greece and signed with CBS Records Greece, which later became Sony Music Greece, a collaboration that lasted until 2013. In March 1984, she released Na 'Hes Kardia (\"If You Had a Heart\"). The album was certified gold. The following year her seventh album Kati Simveni (\"Something Is Happening\") was released which included one of her most famous songs, titled \"Dodeka\" [\"Twelve (O'Clock)\"] and reached gold status selling 80.000 units. In 1986 I Epomeni Kinisi (\"The Next Move\") was released. The album included the hit Pragmata (\"Things\") and went platinum, becoming the best selling record of the year. In February 1988 she released her ninth album Tora (\"Now\") and in December the album Empnefsi! (\"Inspiration!\") which went gold. In 1988, she made her debut as a radio producer on ANT1 Radio. Her radio program was titled after one of her songs Ta Koritsia Einai Atakta (\"Girls Are Naughty\") and was aired every weekend. In the same year, she participated with the song Klaio (\"I'm Crying\") at the Greek National Final for Eurovision Song Contest, finishing third. In 1989, she released the highly successful studio album Fotia (Fire), being one of the first albums to feature western sounds. The lead single Pseftika (\"Fake\") became a big hit and the album reached platinum status, selling 180.000 copies and becoming the second best selling record of 1990. She performed at \"Diogenis Palace\" in that same year, Athens's biggest nightclub/music hall at the time."
# text_2 = "what happened in 1983?"
# indexed_tokens = question_answering_tokenizer.encode(text_1, text_2, add_special_tokens=True)
# # segments_ids = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# # segments_tensors = torch.tensor([segments_ids])
# # print(segments_tensors)
# tokens_tensor = torch.tensor([indexed_tokens])
# segments_tensors = torch.zeros_like(tokens_tensor)
# print(tokens_tensor.size())

# question_answering_model.eval()
# # Predict the start and end positions logits
# with torch.no_grad():
#     out = question_answering_model(tokens_tensor, token_type_ids=segments_tensors)

# # get the highest prediction
# answer = question_answering_tokenizer.decode(indexed_tokens[torch.argmax(out.start_logits):torch.argmax(out.end_logits)+1])
# # assert answer == "puppeteer"

# print(answer)

questions = ['what happened in 1983?', 'did they have any children?','what collaborations did she do with nikos?']
text = "In May 1983, she married Nikos Karvelas, a composer, with whom she collaborated in 1975 and in November she gave birth to her daughter Sofia. After their marriage, she started a close collaboration with Karvelas. Since 1975, all her releases have become gold or platinum and have included songs by Karvelas. In 1986, she participated at the Cypriot National Final for Eurovision Song Contest with the song Thelo Na Gino Star (\"I Want To Be A Star\"), taking second place. This song is still unreleased up to date. In 1984, Vissi left her record company EMI Greece and signed with CBS Records Greece, which later became Sony Music Greece, a collaboration that lasted until 2013. In March 1984, she released Na 'Hes Kardia (\"If You Had a Heart\"). The album was certified gold. The following year her seventh album Kati Simveni (\"Something Is Happening\") was released which included one of her most famous songs, titled \"Dodeka\" [\"Twelve (O'Clock)\"] and reached gold status selling 80.000 units. In 1986 I Epomeni Kinisi (\"The Next Move\") was released. The album included the hit Pragmata (\"Things\") and went platinum, becoming the best selling record of the year. In February 1988 she released her ninth album Tora (\"Now\") and in December the album Empnefsi! (\"Inspiration!\") which went gold. In 1988, she made her debut as a radio producer on ANT1 Radio. Her radio program was titled after one of her songs Ta Koritsia Einai Atakta (\"Girls Are Naughty\") and was aired every weekend. In the same year, she participated with the song Klaio (\"I'm Crying\") at the Greek National Final for Eurovision Song Contest, finishing third. In 1989, she released the highly successful studio album Fotia (Fire), being one of the first albums to feature western sounds. The lead single Pseftika (\"Fake\") became a big hit and the album reached platinum status, selling 180.000 copies and becoming the second best selling record of 1990. She performed at \"Diogenis Palace\" in that same year, Athens's biggest nightclub/music hall at the time."

for question in questions:
    inputs = question_answering_tokenizer.encode_plus(question, 
                                   text, 
                                   add_special_tokens=True, 
                                   max_length=max_seq_length,
                                   truncation=True,
                                   return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    text_tokens = question_answering_tokenizer.convert_ids_to_tokens(input_ids)
    answer_start_scores, answer_end_scores = question_answering_model(**inputs, return_dict=False)

    answer_start = torch.argmax(
        answer_start_scores
    )  # Get the most likely beginning of answer with the argmax of the score
    answer_end = torch.argmax(answer_end_scores) + 1  # Get the most likely end of answer with the argmax of the score

    answer = question_answering_tokenizer.convert_tokens_to_string(question_answering_tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    print(f"Question: {question}")
    print(f"Answer: {answer}\n")

