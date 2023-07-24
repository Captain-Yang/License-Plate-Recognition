from cnocr import CnOcr
ocr = CnOcr()
# cand_alphabet = "NUMBERS"
# CnOcr.set_cand_alphabet(ocr,"NUMBERS")
path = "split_img/" + "0" + ".jpg"
res = ocr.ocr_for_single_line(path)
print("Predicted Chars:", res)