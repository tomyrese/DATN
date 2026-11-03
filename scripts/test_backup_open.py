import sys, os
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

word = None
try:
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    abs_path = os.path.abspath('PL2_Robot_TuHanh_Pi44_backup_before_hyperlink.docx')
    print('Testing backup:', abs_path)
    doc = word.Documents.Open(abs_path, False, True, False)
    print("SUCCESS: Word opened backup! Paragraphs:", doc.Paragraphs.Count)
    doc.Close(False)
except Exception as e:
    print("Error:", e)
finally:
    if word:
        try:
            word.Quit(False)
        except:
            pass

