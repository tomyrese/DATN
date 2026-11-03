import sys, os
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

word = None
try:
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    abs_path = os.path.abspath('PL2_Robot_TuHanh_Pi44_user_original.docx')
    print('Testing original:', abs_path)
    doc = word.Documents.Open(abs_path, False, True, False)
    print("SUCCESS: Word opened user_original! Paragraphs:", doc.Paragraphs.Count)
    doc.Close(False)
except Exception as e:
    print("Error:", e)
finally:
    if word:
        try:
            word.Quit(False)
        except:
            pass

