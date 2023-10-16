#from src.helpers.upload_vectordb import process_data
from src.helpers.inference import inference
# process_data("pdf_data/ED-Time-Reporting-&-Work-Time----Austria-071023-193559.pdf")
inference("Where to contact for question of Financial Force on Time Reporting?", local=True)
