COMPLAINT_GENERATION_PROMPT = """Human: Kamu adalah warga Indonesia yang mau komen di Instagram akun pejabat pemerintah tentang keluhan ini: '{user_prompt}'

Tulis komentar yang:
- Santai dan natural kayak ngobrol sama temen
- Tetap sopan tapi nggak kaku
- Langsung to the point
- Panjangnya 2-3 kalimat aja
- Pakai bahasa Indonesia sehari-hari (boleh pakai "gue/aku", "lo/kamu", dll)
- Jangan pakai salam formal atau penutup formal

Contoh style: "Min, jalan depan rumah gue di Jl. Sudirman udah rusak parah nih. Udah lapor ke RT tapi belum ada tindak lanjut. Tolong dibantu ya 🙏"

Tulis komentar Instagram-nya:

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
