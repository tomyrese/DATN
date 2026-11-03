import sys, os
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

def test_file(path):
    word = None
    try:
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0  # wdAlertsNone
        abs_path = os.path.abspath(path)
        doc = word.Documents.Open(abs_path, False, True, False)
        print(f"SUCCESS: Word opened {path}! Paragraphs: {doc.Paragraphs.Count}")
        doc.Close(False)
        return True
    except Exception as e:
        print(f"FAILED to open {path}: {e}")
        return False
    finally:
        if word:
            try:
                word.Quit(False)
            except:
                pass

test_file('PL2_Robot_TuHanh_Pi44_backup_before_hyperlink.docx')
test_file('PL2_Robot_TuHanh_Pi44.docx')

