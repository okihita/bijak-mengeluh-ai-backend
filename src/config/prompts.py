COMPLAINT_GENERATION_PROMPT_FORMAL = """Human: Kamu adalah warga Indonesia yang mau komen di Instagram akun pejabat pemerintah tentang keluhan ini: '{user_prompt}'

Tulis komentar yang:
- Formal dan sopan
- Profesional tapi tetap ramah
- Langsung to the point
- Panjangnya 2-3 kalimat
- Pakai bahasa Indonesia yang baik dan benar
- Jangan pakai salam formal atau penutup formal

Contoh style: "Mohon perhatiannya untuk jalan di Jl. Sudirman yang kondisinya rusak parah. Sudah dilaporkan ke RT namun belum ada tindak lanjut. Terima kasih atas perhatiannya 🙏"

Tulis komentar Instagram-nya:

A:"""

COMPLAINT_GENERATION_PROMPT_FUNNY = """Human: Kamu adalah warga Indonesia yang mau komen di Instagram akun pejabat pemerintah tentang keluhan ini: '{user_prompt}'

Tulis komentar yang:
- Lucu dan menghibur tapi tetap sopan
- Pakai humor ringan dan sedikit sarkasme
- Langsung to the point
- Panjangnya 2-3 kalimat
- Pakai bahasa Indonesia sehari-hari yang santai
- Boleh pakai emoji yang relevan

Contoh style: "Min, jalan depan rumah gue kayak medan perang nih 😅 Udah 3 bulan nunggu diperbaiki, apa lagi nunggu jadi danau dulu? Tolong dibantu dong Min, kasian motor gue 🙏"

Tulis komentar Instagram-nya:

A:"""

COMPLAINT_GENERATION_PROMPT_ANGRY = """Human: Kamu adalah warga Indonesia yang mau komen di Instagram akun pejabat pemerintah tentang keluhan ini: '{user_prompt}'

Tulis komentar yang:
- Tegas dan menunjukkan kekesalan
- Borderline insulting tapi masih dalam batas wajar
- Langsung to the point dan menuntut
- Panjangnya 2-3 kalimat
- Pakai bahasa Indonesia yang kuat dan emosional
- Tetap hindari kata-kata kasar atau vulgar

Contoh style: "Serius nih Min, jalan depan rumah gue udah kayak kubangan kerbau! Udah 3 bulan lapor tapi cuma dijawab 'ditindaklanjuti'. Kapan sih kerja beneran? Pajak gue bayar buat apa? 😤"

Tulis komentar Instagram-nya:

A:"""

# Keep the original as default
COMPLAINT_GENERATION_PROMPT = COMPLAINT_GENERATION_PROMPT_FORMAL

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
