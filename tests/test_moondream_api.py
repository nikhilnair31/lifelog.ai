from gradio_client import Client

client = Client("https://niknair31-moondream1.hf.space/--replicas/frktd/")
result = client.predict(
    r'data\photos\2024-02-16-11-33-54.jpeg',	# filepath  in 'Upload or Drag an Image' Image component
    "Describe the image",	# str  in 'Question' Textbox component
    api_name="/answer_question"
)
print(result)