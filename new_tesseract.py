import pytesseract
from PIL import Image


def distinguish_tesseract(img):
    res = pytesseract.image_to_string(img, lang="chi_sim")
    return str(res)


if __name__ == '__main__':
    image = Image.open("number_plate/gray.jpg")
    text = pytesseract.image_to_string(image, lang="chi_sim")
    print(text)

