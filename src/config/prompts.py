COMPLAINT_GENERATION_PROMPT = """Human: Based on the following user complaint, please write a clear, polite, and detailed formal complaint suitable for submission to a government agency in Indonesia. The user's input is: '{user_prompt}'

A:"""

RATIONALE_GENERATION_PROMPT = """Human: Here is a user's complaint:
<complaint>
{user_prompt}
</complaint>

And here is the top-matched government ministry and its function:
<ministry>
Nama: {ministry_name}
Fungsi: {ministry_desc}
</ministry>

Your task is to write a brief, clear rationale (in 1-2 sentences) explaining *why* this ministry is the correct one to handle this specific complaint.
Directly connect key phrases from the complaint to the ministry's function.
Example: "Kementerian PUPR disarankan karena keluhan Anda tentang 'jalan rusak' dan 'jembatan' terkait langsung dengan tanggung jawab mereka atas 'infrastruktur jalan' dan 'jembatan'."

Write only the rationale.

A:"""
